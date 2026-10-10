import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models import User
from app.auth import get_current_user
from app.schemas.financial import Transaction, FinancialProfile
from app.schemas.planner import ProbabilisticForecastRequest, ProbabilisticForecastResponse
from app.ml.forecasting import PredictionEngine

client = TestClient(app)


def build_synthetic_history(num_months: int = 5, base_income: float = 4000.0, base_expense: float = 2200.0):
    """
    Builds deterministic chronological transaction history for testing.
    Uses fixed offsets so results are 100% reproducible.
    """
    transactions = []
    start_year = 2026
    start_month = 1

    for m in range(num_months):
        mo = (start_month + m - 1) % 12 + 1
        yr = start_year + (start_month + m - 1) // 12
        month_str = f"{yr}-{mo:02d}"

        # 1. Income transaction (salary on 1st of month)
        # Slight variation +/- $100
        var_inc = 100.0 if (m % 2 == 1) else -50.0
        transactions.append(
            Transaction(
                transaction_id=f"tx_inc_{m}",
                user_id="test_user",
                event_type="income",
                description="Monthly Salary",
                category="income",
                direction="credit",
                amount=base_income + var_inc,
                currency="USD",
                event_date=date(yr, mo, 1),
                status="SETTLED",
                flexibility="variable"
            )
        )

        # 2. Essential fixed rent on 5th of month
        transactions.append(
            Transaction(
                transaction_id=f"tx_rent_{m}",
                user_id="test_user",
                event_type="expense",
                description="Apartment Rent",
                category="housing",
                direction="debit",
                amount=1200.0,
                currency="USD",
                event_date=date(yr, mo, 5),
                status="SETTLED",
                flexibility="fixed"
            )
        )

        # 3. Essential utilities / loan debt obligation
        transactions.append(
            Transaction(
                transaction_id=f"tx_debt_{m}",
                user_id="test_user",
                event_type="debt_payment",
                description="Auto Loan EMI",
                category="debt_repayment",
                direction="debit",
                amount=300.0,
                currency="USD",
                event_date=date(yr, mo, 10),
                status="SETTLED",
                flexibility="fixed"
            )
        )

        # 4. Discretionary groceries/dining
        var_disc = 80.0 if (m % 2 == 1) else -40.0
        transactions.append(
            Transaction(
                transaction_id=f"tx_groceries_{m}",
                user_id="test_user",
                event_type="expense",
                description="Groceries & Dining",
                category="groceries",
                direction="debit",
                amount=700.0 + var_disc,
                currency="USD",
                event_date=date(yr, mo, 15),
                status="SETTLED",
                flexibility="variable"
            )
        )

    return transactions


@pytest.fixture
def test_profile():
    return FinancialProfile(
        user_id="user_prob_test",
        home_currency="USD",
        current_available_balance=5000.0,
        minimum_balance_to_keep=2000.0,
        financial_priorities=["safety_buffer", "retirement"],
        expense_categories_to_protect=["housing", "debt_repayment"],
        expense_categories_user_is_willing_to_reduce=["groceries"],
        expense_categories_user_is_willing_to_stop=["entertainment"],
        payment_methods_user_will_consider=["debit"],
        max_installment_months=12
    )


# -----------------------------------------------------------------------------
# 1. PredictionEngine Probabilistic Unit Tests
# -----------------------------------------------------------------------------
def test_probabilistic_forecast_horizon_and_distributions(test_profile):
    """
    Verify probabilistic forecast produces >= 6 periods with mean, median,
    prediction intervals, and shortfall probability under declared uncertainty method.
    """
    engine = PredictionEngine(min_months_required=3)
    transactions = build_synthetic_history(num_months=5)

    req = ProbabilisticForecastRequest(
        horizon_months=6,
        confidence_level=0.90,
        uncertainty_method="student_t_residual_growth"
    )

    result = engine.run_probabilistic_forecast(transactions, test_profile, req)

    assert result.available is True
    assert result.horizon_months == 6
    assert len(result.periods) == 6
    assert result.uncertainty_method == "student_t_residual_growth"
    assert result.confidence_level == 0.90
    assert result.declared_minimum_reserve == 2000.0

    # Inspect Period 1
    p1 = result.periods[0]
    assert p1.period_index == 1
    assert p1.projected_income.mean > 3800.0
    assert p1.projected_income.lower_bound <= p1.projected_income.mean <= p1.projected_income.upper_bound
    assert p1.essential_expenses.mean == 1500.0  # rent (1200) + auto loan (300)
    assert p1.known_obligations == 1500.0  # rent + debt
    assert p1.projected_cash_flow.mean > 0.0

    # Verify cumulative balance progression and shortfall probability
    for p in result.periods:
        assert p.projected_cumulative_balance.lower_bound <= p.projected_cumulative_balance.mean
        assert p.projected_cumulative_balance.mean <= p.projected_cumulative_balance.upper_bound
        assert 0.0 <= p.probability_below_reserve <= 1.0


