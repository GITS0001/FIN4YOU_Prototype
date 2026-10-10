from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, Transaction as DBTransaction
from app.ingestion.parser import StatementParser
from app.ml.categorization import TransactionCategorizer

router = APIRouter()

@router.post("/upload")
async def upload_statement(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint for a user to upload a CSV financial statement.
    Parses the file, runs it through the ML Data Quality Pipeline,
    categorizes using the ML categorization model, and persists the transactions.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = await file.read()

    MAX_FILE_SIZE = 5 * 1024 * 1024 # 5 MB
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")

    # 1. Parse and apply Data Quality Pipeline
    try:
        parser = StatementParser(user_id=str(current_user.id))
        transactions, metrics = parser.parse_csv(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to parse statement. Please ensure it is a valid CSV.")

    if not transactions:
        return {"message": "No valid transactions found in the file", "metrics": metrics}

    # 2. Run through ML Categorizer
    categorizer = TransactionCategorizer()
    predictions = categorizer.predict_batch(transactions)

    # Map predictions back to transactions
    for t, p in zip(transactions, predictions):
        t.category = p.category
        t.ml_confidence = p.confidence
        t.ml_status = p.status
        t.ml_confidence_level = p.confidence_level

    # 3. Persist to DB (Supabase repository + local fallback)
    inserted_count = 0
    supabase_success = False
    try:
        from app.supabase_config import is_supabase_configured
        from app.services.supabase_repository import supabase_repository

        # If Supabase is configured, use official repository with batch deduplication
        if is_supabase_configured():
            try:
                tx_dicts = [t.model_dump() for t in transactions]
                result = supabase_repository.save_transactions(user_id=str(current_user.id), transactions=tx_dicts)
                inserted_count = result["inserted_count"]
                supabase_success = True
            except Exception as e:
                import logging
                logging.getLogger("fin4you.statements").error(f"Supabase transaction write failed: {e}. Falling back to SQLite.")
                supabase_success = False

        # Also maintain local DB session if available (for test fixture compatibility)
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
                if not is_supabase_configured() or not supabase_success:
                    inserted_count = len(new_db_transactions)

    except Exception as e:
        if db is not None:
            db.rollback()
        # Log error safely without exposing sensitive financial values
        import logging
        logging.getLogger("fin4you.statements").error(f"Failed to persist statements: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="An internal error occurred while saving transactions.")

    return {
        "message": f"Successfully ingested {inserted_count} new transactions",
        "total_parsed": len(transactions),
        "data_quality_metrics": metrics
    }
