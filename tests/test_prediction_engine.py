import pytest
from datetime import date
from app.schemas.financial import Transaction, FinancialProfile
from app.ml.forecasting import PredictionEngine

@pytest.fixture
def sample_profile():
    return FinancialProfile(
        user_id="u1",
        home_currency="ZAR",
        current_available_balance=2000.0,
        minimum_balance_to_keep=500.0,
        financial_priorities=[],
        expense_categories_to_protect=[],
        expense_categories_user_is_willing_to_reduce=[],
        expense_categories_user_is_willing_to_stop=[],
        payment_methods_user_will_consider=[]
    )

@pytest.fixture
def sufficient_history_transactions():
    return [
        # Month 1
        Transaction(transaction_id="t1", user_id="u1", event_type="income", description="Salary", category="salary", direction="credit", amount=5000.0, currency="ZAR", event_date=date(2024, 1, 1), status="settled", flexibility="variable"),
        Transaction(transaction_id="t2", user_id="u1", event_type="expense", description="Groceries", category="groceries", direction="debit", amount=1000.0, currency="ZAR", event_date=date(2024, 1, 15), status="settled", flexibility="variable"),
        Transaction(transaction_id="t3", user_id="u1", event_type="subscription", description="Netflix", category="entertainment", direction="debit", amount=100.0, currency="ZAR", event_date=date(2024, 1, 10), status="settled", flexibility="fixed"),
        
        # Month 2
        Transaction(transaction_id="t4", user_id="u1", event_type="income", description="Salary", category="salary", direction="credit", amount=5000.0, currency="ZAR", event_date=date(2024, 2, 1), status="settled", flexibility="variable"),
        Transaction(transaction_id="t5", user_id="u1", event_type="expense", description="Groceries", category="groceries", direction="debit", amount=1200.0, currency="ZAR", event_date=date(2024, 2, 15), status="settled", flexibility="variable"),
        Transaction(transaction_id="t6", user_id="u1", event_type="subscription", description="Netflix", category="entertainment", direction="debit", amount=100.0, currency="ZAR", event_date=date(2024, 2, 10), status="settled", flexibility="fixed"),

        # Month 3
        Transaction(transaction_id="t7", user_id="u1", event_type="income", description="Salary", category="salary", direction="credit", amount=5000.0, currency="ZAR", event_date=date(2024, 3, 1), status="settled", flexibility="variable"),
        Transaction(transaction_id="t8", user_id="u1", event_type="expense", description="Groceries", category="groceries", direction="debit", amount=1100.0, currency="ZAR", event_date=date(2024, 3, 15), status="settled", flexibility="variable"),
        Transaction(transaction_id="t9", user_id="u1", event_type="subscription", description="Netflix", category="entertainment", direction="debit", amount=100.0, currency="ZAR", event_date=date(2024, 3, 10), status="settled", flexibility="fixed"),
    ]

@pytest.fixture
def insufficient_history_transactions():
    return [
        Transaction(transaction_id="t1", user_id="u1", event_type="income", description="Salary", category="salary", direction="credit", amount=5000.0, currency="ZAR", event_date=date(2024, 1, 1), status="settled", flexibility="variable"),
        Transaction(transaction_id="t2", user_id="u1", event_type="expense", description="Groceries", category="groceries", direction="debit", amount=1000.0, currency="ZAR", event_date=date(2024, 1, 15), status="settled", flexibility="variable"),
    ]

def test_prediction_engine_sufficient_data(sufficient_history_transactions, sample_profile):
    engine = PredictionEngine(min_months_required=3)
    result = engine.run_prediction(sufficient_history_transactions, sample_profile)
    
    assert result.available is True
    
    # 2 forecasts: total_income, variable_expenses
    assert len(result.forecasts) == 2
    income_forecast = next(f for f in result.forecasts if f.target == "total_income")
    exp_forecast = next(f for f in result.forecasts if f.target == "variable_expenses")
    
    # Income MAE check (Train = 5000, 5000; Test = 5000 => MAE = 0)
    assert income_forecast.evaluation.mae == 0.0
    assert income_forecast.predicted_value == 5000.0
    assert income_forecast.uncertainty == 0.0
    
    # Expense MAE check (Train = 1000, 1200 => Avg 1100; Test = 1100 => MAE = 0)
    assert exp_forecast.evaluation.mae == 0.0
    assert exp_forecast.predicted_value == 1100.0 # (1000 + 1200 + 1100) / 3

    # Obligations (only from latest month, so 1 Netflix sub of 100)
    assert len(result.obligations) == 1
    assert result.obligations[0].expected_amount == 100.0

    # Projected Cash Flow = 5000 (inc) - 1100 (var exp) - 100 (obs) = 3800
    assert result.projected_cash_flow.projected_cash_flow == 3800.0
    assert result.projected_cash_flow.known_obligations == 100.0

    # Balance and Gap
    # Current Balance = 2000, Projected CF = 3800 => Projected Balance = 5800
    # Min Buffer = 500. 5800 > 500, so no gap.
    assert result.gap_detection.detected is False
    assert result.gap_detection.projected_balance == 5800.0

def test_prediction_engine_gap_detection(sufficient_history_transactions, sample_profile):
    # Artificially modify sample_profile so current balance is very low, and min_buffer is very high
    sample_profile.current_available_balance = 0.0
    sample_profile.minimum_balance_to_keep = 10000.0

    engine = PredictionEngine(min_months_required=3)
    result = engine.run_prediction(sufficient_history_transactions, sample_profile)
    
    assert result.available is True
    assert result.gap_detection.detected is True
    assert result.gap_detection.projected_balance == 3800.0 # 0 + 3800
    assert result.gap_detection.shortfall == 6200.0 # 10000 - 3800

def test_prediction_engine_insufficient_data(insufficient_history_transactions, sample_profile):
    engine = PredictionEngine(min_months_required=3)
    result = engine.run_prediction(insufficient_history_transactions, sample_profile)
    
    assert result.available is False
    assert "Insufficient historical observations" in result.reason
    assert len(result.forecasts) == 0
