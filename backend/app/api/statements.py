from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Transaction as DBTransaction
from app.ingestion.parser import StatementParser
from app.ml.categorization import TransactionCategorizer

class ConfirmImportRequest(BaseModel):
    transactions: List[Dict[str, Any]]

router = APIRouter()

@router.post("/parse")
async def parse_statement_preview(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Parses a CSV or PDF statement and returns an Import Preview summary table
    without persisting transactions to the database.
    """
    fn = file.filename.lower()
    if not (fn.endswith('.csv') or fn.endswith('.pdf')):
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a CSV or PDF bank statement.")

    content = await file.read()
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")

    try:
        parser = StatementParser(user_id=str(current_user.id))
        transactions, metrics = parser.parse_file(content, file.filename)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse statement: {str(e)}")

    if not transactions:
        raise HTTPException(status_code=400, detail="No valid transactions found in the file.")

    # Categorize batch
    categorizer = TransactionCategorizer()
    predictions = categorizer.predict_batch(transactions)
    for t, p in zip(transactions, predictions):
        t.category = p.category
        t.ml_confidence = p.confidence
        t.ml_status = p.status
        t.ml_confidence_level = p.confidence_level

    # Calculate duplicate count against existing user transactions
    duplicate_count = 0
    if db is not None:
        existing_ids = {
            tx.transaction_id for tx in db.query(DBTransaction.transaction_id)
                                         .filter(DBTransaction.user_id == current_user.id).all()
        }
        duplicate_count = sum(1 for t in transactions if t.transaction_id in existing_ids)

    # Serialize transactions for preview
    tx_list = [t.model_dump() for t in transactions]

    total_credits = sum(t["amount"] for t in tx_list if t["direction"] == "INFLOW")
    total_debits = sum(t["amount"] for t in tx_list if t["direction"] == "OUTFLOW")
    net_cash_flow = total_credits - total_debits

    sorted_dates = sorted([t["event_date"] for t in tx_list])
    date_range = f"{sorted_dates[0]} to {sorted_dates[-1]}" if sorted_dates else "N/A"

    return {
        "filename": file.filename,
        "file_size_bytes": len(content),
        "total_detected": len(tx_list),
        "valid_count": len(tx_list) - duplicate_count,
        "duplicate_count": duplicate_count,
        "date_range": date_range,
        "total_credits": round(total_credits, 2),
        "total_debits": round(total_debits, 2),
        "net_cash_flow": round(net_cash_flow, 2),
        "metrics": metrics,
        "transactions": tx_list
    }

@router.post("/confirm")
async def confirm_statement_import(
    payload: ConfirmImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Persists reviewed transactions to the database after user confirmation.
    Applies strict deduplication logic.
    """
    if not payload.transactions:
        raise HTTPException(status_code=400, detail="No transactions provided for confirmation.")

    inserted_count = 0
    try:
        from app.supabase_config import is_supabase_configured
        from app.services.supabase_repository import supabase_repository

        if is_supabase_configured():
            result = supabase_repository.save_transactions(user_id=str(current_user.id), transactions=payload.transactions)
            inserted_count = result["inserted_count"]

        if db is not None:
            existing_tx_ids = {
                tx.transaction_id for tx in db.query(DBTransaction.transaction_id)
                                             .filter(DBTransaction.user_id == current_user.id).all()
            }
            new_db_transactions = []
            for t_dict in payload.transactions:
                tx_id = t_dict.get("transaction_id")
                if tx_id not in existing_tx_ids:
                    # Convert event_date string/date
                    ev_date = t_dict["event_date"]
                    if isinstance(ev_date, str):
                        from datetime import datetime
                        ev_date = datetime.strptime(ev_date[:10], "%Y-%m-%d").date()

                    db_tx = DBTransaction(
                        transaction_id=tx_id,
                        user_id=current_user.id,
                        event_type=t_dict.get("event_type", "expense"),
                        description=t_dict.get("description", "Unknown"),
                        category=t_dict.get("category", "Uncategorized"),
                        direction=t_dict.get("direction", "OUTFLOW"),
                        amount=float(t_dict.get("amount", 0.0)),
                        currency=t_dict.get("currency", "INR"),
                        event_date=ev_date,
                        settlement_date=None,
                        status=t_dict.get("status", "COMPLETED"),
                        flexibility=t_dict.get("flexibility", "variable"),
                        ml_confidence=t_dict.get("ml_confidence"),
                        ml_status=t_dict.get("ml_status"),
                        ml_confidence_level=t_dict.get("ml_confidence_level")
                    )
                    new_db_transactions.append(db_tx)
            if new_db_transactions:
                db.add_all(new_db_transactions)
                db.commit()
                if not is_supabase_configured():
                    inserted_count = len(new_db_transactions)

    except Exception as e:
        if db is not None:
            db.rollback()
        import logging
        logging.getLogger("fin4you.statements").error(f"Failed to save confirmed transactions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save transactions to database.")

    return {
        "success": True,
        "message": f"Successfully imported {inserted_count} transactions to your ledger.",
        "inserted_count": inserted_count
    }

@router.post("/upload")
async def upload_statement(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Direct upload & ingest endpoint supporting CSV and PDF files.
    """
    fn = file.filename.lower()
    if not (fn.endswith('.csv') or fn.endswith('.pdf')):
        raise HTTPException(status_code=400, detail="Only CSV and PDF bank statement files are supported.")

    content = await file.read()
    MAX_FILE_SIZE = 10 * 1024 * 1024 # 10 MB
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")

    # 1. Parse file
    try:
        parser = StatementParser(user_id=str(current_user.id))
        transactions, metrics = parser.parse_file(content, file.filename)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse statement: {str(e)}")

    if not transactions:
        return {"message": "No valid transactions found in the file", "metrics": metrics}

    # 2. Run through ML Categorizer
    categorizer = TransactionCategorizer()
    predictions = categorizer.predict_batch(transactions)
    for t, p in zip(transactions, predictions):
        t.category = p.category
        t.ml_confidence = p.confidence
        t.ml_status = p.status
        t.ml_confidence_level = p.confidence_level

    # 3. Persist to DB
    inserted_count = 0
    try:
        from app.supabase_config import is_supabase_configured
        from app.services.supabase_repository import supabase_repository

        if is_supabase_configured():
            tx_dicts = [t.model_dump() for t in transactions]
            result = supabase_repository.save_transactions(user_id=str(current_user.id), transactions=tx_dicts)
            inserted_count = result["inserted_count"]

        if db is not None:
            existing_tx_ids = {
                tx.transaction_id for tx in db.query(DBTransaction.transaction_id)
                                             .filter(DBTransaction.user_id == current_user.id).all()
            }
            new_db_transactions = []
            for t in transactions:
                if t.transaction_id not in existing_tx_ids:
                    db_tx = DBTransaction(
                        transaction_id=t.transaction_id,
                        user_id=current_user.id,
                        event_type=t.event_type,
                        description=t.description,
                        category=t.category,
                        direction=t.direction,
                        amount=t.amount,
                        currency=t.currency,
                        event_date=t.event_date,
                        settlement_date=t.settlement_date,
                        status=t.status,
                        flexibility=t.flexibility,
                        ml_confidence=t.ml_confidence,
                        ml_status=t.ml_status,
                        ml_confidence_level=t.ml_confidence_level
                    )
                    new_db_transactions.append(db_tx)
            if new_db_transactions:
                db.add_all(new_db_transactions)
                db.commit()
                if not is_supabase_configured():
                    inserted_count = len(new_db_transactions)

    except Exception as e:
        if db is not None:
            db.rollback()
        import logging
        logging.getLogger("fin4you.statements").error(f"Failed to persist statements: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="An internal error occurred while saving transactions.")

    return {
        "message": f"Successfully ingested {inserted_count} new transactions",
        "total_parsed": len(transactions),
        "data_quality_metrics": metrics
    }
