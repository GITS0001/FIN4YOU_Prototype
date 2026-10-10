from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import PlaidItem, Transaction, User
from app.auth import get_current_user
from app.services.plaid_service import create_link_token, exchange_public_token, sync_transactions
from datetime import datetime
from datetime import datetime, date

router = APIRouter()

def map_plaid_transactions_to_db(added, modified, removed, user_id: int, db: Session):
    for t in added:
        amount = t.get('amount', 0)
        direction = 'OUTFLOW' if amount > 0 else 'INFLOW'
        event_type = 'Expense' if amount > 0 else 'Income'

        # Plaid returns dates as YYYY-MM-DD string
        t_date = datetime.strptime(t['date'], '%Y-%m-%d').date() if t.get('date') else date.today()

        db_t = Transaction(
            transaction_id=t['transaction_id'],
            user_id=user_id,
            event_type=event_type,
            description=t.get('name', 'Unknown Transaction'),
            category=t['category'][0] if t.get('category') else 'Other',
            direction=direction,
            amount=abs(amount),
            currency=t.get('iso_currency_code', 'USD'),
            event_date=t_date,
            status='PENDING' if t.get('pending') else 'SETTLED',
            flexibility='FLEXIBLE'
        )
        db.add(db_t)

    for t in modified:
        db_t = db.query(Transaction).filter(Transaction.transaction_id == t['transaction_id']).first()
        if db_t:
            amount = t.get('amount', 0)
            db_t.amount = abs(amount)
            db_t.event_type = 'Expense' if amount > 0 else 'Income'
            db_t.direction = 'OUTFLOW' if amount > 0 else 'INFLOW'
            db_t.status = 'PENDING' if t.get('pending') else 'SETTLED'

    for t_rm in removed:
        db.query(Transaction).filter(Transaction.transaction_id == t_rm['transaction_id']).delete()

class PublicTokenRequest(BaseModel):
    public_token: str

@router.post("/link/token/create")
def get_link_token(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        link_token = create_link_token(str(current_user.id))
        return {"link_token": link_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/item/public_token/exchange")
def set_public_token(request: PublicTokenRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        access_token, item_id = exchange_public_token(request.public_token)

        # Save to DB
        new_item = PlaidItem(
            user_id=current_user.id,
            item_id=item_id,
            access_token=access_token
        )
        db.add(new_item)
        db.commit()

        return {"message": "Public token exchanged successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transactions/sync")
def sync_user_transactions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(PlaidItem).filter(PlaidItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="No Plaid connection found for user")

    try:
        added, modified, removed, next_cursor = sync_transactions(item.access_token, item.cursor)

        # Map Plaid transactions to our Transaction model
        map_plaid_transactions_to_db(added, modified, removed, current_user.id, db)

        # Update cursor
        item.cursor = next_cursor
        db.commit()

        return {
            "message": "Transactions synced",
            "added_count": len(added),
            "modified_count": len(modified),
            "removed_count": len(removed)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class WebhookPayload(BaseModel):
    webhook_type: str
    webhook_code: str
    item_id: str
    error: Optional[str] = None
    new_transactions: Optional[int] = None

@router.post("/webhook")
def plaid_webhook(payload: WebhookPayload, db: Session = Depends(get_db)):
    if payload.webhook_type == "TRANSACTIONS" and payload.webhook_code == "SYNC_UPDATES_AVAILABLE":
        item = db.query(PlaidItem).filter(PlaidItem.item_id == payload.item_id).first()
        if not item:
            return {"status": "Item not found"}

        try:
            added, modified, removed, next_cursor = sync_transactions(item.access_token, item.cursor)

            # Map added/modified/removed to the database
            map_plaid_transactions_to_db(added, modified, removed, item.user_id, db)

            item.cursor = next_cursor
            db.commit()
            return {"status": "Sync successful", "added": len(added)}
        except Exception as e:
            return {"status": "Sync failed", "error": str(e)}

    return {"status": "Ignored"}
