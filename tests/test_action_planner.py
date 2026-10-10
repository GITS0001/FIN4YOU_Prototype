import pytest
from datetime import date
from fastapi.testclient import TestClient

from app.main import app
from app.models import User
from app.auth import get_current_user
from app.schemas.financial import Transaction, FinancialProfile
from app.schemas.planner import (
    ActionType, PeriodAction, FinancialGoal, CandidateActionPlan,
    PlanEvaluationRequest, PlanEvaluationResponse
)
from app.decision.planner import ConstrainedPlannerEngine

client = TestClient(app)


def build_scenario_transactions(num_months: int = 5, base_income: float = 4500.0, monthly_variance: float = 0.0):
    """Generates standard chronological transaction history for scenario evaluation."""
    txs = []
    for m in range(num_months):
        mo = (1 + m - 1) % 12 + 1
        yr = 2026 + (1 + m - 1) // 12

        v_inc = monthly_variance if (m % 2 == 1) else -monthly_variance
        v_disc = (monthly_variance * 0.7) if (m % 2 == 1) else -(monthly_variance * 0.7)

        # Income: $4,500 (+/- variance)
        txs.append(Transaction(
            transaction_id=f"tx_inc_{m}",
            user_id="user_plan",
            event_type="income",
            description="Salary",
            category="income",
            direction="credit",
            amount=base_income + v_inc,
            currency="USD",
            event_date=date(yr, mo, 1),
            status="SETTLED",
            flexibility="variable"
        ))

        # Essential Housing: $1,400
        txs.append(Transaction(
            transaction_id=f"tx_rent_{m}",
            user_id="user_plan",
            event_type="expense",
            description="Rent",
            category="housing",
            direction="debit",
            amount=1400.0,
            currency="USD",
            event_date=date(yr, mo, 3),
            status="SETTLED",
            flexibility="fixed"
        ))

        # Debt obligation: $400
        txs.append(Transaction(
            transaction_id=f"tx_debt_{m}",
            user_id="user_plan",
            event_type="debt_payment",
            description="Student Loan",
            category="debt_repayment",
            direction="debit",
            amount=400.0,
            currency="USD",
            event_date=date(yr, mo, 10),
            status="SETTLED",
            flexibility="fixed"
        ))

        # Discretionary: $1,200 (+/- variance)
        txs.append(Transaction(
            transaction_id=f"tx_disc_{m}",
            user_id="user_plan",
            event_type="expense",
            description="Shopping & Dining",
            category="dining",
            direction="debit",
            amount=1200.0 + v_disc,
            currency="USD",
            event_date=date(yr, mo, 15),
            status="SETTLED",
            flexibility="variable"
        ))
    return txs


@pytest.fixture
def planner_profile():
    return FinancialProfile(
        user_id="user_planner_1",
        home_currency="USD",
        current_available_balance=4000.0,
        minimum_balance_to_keep=2500.0,
        financial_priorities=["safety_buffer", "debt_paydown"],
        expense_categories_to_protect=["housing", "debt_repayment"],
        expense_categories_user_is_willing_to_reduce=["dining"],
        expense_categories_user_is_willing_to_stop=["entertainment"],
        payment_methods_user_will_consider=["debit"],
        max_installment_months=12
    )


# -----------------------------------------------------------------------------
# Scenario 1: Stable Income
# -----------------------------------------------------------------------------
def test_scenario_1_stable_income(planner_profile):
    """
    Scenario 1: Stable Income.
    Plans across 6 monthly periods.
    Compares candidate action sequences (Balanced Reserve vs Aggressive Acceleration).
    Shows period-by-period balances, trade-offs, and confirms reserve maintenance.
    """
    planner = ConstrainedPlannerEngine()
    txs = build_scenario_transactions(num_months=5, base_income=4500.0)

    req = PlanEvaluationRequest(
        horizon_months=6,
        income_shock_percentage=0.0,
        unexpected_essential_expense=0.0
    )

    res: PlanEvaluationResponse = planner.evaluate_plans(txs, planner_profile, req)

    assert res.horizon_months == 6
    assert len(res.evaluated_plans) >= 2
    assert res.declared_minimum_reserve == 2500.0

    # Verify each evaluated plan has 6 period projections
    for p in res.evaluated_plans:
        assert len(p.projections) == 6
        assert len(p.trade_off_summary) >= 0
        assert 0.0 <= p.average_shortfall_probability <= 1.0

    # Under stable $4,500 income with current balance $4,000, recommended plan maintains reserve
    best_plan = next(p for p in res.evaluated_plans if p.plan_id == res.recommended_plan_id)
    assert best_plan.reserve_breach_count == 0
    assert best_plan.final_projected_balance_mean > planner_profile.minimum_balance_to_keep


