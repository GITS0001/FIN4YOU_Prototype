import pytest
from pathlib import Path
from app.schemas.financial import Transaction, FinancialProfile
from app.ingestion.loader import DataLoader
import pandas as pd
from datetime import date

def test_transaction_schema():
    t = Transaction(
        transaction_id="t1",
        user_id="u1",
        event_type="expense",
        description="test",
        category="food",
        direction="debit",
        amount=-50.0, # test absolute normalization
        currency="ZAR",
        event_date="2024-01-01",
        status="settled",
        flexibility="variable"
    )
    assert t.amount == 50.0
    assert t.event_date == date(2024, 1, 1)

def test_profile_schema_pipe_separated():
    p = FinancialProfile(
        user_id="u1",
        home_currency="IDR",
        current_available_balance=1000.0,
        minimum_balance_to_keep=500.0,
        financial_priorities="education|debt_repayment",
        expense_categories_to_protect="rent",
        expense_categories_user_is_willing_to_reduce=None,
        expense_categories_user_is_willing_to_stop=pd.NA,
        payment_methods_user_will_consider="full_payment"
    )
    assert "education" in p.financial_priorities
    assert "debt_repayment" in p.financial_priorities
    assert p.expense_categories_user_is_willing_to_reduce == []
    assert p.expense_categories_user_is_willing_to_stop == []

def test_data_loader(tmp_path):
    # Create dummy data
    d = tmp_path / "data"
    d.mkdir()
    
    events_csv = d / "financial_events.csv"
    events_csv.write_text("event_id,user_id,event_type,description,category,direction,amount,currency,event_date,settlement_date,status,linked_event_id,flexibility,minimum_allowed_amount\n"
                          "e1,u1,expense,food,food,debit,50,ZAR,2024-01-01,,settled,,,\n"
                          "e2,u1,expense,food,food,debit,,ZAR,2024-01-02,,settled,,,") # missing amount
    
    loader = DataLoader(str(d))
    events = loader.load_events()
    
    assert len(events) == 1
    assert events[0].transaction_id == "e1"
    assert events[0].amount == 50
    assert events[0].settlement_date == date(2024, 1, 1)
    assert events[0].flexibility == "variable"
