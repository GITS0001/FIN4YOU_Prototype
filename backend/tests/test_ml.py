import pytest
from app.ml.categorization import TransactionCategorizer
from app.schemas.financial import Transaction
from datetime import date

def test_model_initialization():
    categorizer = TransactionCategorizer()
    assert hasattr(categorizer, "model")

def test_valid_categorization():
    categorizer = TransactionCategorizer()
    tx = Transaction(
        transaction_id="tx_test",
        user_id="user1",
        event_type="expense",
        description="STARBUCKS STORE",
        category="Uncategorized",
        direction="debit",
        amount=4.50,
        currency="USD",
        event_date=date.today(),
        status="COMPLETED",
        flexibility="variable"
    )
    predictions = categorizer.predict_batch([tx])
    assert len(predictions) == 1
    p = predictions[0]
    assert p.confidence > 0.0

def test_invalid_input_handling():
    categorizer = TransactionCategorizer()
    tx = Transaction(
        transaction_id="tx_test2",
        user_id="user1",
        event_type="expense",
        description="",  # Empty description
        category="Uncategorized",
        direction="debit",
        amount=0.0,
        currency="USD",
        event_date=date.today(),
        status="COMPLETED",
        flexibility="variable"
    )
    predictions = categorizer.predict_batch([tx])
    assert len(predictions) == 1
    assert predictions[0].category is not None