# -----------------------------------------------------------------------------
# Scenario 2: Income Reduction
# -----------------------------------------------------------------------------
def test_scenario_2_income_reduction(planner_profile):
    """
    Scenario 2: Income Reduction.
    Simulates a 25% drop in monthly income.
    Verifies that the planner replans, recalculates shortfall risk,
    and includes explicit replan notice.
    """
    planner = ConstrainedPlannerEngine()
    txs = build_scenario_transactions(num_months=5, base_income=4500.0)

    req = PlanEvaluationRequest(
        horizon_months=6,
        income_shock_percentage=-0.25,  # 25% income reduction
        unexpected_essential_expense=0.0
    )

    res: PlanEvaluationResponse = planner.evaluate_plans(txs, planner_profile, req)

    assert res.replan_notice is not None
    assert "-25.0%" in res.replan_notice
    assert len(res.evaluated_plans) >= 2

    # Under 25% income drop, income falls to ~$3,375.
    # The conservative/balanced plans that trim discretionary spending should be preferred
    assert res.recommended_plan_id in ["plan_conservative_liquidity", "plan_balanced_reserve"]


# -----------------------------------------------------------------------------
# Scenario 3: Unexpected Essential Expense
# -----------------------------------------------------------------------------
def test_scenario_3_unexpected_essential_expense(planner_profile):
    """
    Scenario 3: Unexpected Essential Expense.
    Adds a $1,800 emergency expense shock in month 1.
    Verifies that essential expenses cannot be cut and cash buffer absorbs shock.
    """
    planner = ConstrainedPlannerEngine()
    txs = build_scenario_transactions(num_months=5, base_income=4500.0)

    req = PlanEvaluationRequest(
        horizon_months=6,
        income_shock_percentage=0.0,
        unexpected_essential_expense=1800.0
    )

    res: PlanEvaluationResponse = planner.evaluate_plans(txs, planner_profile, req)

    assert res.replan_notice is not None
    assert "$1,800.00" in res.replan_notice

    # Check period 1 projections in the evaluated plans reflect increased essential outflow
    for p in res.evaluated_plans:
        p1 = p.projections[0]
        # Rent ($1,400) + emergency ($1,800) = $3,200
        assert p1.essential_expenses >= 3000.0


# -----------------------------------------------------------------------------
# Scenario 4: Infeasible Financial Goal
# -----------------------------------------------------------------------------
def test_scenario_4_infeasible_financial_goal(planner_profile):
    """
    Scenario 4: Infeasible Financial Goal.
    User specifies an unrealistic goal: save $10,000 by period 2 with balance $4,000.
    Verifies that:
    - Goal is detected as infeasible (is_feasible == False)
    - Specific conflict reason is provided
    - Explicit proposed relaxations (timeline extension, target amount scale-down, discretionary cut) are generated.
    """
    planner = ConstrainedPlannerEngine()
    txs = build_scenario_transactions(num_months=5, base_income=4500.0)

    infeasible_goal = FinancialGoal(
        goal_id="goal_supercar",
        name="Emergency Reserve Expansion & Vacation",
        target_amount=10000.0,
        target_period_index=2,
        priority="high"
    )

    req = PlanEvaluationRequest(
        horizon_months=6,
        goals=[infeasible_goal]
    )

    res: PlanEvaluationResponse = planner.evaluate_plans(txs, planner_profile, req)

    for p in res.evaluated_plans:
        assert p.all_goals_feasible is False
        assert len(p.goals_feasibility) == 1
        gf = p.goals_feasibility[0]
        assert gf.is_feasible is False
        assert gf.shortfall > 0.0
        assert gf.conflict_reason is not None
        assert "shortfall of" in gf.conflict_reason.lower()
        # Verify explicit proposed relaxations
        assert len(gf.proposed_relaxations) >= 3
        assert any("timeline" in r.lower() or "extend" in r.lower() for r in gf.proposed_relaxations)
        assert any("amount" in r.lower() or "scale" in r.lower() for r in gf.proposed_relaxations)
        assert any("discretionary" in r.lower() for r in gf.proposed_relaxations)


