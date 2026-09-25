import pytest
from datetime import date
from app.schemas.financial import Transaction, FinancialState, FinancialProfile
from app.ml.categorization import TransactionCategorizer
from app.ml.anomaly import AnomalyDetector
from app.financial.state import FinancialStateEngine

@pytest.fixture
def sample_transactions():
    return [
        Transaction(
            transaction_id="t1", user_id="u1", event_type="income", description="Salary",
            category="salary", direction="credit", amount=5000.0, currency="ZAR",
            event_date=date(2024, 1, 1), status="settled", flexibility="variable"
        ),
        Transaction(
            transaction_id="t2", user_id="u1", event_type="expense", description="Rent",
            category="rent", direction="debit", amount=1500.0, currency="ZAR",
            event_date=date(2024, 1, 2), status="settled", flexibility="fixed"
        ),
        Transaction(
            transaction_id="t3", user_id="u1", event_type="subscription", description="Netflix",
            category="entertainment", direction="debit", amount=20.0, currency="ZAR",
            event_date=date(2024, 1, 3), status="settled", flexibility="fixed"
        ),
        Transaction(
            transaction_id="t4", user_id="u1", event_type="debt_payment", description="Car Loan",
            category="debt_repayment", direction="debit", amount=300.0, currency="ZAR",
            event_date=date(2024, 1, 4), status="settled", flexibility="fixed"
        ),
        Transaction(
            transaction_id="t5", user_id="u1", event_type="expense", description="Groceries",
            category="groceries", direction="debit", amount=400.0, currency="ZAR",
            event_date=date(2024, 1, 5), status="settled", flexibility="variable"
        ),
        Transaction(
            transaction_id="t6", user_id="u1", event_type="expense", description="Groceries",
            category="groceries", direction="debit", amount=410.0, currency="ZAR",
            event_date=date(2024, 1, 6), status="settled", flexibility="variable"
        ),
        Transaction(
            transaction_id="t6_1", user_id="u1", event_type="expense", description="Groceries",
            category="groceries", direction="debit", amount=390.0, currency="ZAR",
            event_date=date(2024, 1, 6), status="settled", flexibility="variable"
        ),
        Transaction(
            transaction_id="t6_2", user_id="u1", event_type="expense", description="Groceries",
            category="groceries", direction="debit", amount=405.0, currency="ZAR",
            event_date=date(2024, 1, 6), status="settled", flexibility="variable"
        ),
        Transaction(
            transaction_id="t7", user_id="u1", event_type="expense", description="Groceries Anomaly",
            category="groceries", direction="debit", amount=10000.0, currency="ZAR",
            event_date=date(2024, 1, 7), status="settled", flexibility="variable"
        ),
    ]

def test_categorizer(sample_transactions):
    categorizer = TransactionCategorizer()
    preds = categorizer.predict_batch(sample_transactions)
    
    assert len(preds) == len(sample_transactions)
    assert preds[0].category == "salary"
    assert preds[0].confidence == 0.95

    # Test unknown category
    t_unknown = Transaction(
        transaction_id="t_unk", user_id="u1", event_type="expense", description="Mystery",
        category="", direction="debit", amount=100.0, currency="ZAR",
        event_date=date(2024, 1, 1), status="settled", flexibility="variable"
    )
    pred_unk = categorizer.predict(t_unknown)
    assert pred_unk.category == "unknown"
    assert pred_unk.confidence == 0.20

def test_anomaly_detector(sample_transactions):
    detector = AnomalyDetector(std_threshold=1.5)
    anomalies = detector.detect_anomalies(sample_transactions)
    
    # We expect t7 (Groceries Anomaly = 5000) to be flagged since the other two are 400 and 410.
    assert len(anomalies) == 1
    assert anomalies[0].transaction_id == "t7"
    assert anomalies[0].is_anomaly is True
    assert anomalies[0].anomaly_score > 1.5

def test_financial_state_engine(sample_transactions):
    engine = FinancialStateEngine(user_id="u1", std_threshold=1.5)
    state = engine.calculate_state(sample_transactions)

    # Income = 5000
    # Expenses = 1500 (rent) + 20 (sub) + 300 (loan) + 400 + 410 + 390 + 405 + 10000 (groceries) = 13425
    assert state.income == 5000.0
    assert state.expenses == 13425.0
    
    # Savings = 5000 - 13425 = -8425
    assert state.savings == -8425.0
    assert state.cash_flow == -8425.0
    
    # Ratios
    assert state.savings_rate == (-8425.0 / 5000.0)
    assert state.expense_ratio == (13425.0 / 5000.0)

    # Essential (fixed) = 1500 + 20 + 300 = 1820
    assert state.essential_expenses == 1820.0
    # Discretionary (variable) = 400 + 410 + 390 + 405 + 10000 = 11605
    assert state.discretionary_expenses == 11605.0

    # Recurring obligations (fixed + sub/debt) = 20 + 300 = 320
    assert state.recurring_obligations == 320.0

    # EMI burden (debt_payment) = 300
    assert state.emi_burden == 300.0

    # Anomalies
    assert len(state.anomalies) == 1

def test_empty_financial_state():
    engine = FinancialStateEngine(user_id="u_empty")
    state = engine.calculate_state([])
    
    assert state.income == 0.0
    assert state.expenses == 0.0
    assert state.savings == 0.0
    assert state.savings_rate == 0.0
    assert state.expense_ratio == 0.0

def test_profile_schema_empty_list():
    # Focused regression test to prove that passing an empty list []
    # to a pipe-separated field correctly returns [] without triggering
    # a pandas ambiguous truth value ValueError.
    p = FinancialProfile(
        user_id="u1",
        home_currency="USD",
        current_available_balance=1000.0,
        minimum_balance_to_keep=500.0,
        financial_priorities=[],
        expense_categories_to_protect=[],
        expense_categories_user_is_willing_to_reduce=[],
        expense_categories_user_is_willing_to_stop=[],
        payment_methods_user_will_consider=[]
    )
    assert p.financial_priorities == []
    assert p.expense_categories_to_protect == []
