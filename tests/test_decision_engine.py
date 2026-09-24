import pytest
from app.schemas.financial import FinancialProfile, PredictionEngineResult, ProjectedCashFlow, PaymentOption, FinancialState, CategorySpending
from app.decision.simulation import WhatIfSimulator
from app.decision.impact import ImpactEngine
from app.decision.affordability import AffordabilityEngine
from app.decision.engine import DecisionEngine

@pytest.fixture
def mock_profile():
    return FinancialProfile(
        user_id="u1",
        home_currency="ZAR",
        current_available_balance=1000.0,
        minimum_balance_to_keep=500.0,
        financial_priorities=[],
        expense_categories_to_protect=[],
        expense_categories_user_is_willing_to_reduce=[],
        expense_categories_user_is_willing_to_stop=[],
        payment_methods_user_will_consider=[]
    )

@pytest.fixture
def mock_prediction_safe():
    return PredictionEngineResult(
        available=True,
        projected_cash_flow=ProjectedCashFlow(
            period="next_month",
            projected_income=2000.0,
            projected_expenses=1000.0,
            known_obligations=500.0,
            projected_cash_flow=500.0 # 2000 - 1000 - 500 = 500
        )
    )

@pytest.fixture
def mock_prediction_gap():
    return PredictionEngineResult(
        available=True,
        projected_cash_flow=ProjectedCashFlow(
            period="next_month",
            projected_income=2000.0,
            projected_expenses=1500.0,
            known_obligations=1200.0,
            projected_cash_flow=-700.0 # 2000 - 1500 - 1200 = -700
        )
    )

@pytest.fixture
def mock_state():
    return FinancialState(
        user_id="u1",
        income=2000.0,
        expenses=1000.0,
        savings=1000.0,
        savings_rate=0.5,
        expense_ratio=0.5,
        essential_expenses=500.0,
        discretionary_expenses=500.0,
        recurring_obligations=0.0,
        emi_burden=0.0,
        cash_flow=1000.0,
        category_spending=[],
        anomalies=[],
        data_quality_confidence=1.0
    )

def test_what_if_simulator(mock_profile, mock_prediction_safe):
    sim = WhatIfSimulator(mock_profile, mock_prediction_safe)
    
    # Baseline
    baseline = sim.baseline_scenario()
    assert baseline.projected_balance == 1500.0 # 1000 (current) + 500 (cf)
    assert not baseline.buffer_breached
    
    # Reduce discretionary by 200
    scenario_reduce = sim.simulate_reduce_discretionary_spending(200.0)
    assert scenario_reduce.projected_expenses == 800.0
    assert scenario_reduce.projected_cash_flow == 700.0
    assert scenario_reduce.projected_balance == 1700.0
    
    # Add obligation of 1200
    scenario_ob = sim.simulate_add_obligation(1200.0)
    assert scenario_ob.projected_cash_flow == -700.0
    assert scenario_ob.projected_balance == 300.0 # 1000 - 700 = 300
    assert scenario_ob.buffer_breached
    assert scenario_ob.shortfall == 200.0 # 500 (min) - 300 = 200

def test_impact_engine(mock_profile, mock_prediction_safe):
    sim = WhatIfSimulator(mock_profile, mock_prediction_safe)
    baseline = sim.baseline_scenario()
    
    scenario_ob = sim.simulate_add_obligation(1200.0)
    impact = ImpactEngine.calculate_impact(baseline, scenario_ob)
    
    assert impact.cash_flow_difference == -1200.0
    assert impact.buffer_status_change == "breached"

def test_affordability_engine_affordable(mock_profile, mock_prediction_safe):
    aff = AffordabilityEngine(mock_profile, mock_prediction_safe)
    # Afford a 500 expense
    res = aff.evaluate_purchase(500.0, [])
    assert res.status == "AFFORDABLE"
    assert res.resulting_balance == 1000.0 # 1000 (start) + 500 (cf) - 500 (purchase)
    assert res.trade_off_required == 0.0

def test_affordability_engine_tradeoff(mock_profile, mock_prediction_safe):
    aff = AffordabilityEngine(mock_profile, mock_prediction_safe)
    # 1000 (start) + 500 (cf) = 1500 balance. Min = 500. Discretionary = 1000.
    # Purchase = 1200. Resulting balance = 300. Shortfall = 200.
    res = aff.evaluate_purchase(1200.0, [])
    assert res.status == "POTENTIALLY AFFORDABLE WITH TRADE-OFF"
    assert res.shortfall == 200.0
    assert res.trade_off_required == 200.0

def test_affordability_engine_unaffordable(mock_profile, mock_prediction_safe):
    aff = AffordabilityEngine(mock_profile, mock_prediction_safe)
    # Purchase = 3000. Resulting balance = 1500 - 3000 = -1500. Shortfall = 2000.
    # Discretionary is only 1000, so we can't trade off 2000.
    res = aff.evaluate_purchase(3000.0, [])
    assert res.status == "NOT AFFORDABLE UNDER CURRENT PROJECTION"

def test_affordability_engine_installments(mock_profile, mock_prediction_safe):
    aff = AffordabilityEngine(mock_profile, mock_prediction_safe)
    
    po1 = PaymentOption(payment_option_id="p1", request_id="r1", payment_method="full", payment_amount=3000, number_of_payments=1, first_payment_date="2024-01-01", financing_fee=0, total_payable_amount=3000)
    po2 = PaymentOption(payment_option_id="p2", request_id="r1", payment_method="installment", payment_amount=200, number_of_payments=15, first_payment_date="2024-01-01", financing_fee=0, total_payable_amount=3000)
    
    res = aff.evaluate_purchase(3000.0, [po1, po2])
    
    # 3000 upfront is not affordable, but 200/month is affordable since 1500 - 200 = 1300 >= 500.
    assert len(res.viable_payment_options) == 1
    assert res.viable_payment_options[0].payment_option_id == "p2"

def test_decision_engine_gap(mock_profile, mock_state, mock_prediction_gap):
    engine = DecisionEngine(mock_profile, mock_state, mock_prediction_gap)
    trace = engine.generate_recommendation_for_gap()
    
    assert trace is not None
    assert trace.recommendation.recommendation_type == "REDUCE_DISCRETIONARY_SPENDING"
    # Gap is 1000 + (-700) = 300 balance. Shortfall = 200.
    # Max reduction = 50% of 1500 = 750. Shortfall 200 is less, so we reduce by 200.
    assert "200.00" in trace.recommendation.actionable_text
    assert trace.recommendation.expected_impact.buffer_status_change == "restored"
    assert trace.supporting_data["suggested_reduction"] == 200.0