# -----------------------------------------------------------------------------
# Scenario 5: Uncertainty Changes Preferred Plan
# -----------------------------------------------------------------------------
def test_scenario_5_uncertainty_changes_preferred_plan(planner_profile):
    """
    Demonstrates a case where uncertainty changes the preferred plan:
    Plan High-Yield Aggressive has a higher expected ending balance, but high uncertainty
    causes an unacceptable shortfall probability (> 15%).
    Plan Safe Buffer has a lower expected ending balance, but preserves liquidity with
    acceptable shortfall risk (<= 15%).
    Verifies that the planner rejects the aggressive plan due to forecast uncertainty,
    asserting:
    1. uncertainty_changed_preference == True
    2. the selected plan is the safer plan
    3. both plans were evaluated
    4. the expected financial advantage of the aggressive plan is documented.
    """
    planner = ConstrainedPlannerEngine()
    # Income close to expenses with historical volatility to establish realistic prediction distributions
    txs = build_scenario_transactions(num_months=5, base_income=3050.0, monthly_variance=200.0)

    # Tighten starting cash so buffer margin is close to minimum reserve ($2,500)
    tight_profile = planner_profile.model_copy(update={
        "current_available_balance": 2550.0,
        "minimum_balance_to_keep": 2500.0
    })

    # Plan Safe: Moderate, disciplined discretionary reduction with low uncertainty
    plan_safe = CandidateActionPlan(
        plan_id="plan_safe_buffer",
        name="Buffer Protection Plan",
        strategy_description="Moderate discretionary trim ensuring safe liquidity above minimum reserve.",
        actions=[
            PeriodAction(
                period_index=p,
                action_type=ActionType.REDUCE_DISCRETIONARY,
                amount=100.0,
                description="Moderate discretionary trim"
            ) for p in range(1, 7)
        ],
        uncertainty_multiplier=0.5
    )

    # Plan Aggressive: Heavy discretionary spending cuts leading to higher expected ending balance,
    # but with high uncertainty (e.g., volatile side-gig or austere execution risk)
    plan_aggressive = CandidateActionPlan(
        plan_id="plan_aggressive_risk",
        name="High-Yield Aggressive Plan",
        strategy_description="Aggressive savings cuts yielding higher expected ending balance but with elevated uncertainty.",
        actions=[
            PeriodAction(
                period_index=p,
                action_type=ActionType.REDUCE_DISCRETIONARY,
                amount=400.0,
                description="Aggressive discretionary reduction"
            ) for p in range(1, 7)
        ],
        uncertainty_multiplier=2.5
    )

    req = PlanEvaluationRequest(
        horizon_months=6,
        candidate_plans=[plan_safe, plan_aggressive]
    )

    res = planner.evaluate_plans(txs, tight_profile, req)

    # 1. Uncertainty changed preference from naive highest-expected-balance to safer plan
    assert res.uncertainty_changed_preference is True

    # 2. Selected plan is the safer plan
    assert res.recommended_plan_id == "plan_safe_buffer"

    # 3. Both plans were evaluated
    assert len(res.evaluated_plans) == 2
    evaluated_ids = {p.plan_id for p in res.evaluated_plans}
    assert evaluated_ids == {"plan_safe_buffer", "plan_aggressive_risk"}

    # 4. Expected financial advantage of the aggressive plan is documented and verified
    p_safe = next(p for p in res.evaluated_plans if p.plan_id == "plan_safe_buffer")
    p_agg = next(p for p in res.evaluated_plans if p.plan_id == "plan_aggressive_risk")

    assert p_agg.final_projected_balance_mean > p_safe.final_projected_balance_mean
    assert p_agg.max_shortfall_probability > p_safe.max_shortfall_probability
    assert p_safe.max_shortfall_probability <= 0.15
    assert p_agg.max_shortfall_probability > 0.15

    # Recommendation rationale explicitly articulates trade-off
    assert "uncertainty" in res.recommendation_rationale.lower()
    assert "buffer protection plan" in res.recommendation_rationale.lower()


# -----------------------------------------------------------------------------
# HTTP Integration & Security Tests: POST /api/users/planner/evaluate
# -----------------------------------------------------------------------------
def test_planner_endpoint_requires_auth():
    """Unauthenticated calls must be rejected with 401."""
    res = client.post("/api/users/planner/evaluate", json={})
    assert res.status_code == 401


