import pytest
from app.models import Transaction
from datetime import date

def test_transaction_persistence(db, test_user):
    # Insert transaction
    tx = Transaction(
        transaction_id="tx_12345",
        user_id=test_user.id,
        event_type="expense",
        description="Coffee",
        category="Food & Dining",
        direction="OUTFLOW",
        amount=5.50,
        currency="USD",
        event_date=date.today(),
        status="COMPLETED",
        flexibility="variable"
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    
    # Query transaction
    saved_tx = db.query(Transaction).filter(Transaction.transaction_id == "tx_12345").first()
    assert saved_tx is not None
    assert saved_tx.amount == 5.50
    assert saved_tx.user_id == test_user.id

def test_user_specific_queries(db, test_user):
    # Ensure querying for another user does not return this transaction
    transactions = db.query(Transaction).filter(Transaction.user_id == "other_user_id").all()
    assert len(transactions) == 0