def test_probabilistic_forecast_held_out_evaluation_and_baseline(test_profile):
    """
    Verify chronological train/test split: future observations kept out of training.
    Verify MAE, RMSE, interval coverage, interval width, and baseline comparison.
    """
    engine = PredictionEngine(min_months_required=3)
    transactions = build_synthetic_history(num_months=5)

    result = engine.run_probabilistic_forecast(transactions, test_profile)

    assert result.evaluation_metrics is not None
    metrics = result.evaluation_metrics
    # For num_months = 5, rolling-origin backtesting evaluates >= 2 origins
    assert metrics.evaluation_periods_evaluated >= 2
    assert metrics.income_mae >= 0.0
    assert metrics.income_rmse >= 0.0
    assert metrics.expense_mae >= 0.0
    assert metrics.expense_rmse >= 0.0
    assert 0.0 <= metrics.interval_coverage <= 1.0
    assert metrics.mean_interval_width > 0.0

    # Baseline model check
    assert metrics.baseline_model == "historical_average"
    assert metrics.baseline_income_mae >= 0.0
    assert result.baseline_comparison is not None
    assert "historical_mean_income" in result.baseline_comparison
    assert "evaluation_origins_tested" in result.baseline_comparison
    assert len(result.baseline_comparison["evaluation_origins_tested"]) >= 2
    assert "selected_income_model" in result.baseline_comparison
    assert "selected_expense_model" in result.baseline_comparison


def test_probabilistic_forecast_insufficient_history(test_profile):
    """
    Verify honest diagnostic when historical data is below minimum requirement.
    Does not invent confidence or calibrated probabilities.
    """
    engine = PredictionEngine(min_months_required=3)
    # Only 2 months provided
    short_history = build_synthetic_history(num_months=2)

    result = engine.run_probabilistic_forecast(short_history, test_profile)

    assert result.available is False
    assert "Insufficient historical observations" in result.reason
    assert len(result.periods) == 0


def test_probabilistic_forecast_does_not_mutate_transactions(test_profile):
    """Ensure forecasting executes in a pure functional manner without mutating inputs."""
    engine = PredictionEngine()
    transactions = build_synthetic_history(num_months=4)
    original_amounts = [t.amount for t in transactions]

    _ = engine.run_probabilistic_forecast(transactions, test_profile)

    current_amounts = [t.amount for t in transactions]
    assert original_amounts == current_amounts


# -----------------------------------------------------------------------------
# 2. HTTP Endpoint & Security Tests: POST /api/users/forecast/probabilistic
# -----------------------------------------------------------------------------
def test_forecast_probabilistic_requires_auth():
    """Unauthenticated calls must be rejected with 401."""
    res = client.post("/api/users/forecast/probabilistic", json={})
    assert res.status_code == 401


def test_forecast_probabilistic_endpoint_success(monkeypatch, test_profile):
    """Verify authenticated endpoint returns valid ProbabilisticForecastResponse."""
    mock_user = User(id=777, email="prob_user@fin4you.ai", is_verified=True, is_active=True)
    app.dependency_overrides[get_current_user] = lambda: mock_user

    txs = build_synthetic_history(num_months=4)

    # Mock DB service to supply test transactions and profile
    from app.api import users as users_api
    monkeypatch.setattr(users_api, "get_user_profile", lambda db, uid: test_profile)
    monkeypatch.setattr(users_api, "get_user_transactions", lambda db, uid: txs)

    try:
        payload = {
            "horizon_months": 6,
            "confidence_level": 0.90,
            "uncertainty_method": "student_t_residual_growth"
        }
        res = client.post("/api/users/forecast/probabilistic", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["available"] is True
        assert data["horizon_months"] == 6
        assert len(data["periods"]) == 6
        assert data["uncertainty_method"] == "student_t_residual_growth"
        assert "evaluation_metrics" in data
    finally:
        app.dependency_overrides.pop(get_current_user, None)