def test_planner_endpoint_authenticated_success(monkeypatch, planner_profile):
    """Verify authenticated endpoint uses verified user token and returns plan evaluations."""
    mock_user = User(id=888, email="planner_user@fin4you.ai", is_verified=True, is_active=True)
    app.dependency_overrides[get_current_user] = lambda: mock_user

    txs = build_scenario_transactions(num_months=5)

    from app.api import users as users_api
    monkeypatch.setattr(users_api, "get_user_profile", lambda db, uid: planner_profile)
    monkeypatch.setattr(users_api, "get_user_transactions", lambda db, uid: txs)

    try:
        payload = {
            "horizon_months": 6,
            "income_shock_percentage": 0.0,
            "unexpected_essential_expense": 0.0
        }
        res = client.post("/api/users/planner/evaluate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert len(data["evaluated_plans"]) >= 2
        assert data["recommended_plan_id"] != ""
        assert data["declared_minimum_reserve"] == 2500.0
    finally:
        app.dependency_overrides.pop(get_current_user, None)


# -----------------------------------------------------------------------------
# Hand-Calculated Accounting & Cash Balance Verification
# -----------------------------------------------------------------------------
def test_hand_calculated_accounting_cash_balance():
    """
    Independently verifies financial accounting and cash balance evolution
    against a deterministic, hand-calculated multi-period ledger.
    Guarantees contractual obligations are captured exactly once and neither omitted nor double-counted.

    Hand-calculated ledger:
    - Initial Starting Balance: $3,000.00
    - Minimum Cash Reserve: $2,000.00
    - Monthly Transactions (4 identical historical months):
        * Salary Income: $5,000.00
        * Rent (Essential/Fixed): $1,500.00
        * Loan (Debt Payment/Fixed): $500.00
        * Groceries (Discretionary/Variable): $1,000.00
    - Accounting Verification:
        * Monthly Essential Expenses = $1,500 + $500 = $2,000.00
        * Monthly Discretionary Expenses = $1,000.00
        * Known Contractual Obligations = $1,500 + $500 = $2,000.00
        * Base Net Cash Flow per period = $5,000 - $2,000 - $1,000 = +$2,000.00

    Candidate Plan Actions:
        * Period 1: Reduce discretionary by $200 (+ $200 cash flow)
            Expected Net CF = $2,000 + $200 = $2,200.00
            Expected Ending Balance = $3,000 + $2,200 = $5,200.00
        * Period 2: Accelerate debt payment by $800 (- $800 cash flow)
            Expected Net CF = $2,000 - $800 = $1,200.00
            Expected Ending Balance = $5,200 + $1,200 = $6,400.00
        * Period 3: No action ($0 modification)
            Expected Net CF = $2,000.00
            Expected Ending Balance = $6,400 + $2,000 = $8,400.00
        * Period 4: No action -> Ending Balance = $10,400.00
        * Period 5: No action -> Ending Balance = $12,400.00
        * Period 6: No action -> Ending Balance = $14,400.00
    """
    planner = ConstrainedPlannerEngine()

    # Build 4 identical historical months
    txs = []
    for m in range(1, 5):
        # Income $5,000
        txs.append(Transaction(
            transaction_id=f"tx_inc_{m}",
            user_id="hc_user",
            event_type="income",
            description="Salary",
            category="income",
            direction="credit",
            amount=5000.0,
            currency="USD",
            event_date=date(2026, m, 1),
            status="SETTLED",
            flexibility="variable"
        ))
        # Rent $1,500 (fixed)
        txs.append(Transaction(
            transaction_id=f"tx_rent_{m}",
            user_id="hc_user",
            event_type="expense",
            description="Apartment Rent",
            category="housing",
            direction="debit",
            amount=1500.0,
            currency="USD",
            event_date=date(2026, m, 5),
            status="SETTLED",
            flexibility="fixed"
        ))
        # Loan $500 (debt payment)
        txs.append(Transaction(
            transaction_id=f"tx_debt_{m}",
            user_id="hc_user",
            event_type="debt_payment",
            description="Car Loan",
            category="debt_repayment",
            direction="debit",
            amount=500.0,
            currency="USD",
            event_date=date(2026, m, 10),
            status="SETTLED",
            flexibility="fixed"
        ))
        # Groceries $1,000 (discretionary)
        txs.append(Transaction(
            transaction_id=f"tx_groc_{m}",
            user_id="hc_user",
            event_type="expense",
            description="Groceries",
            category="groceries",
            direction="debit",
            amount=1000.0,
            currency="USD",
            event_date=date(2026, m, 15),
            status="SETTLED",
            flexibility="variable"
        ))

    profile = FinancialProfile(
        user_id="hc_user",
        home_currency="USD",
        current_available_balance=3000.0,
        minimum_balance_to_keep=2000.0,
        financial_priorities=["safety_buffer"],
        expense_categories_to_protect=["housing"],
        expense_categories_user_is_willing_to_reduce=["groceries"],
        expense_categories_user_is_willing_to_stop=[],
        payment_methods_user_will_consider=["debit"],
        max_installment_months=12
    )

    plan = CandidateActionPlan(
        plan_id="plan_hand_calc",
        name="Hand Calculated Verification Plan",
        strategy_description="Validates ledger exactness.",
        actions=[
            PeriodAction(
                period_index=1,
                action_type=ActionType.REDUCE_DISCRETIONARY,
                amount=200.0,
                description="Trim discretionary spending"
            ),
            PeriodAction(
                period_index=2,
                action_type=ActionType.ACCELERATE_DEBT,
                amount=800.0,
                description="Extra debt paydown"
            )
        ]
    )

    dummy_plan = CandidateActionPlan(
        plan_id="plan_dummy",
        name="Dummy Baseline Plan",
        strategy_description="No action baseline.",
        actions=[]
    )

    req = PlanEvaluationRequest(
        horizon_months=6,
        candidate_plans=[plan, dummy_plan]
    )

    res = planner.evaluate_plans(txs, profile, req)
    p_hc = next(p for p in res.evaluated_plans if p.plan_id == "plan_hand_calc")

    # Verify period-by-period accounting exactly matches hand calculation
    expected_balances = [5200.0, 6400.0, 8400.0, 10400.0, 12400.0, 14400.0]
    expected_net_cfs = [2200.0, 1200.0, 2000.0, 2000.0, 2000.0, 2000.0]
    expected_mods = [200.0, -800.0, 0.0, 0.0, 0.0, 0.0]

    for idx, proj in enumerate(p_hc.projections):
        assert proj.projected_income == 5000.0
        assert proj.essential_expenses == 2000.0
        assert proj.discretionary_expenses == 1000.0
        assert proj.known_obligations == 2000.0
        assert proj.action_modifications == expected_mods[idx]
        assert proj.net_cash_flow == expected_net_cfs[idx]
        assert proj.ending_balance_mean == expected_balances[idx]

    assert p_hc.final_projected_balance_mean == 14400.0
    assert p_hc.reserve_breach_count == 0


def test_uncertainty_removal_reverses_plan_preference(planner_profile):
    """
    Ablation verification:
    Confirms that if uncertainty is omitted (naive risk-neutral ranking by highest expected balance),
    the aggressive plan would be selected over the safe plan.
    With uncertainty active, the risk-aware engine rejects the aggressive plan due to excessive
    reserve-breach risk (> 15%) and selects the safe plan instead.
    """
    planner = ConstrainedPlannerEngine()
    txs = build_scenario_transactions(num_months=5, base_income=3050.0, monthly_variance=200.0)

    tight_profile = planner_profile.model_copy(update={
        "current_available_balance": 2550.0,
        "minimum_balance_to_keep": 2500.0
    })

    plan_safe = CandidateActionPlan(
        plan_id="plan_safe_buffer",
        name="Buffer Protection Plan",
        strategy_description="Safe plan.",
        actions=[
            PeriodAction(
                period_index=p,
                action_type=ActionType.REDUCE_DISCRETIONARY,
                amount=100.0,
                description="Trim"
            ) for p in range(1, 7)
        ],
        uncertainty_multiplier=0.5
    )

    plan_agg = CandidateActionPlan(
        plan_id="plan_aggressive_risk",
        name="High-Yield Aggressive Plan",
        strategy_description="High expected return with high uncertainty.",
        actions=[
            PeriodAction(
                period_index=p,
                action_type=ActionType.REDUCE_DISCRETIONARY,
                amount=400.0,
                description="Aggressive trim"
            ) for p in range(1, 7)
        ],
        uncertainty_multiplier=2.5
    )

    req = PlanEvaluationRequest(
        horizon_months=6,
        candidate_plans=[plan_safe, plan_agg]
    )

    res = planner.evaluate_plans(txs, tight_profile, req)

    # 1. Active uncertainty selects safe plan
    assert res.recommended_plan_id == "plan_safe_buffer"
    assert res.uncertainty_changed_preference is True

    # 2. Risk-neutral ablation: ranking purely by expected balance reverses preference to aggressive plan
    p_safe = next(p for p in res.evaluated_plans if p.plan_id == "plan_safe_buffer")
    p_agg = next(p for p in res.evaluated_plans if p.plan_id == "plan_aggressive_risk")
    assert p_agg.final_projected_balance_mean > p_safe.final_projected_balance_mean

    naive_choice = max(res.evaluated_plans, key=lambda p: p.final_projected_balance_mean)
    assert naive_choice.plan_id == "plan_aggressive_risk"
    assert naive_choice.plan_id != res.recommended_plan_id
