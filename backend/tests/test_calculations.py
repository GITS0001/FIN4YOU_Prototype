import pytest
from app.financial.state import FinancialStateEngine
from app.ml.forecasting import PredictionEngine
from app.schemas.financial import Transaction, FinancialProfile
from datetime import date


def test_income_and_expense_totals():
    txs = [
        Transaction(
            transaction_id="1", user_id="u1", event_type="income", description="Salary",
            category="Income", direction="credit", amount=5000.0, currency="USD",
            event_date=date.today(), status="COMPLETED", flexibility="variable"
        ),
        Transaction(
            transaction_id="2", user_id="u1", event_type="expense", description="Rent",
            category="Housing", direction="debit", amount=1500.0, currency="USD",
            event_date=date.today(), status="COMPLETED", flexibility="fixed"
        ),
        Transaction(
            transaction_id="3", user_id="u1", event_type="expense", description="Groceries",
            category="Food", direction="debit", amount=300.0, currency="USD",
            event_date=date.today(), status="COMPLETED", flexibility="variable"
        )
    ]
    engine = FinancialStateEngine(user_id="u1")
    state = engine.calculate_state(txs)
    assert state.income == 5000.0
    assert state.expenses == 1800.0
    assert state.cash_flow == 3200.0

def test_refund_treatment():
    txs = [
        Transaction(
            transaction_id="1", user_id="u1", event_type="expense", description="Store Purchase",
            category="Shopping", direction="debit", amount=100.0, currency="USD",
            event_date=date.today(), status="COMPLETED", flexibility="variable"
        ),
        Transaction(
            transaction_id="2", user_id="u1", event_type="income", description="Refund Store Purchase",
            category="Refund", direction="credit", amount=100.0, currency="USD",
            event_date=date.today(), status="COMPLETED", flexibility="variable"
        )
    ]
    engine = FinancialStateEngine(user_id="u1")
    state = engine.calculate_state(txs)
    # Both are counted, net cash flow should balance to 0
    assert state.expenses == 100.0
    assert state.income == 100.0
    assert state.cash_flow == 0.0

def test_insufficient_history_for_forecasting():
    txs = [
        Transaction(
            transaction_id="1", user_id="u1", event_type="income", description="Salary",
            category="Income", direction="credit", amount=5000.0, currency="USD",
            event_date=date.today(), status="COMPLETED", flexibility="fixed"
        )
    ]
    profile = FinancialProfile(
        user_id="u1",
        home_currency="USD",
        current_available_balance=5000.0,
        minimum_balance_to_keep=1000.0,
        financial_priorities=[],
        expense_categories_to_protect=[],
        expense_categories_user_is_willing_to_reduce=[],
        expense_categories_user_is_willing_to_stop=[],
        payment_methods_user_will_consider=[]
    )
    engine = PredictionEngine()
    prediction = engine.run_prediction(txs, profile)
    # The forecasting should gracefully run, though maybe lacking confidence
    assert prediction is not None

def test_internal_transfer_does_not_inflate_totals():
    txs = [
        Transaction(
            transaction_id="1", user_id="u1", event_type="income", description="Salary",
            category="Income", direction="credit", amount=50000.0, currency="INR",
            event_date=date.today(), status="COMPLETED", flexibility="variable"
        ),
        Transaction(
            transaction_id="2", user_id="u1", event_type="expense", description="Rent",
            category="Housing", direction="debit", amount=15000.0, currency="INR",
            event_date=date.today(), status="COMPLETED", flexibility="fixed"
        ),
        Transaction(
            transaction_id="3", user_id="u1", event_type="transfer", description="Self Transfer to Savings",
            category="Transfer", direction="debit", amount=10000.0, currency="INR",
            event_date=date.today(), status="COMPLETED", flexibility="variable"
        ),
        Transaction(
            transaction_id="4", user_id="u1", event_type="transfer", description="Self Transfer from Checking",
            category="Transfer", direction="credit", amount=10000.0, currency="INR",
            event_date=date.today(), status="COMPLETED", flexibility="variable"
        )
    ]
    engine = FinancialStateEngine(user_id="u1")
    state = engine.calculate_state(txs)
    # Transfers should not inflate income or expenses
    assert state.income == 50000.0
    assert state.expenses == 15000.0
    assert state.cash_flow == 35000.0

def test_financial_invariants_and_category_reconciliation():
    txs = [
        Transaction(
            transaction_id="1", user_id="u1", event_type="income", description="Salary",
            category="Income", direction="credit", amount=60000.0, currency="INR",
            event_date=date.today(), status="COMPLETED", flexibility="variable"
        ),
        Transaction(
            transaction_id="2", user_id="u1", event_type="expense", description="Groceries",
            category="Groceries", direction="debit", amount=5000.0, currency="INR",
            event_date=date.today(), status="COMPLETED", flexibility="variable"
        ),
        Transaction(
            transaction_id="3", user_id="u1", event_type="expense", description="Dining",
            category="Food", direction="debit", amount=3000.0, currency="INR",
            event_date=date.today(), status="COMPLETED", flexibility="variable"
        ),
        Transaction(
            transaction_id="4", user_id="u1", event_type="refund", description="Returned Groceries Item",
            category="Groceries", direction="credit", amount=1000.0, currency="INR",
            event_date=date.today(), status="COMPLETED", flexibility="variable"
        )
    ]
    engine = FinancialStateEngine(user_id="u1")
    state = engine.calculate_state(txs)
    
    # Invariant 1: Cash flow = income - expenses
    assert state.cash_flow == state.income - state.expenses
    # Invariant 2: Refund nets against expenses (5000 + 3000 - 1000 = 7000)
    assert state.expenses == 7000.0
    assert state.income == 60000.0
    assert state.cash_flow == 53000.0
    # Invariant 3: Category totals match total expenses
    sum_categories = sum(c.total_amount for c in state.category_spending)
    assert sum_categories == state.expenses


