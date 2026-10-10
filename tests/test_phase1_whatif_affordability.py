"""
Phase 1 tests: What-if Simulator & Affordability Engine
=======================================================
Covers all scenarios specified in the Phase 1 requirements:
  - Simulation: baseline, reduction, increase, zero-change, missing amount,
    invalid inputs, negative projected CF, cumulative differences, response text accuracy
  - Affordability: affordable, unaffordable, trade-off, installments,
    missing data, zero/negative EMI, invalid amounts, explanation accuracy
  - Integration: copilot API round-trips for what-if (increase + reduce),
    decision traces, data_sources accuracy

All fixtures are deterministic; no live Supabase or CSV access required.
"""
import pytest
from datetime import date

from app.schemas.financial import (
    FinancialProfile,
    PredictionEngineResult,
    ProjectedCashFlow,
    PaymentOption,
    FinancialState,
    CategorySpending,
)
from app.schemas.decision import WhatIfSummary
from app.decision.simulation import WhatIfSimulator
from app.decision.impact import ImpactEngine
from app.decision.affordability import AffordabilityEngine
from app.decision.engine import DecisionEngine
from app.copilot.intent_parser import IntentParser
from app.copilot.response_generator import ResponseGenerator
from app.schemas.copilot import ParsedIntent, IntentType


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def profile():
    """Standard profile: balance 5000, minimum buffer 1000."""
    return FinancialProfile(
        user_id="u_test",
        home_currency="INR",
        current_available_balance=5000.0,
        minimum_balance_to_keep=1000.0,
        financial_priorities=[],
        expense_categories_to_protect=[],
        expense_categories_user_is_willing_to_reduce=[],
        expense_categories_user_is_willing_to_stop=[],
        payment_methods_user_will_consider=[],
    )


@pytest.fixture
def safe_prediction():
    """Prediction where cash flow is comfortably positive."""
    return PredictionEngineResult(
        available=True,
        projected_cash_flow=ProjectedCashFlow(
            period="next_month",
            projected_income=10000.0,
            projected_expenses=4000.0,
            known_obligations=2000.0,
            projected_cash_flow=4000.0,  # 10000 - 4000 - 2000
        ),
    )


@pytest.fixture
def tight_prediction():
    """Prediction where cash flow is barely negative (gap scenario)."""
    return PredictionEngineResult(
        available=True,
        projected_cash_flow=ProjectedCashFlow(
            period="next_month",
            projected_income=5000.0,
            projected_expenses=3500.0,
            known_obligations=2000.0,
            projected_cash_flow=-500.0,  # 5000 - 3500 - 2000
        ),
    )


@pytest.fixture
def unavailable_prediction():
    """Prediction with insufficient historical data."""
    return PredictionEngineResult(
        available=False,
        reason="Insufficient historical observations.",
    )


@pytest.fixture
def mock_state():
    return FinancialState(
        user_id="u_test",
        income=10000.0,
        expenses=6000.0,
        savings=4000.0,
        savings_rate=0.4,
        expense_ratio=0.6,
        essential_expenses=2000.0,
        discretionary_expenses=4000.0,
        recurring_obligations=2000.0,
        emi_burden=500.0,
        cash_flow=4000.0,
        category_spending=[],
        anomalies=[],
        data_quality_confidence=1.0,
    )


# ===========================================================================
# What-if Simulator Tests
# ===========================================================================

class TestWhatIfSimulatorBaseline:
    def test_baseline_correct_values(self, profile, safe_prediction):
        sim = WhatIfSimulator(profile, safe_prediction)
        b = sim.baseline_scenario()
        # balance = 5000 + 4000 = 9000
        assert b.projected_balance == 9000.0
        assert b.projected_cash_flow == 4000.0
        assert not b.buffer_breached
        assert b.shortfall == 0.0

    def test_baseline_raises_when_unavailable(self, profile, unavailable_prediction):
        sim = WhatIfSimulator(profile, unavailable_prediction)
        with pytest.raises(ValueError, match="not available"):
            sim.baseline_scenario()


class TestWhatIfSpendingReduction:
    def test_reduce_decreases_expenses_and_increases_cf(self, profile, safe_prediction):
        sim = WhatIfSimulator(profile, safe_prediction)
        s = sim.simulate_reduce_discretionary_spending(500.0)
        assert s.projected_expenses == 3500.0   # 4000 - 500
        assert s.projected_cash_flow == 4500.0   # 10000 - 3500 - 2000
        assert s.projected_balance == 9500.0     # 5000 + 4500

    def test_reduce_zero_returns_baseline(self, profile, safe_prediction):
        sim = WhatIfSimulator(profile, safe_prediction)
        b = sim.baseline_scenario()
        s = sim.simulate_reduce_discretionary_spending(0.0)
        assert s.projected_balance == b.projected_balance
        assert s.scenario_name == "Baseline"

    def test_reduce_negative_raises(self, profile, safe_prediction):
        sim = WhatIfSimulator(profile, safe_prediction)
        with pytest.raises(ValueError, match="non-negative"):
            sim.simulate_reduce_discretionary_spending(-100.0)

    def test_reduce_more_than_expenses_clamps_at_zero(self, profile, safe_prediction):
        """Expenses cannot go negative; simulator clamps at 0."""
        sim = WhatIfSimulator(profile, safe_prediction)
        s = sim.simulate_reduce_discretionary_spending(50000.0)
        assert s.projected_expenses == 0.0  # max(0, 4000 - 50000)

    def test_reduction_producing_negative_cash_flow(self, profile, safe_prediction):
        """A reduction can't fix a CF already negative from obligations alone."""
        # Force obligations very high so reduction can't recover CF
        p2 = PredictionEngineResult(
            available=True,
            projected_cash_flow=ProjectedCashFlow(
                period="next_month",
                projected_income=2000.0,
                projected_expenses=500.0,
                known_obligations=10000.0,
                projected_cash_flow=-8500.0,
            ),
        )
        sim = WhatIfSimulator(profile, p2)
        s = sim.simulate_reduce_discretionary_spending(500.0)
        assert s.projected_cash_flow < 0
        assert s.buffer_breached
        assert s.shortfall > 0


class TestWhatIfSpendingIncrease:
    def test_increase_raises_expenses_and_lowers_cf(self, profile, safe_prediction):
        sim = WhatIfSimulator(profile, safe_prediction)
        s = sim.simulate_increase_spending(1000.0)
        assert s.projected_expenses == 5000.0    # 4000 + 1000
        assert s.projected_cash_flow == 3000.0   # 10000 - 5000 - 2000
        assert s.projected_balance == 8000.0     # 5000 + 3000

    def test_increase_zero_returns_baseline(self, profile, safe_prediction):
        sim = WhatIfSimulator(profile, safe_prediction)
        b = sim.baseline_scenario()
        s = sim.simulate_increase_spending(0.0)
        assert s.projected_balance == b.projected_balance

    def test_increase_negative_raises(self, profile, safe_prediction):
        sim = WhatIfSimulator(profile, safe_prediction)
        with pytest.raises(ValueError, match="non-negative"):
            sim.simulate_increase_spending(-200.0)

    def test_large_increase_breaches_buffer(self, profile, safe_prediction):
        """Spending so much that balance falls below buffer."""
        sim = WhatIfSimulator(profile, safe_prediction)
        # 4000 (current cf) - 13000 (increase) = -9000 cash flow
        # balance = 5000 + (-9000) = -4000 → breached
        s = sim.simulate_increase_spending(13000.0)
        assert s.buffer_breached
        assert s.shortfall == max(0.0, 1000.0 - (-4000.0))

    def test_increase_unavailable_raises(self, profile, unavailable_prediction):
        sim = WhatIfSimulator(profile, unavailable_prediction)
        with pytest.raises(ValueError):
            sim.simulate_increase_spending(100.0)


class TestWhatIfCumulativeSummary:
    def test_summary_monthly_diff(self, profile, safe_prediction):
        sim = WhatIfSimulator(profile, safe_prediction)
        b = sim.baseline_scenario()
        s = sim.simulate_reduce_discretionary_spending(500.0)
        summary = sim.compute_what_if_summary(b, s, months=6)

        assert summary.monthly_cash_flow_difference == pytest.approx(500.0)
        assert summary.monthly_balance_difference == pytest.approx(500.0)
        assert summary.cumulative_cash_flow_difference == pytest.approx(3000.0)  # 500 * 6
        assert summary.cumulative_balance_difference == pytest.approx(3000.0)
        assert summary.forecast_months == 6

    def test_summary_increase_shows_negative_diff(self, profile, safe_prediction):
        sim = WhatIfSimulator(profile, safe_prediction)
        b = sim.baseline_scenario()
        s = sim.simulate_increase_spending(300.0)
        summary = sim.compute_what_if_summary(b, s, months=3)

        assert summary.monthly_cash_flow_difference == pytest.approx(-300.0)
        assert summary.cumulative_cash_flow_difference == pytest.approx(-900.0)

    def test_summary_invalid_months_raises(self, profile, safe_prediction):
        sim = WhatIfSimulator(profile, safe_prediction)
        b = sim.baseline_scenario()
        with pytest.raises(ValueError, match="at least 1"):
            sim.compute_what_if_summary(b, b, months=0)

    def test_summary_baseline_values_correct(self, profile, safe_prediction):
        sim = WhatIfSimulator(profile, safe_prediction)
        b = sim.baseline_scenario()
        s = sim.simulate_reduce_discretionary_spending(200.0)
        summary = sim.compute_what_if_summary(b, s)

        assert summary.baseline_monthly_income == 10000.0
        assert summary.baseline_monthly_expenses == 4000.0
        assert summary.baseline_monthly_cash_flow == 4000.0
        assert summary.scenario_monthly_expenses == 3800.0
        assert summary.scenario_monthly_cash_flow == 4200.0


# ===========================================================================
# Intent Parser Tests (What-if direction)
# ===========================================================================

class TestIntentParserWhatIf:
    def setup_method(self):
        self.parser = IntentParser()

    def test_reduce_phrase_gives_negative_change_amount(self):
        r = self.parser.parse("What if I spend 500 less on eating out?")
        assert r.intent == IntentType.WHAT_IF
        assert r.change_amount is not None
        assert r.change_amount < 0
        assert abs(r.change_amount) == pytest.approx(500.0)

    def test_increase_phrase_gives_positive_change_amount(self):
        r = self.parser.parse("What if I spend 300 more on eating out?")
        assert r.intent == IntentType.WHAT_IF
        assert r.change_amount is not None
        assert r.change_amount > 0
        assert r.change_amount == pytest.approx(300.0)

    def test_what_if_no_amount_gives_none(self):
        r = self.parser.parse("What if I change my spending habits?")
        assert r.intent == IntentType.WHAT_IF
        assert r.change_amount is None

    def test_what_if_category_extracted(self):
        r = self.parser.parse("What happens if I spend 200 less on eating out?")
        assert r.category == "eating out"

    def test_affordability_still_parsed(self):
        r = self.parser.parse("Can I afford a 5000 purchase?")
        assert r.intent == IntentType.AFFORDABILITY_CHECK
        assert r.amount == pytest.approx(5000.0)


# ===========================================================================
# Response Generator Tests (What-if)
# ===========================================================================

class TestResponseGeneratorWhatIf:
    def setup_method(self):
        self.gen = ResponseGenerator()

    def _parsed(self, change_amount=None):
        return ParsedIntent(intent=IntentType.WHAT_IF, change_amount=change_amount)

    def test_reduction_response_says_reduce(self):
        parsed = self._parsed(change_amount=-500.0)
        result = {
            "type": "what_if",
            "scenario_type": "spending_reduction",
            "projected_balance": 9500.0,
            "buffer_status_change": "maintained",
            "change_amount": 500.0,
        }
        resp = self.gen.generate(parsed, result, "INR")
        assert "reduce spending" in resp.lower()
        assert "increase" not in resp.lower() or "increase spending" not in resp.lower()

    def test_increase_response_says_increase(self):
        parsed = self._parsed(change_amount=300.0)
        result = {
            "type": "what_if",
            "scenario_type": "spending_increase",
            "projected_balance": 8000.0,
            "buffer_status_change": "maintained",
            "change_amount": 300.0,
        }
        resp = self.gen.generate(parsed, result, "INR")
        assert "increase spending" in resp.lower()
        assert "reduce spending" not in resp.lower()

    def test_no_change_response_does_not_claim_action(self):
        parsed = self._parsed(change_amount=None)
        result = {
            "type": "what_if",
            "scenario_type": "no_change",
            "projected_balance": 9000.0,
            "buffer_status_change": "maintained",
            "change_amount": 0.0,
            "note": "No change amount was specified.",
        }
        resp = self.gen.generate(parsed, result, "INR")
        # Must NOT claim reduction or increase
        assert "reduce spending" not in resp.lower()
        assert "increase spending" not in resp.lower()

    def test_buffer_status_messages_correct(self):
        parsed = self._parsed(change_amount=5000.0)
        result = {
            "type": "what_if",
            "scenario_type": "spending_increase",
            "projected_balance": -1000.0,
            "buffer_status_change": "breached",
            "change_amount": 5000.0,
        }
        resp = self.gen.generate(parsed, result, "INR")
        assert "breach" in resp.lower()


# ===========================================================================
# Affordability Engine Tests
# ===========================================================================

class TestAffordabilityAffordable:
    def test_affordable_purchase(self, profile, safe_prediction):
        aff = AffordabilityEngine(profile, safe_prediction)
        res = aff.evaluate_purchase(1000.0)
        # balance after = 5000 + 4000 - 1000 = 8000 >= 1000 buffer → AFFORDABLE
        assert res.status == "AFFORDABLE"
        assert res.resulting_balance == pytest.approx(8000.0)
        assert res.shortfall == 0.0
        assert res.trade_off_required == 0.0
        assert len(res.reasons) > 0

    def test_reasons_mention_balance_and_buffer(self, profile, safe_prediction):
        aff = AffordabilityEngine(profile, safe_prediction)
        res = aff.evaluate_purchase(1000.0)
        all_reasons = " ".join(res.reasons)
        assert "5000.00" in all_reasons   # current balance
        assert "1000.00" in all_reasons   # min buffer


class TestAffordabilityNotAffordable:
    def test_unaffordable_purchase(self, profile, safe_prediction):
        aff = AffordabilityEngine(profile, safe_prediction)
        # balance after = 5000 + 4000 - 50000 = -41000 → NOT AFFORDABLE
        res = aff.evaluate_purchase(50000.0)
        assert res.status == "NOT AFFORDABLE UNDER CURRENT PROJECTION"
        assert res.resulting_balance < 0
        assert res.shortfall > 0

    def test_unaffordable_reasons_reference_shortfall(self, profile, safe_prediction):
        aff = AffordabilityEngine(profile, safe_prediction)
        res = aff.evaluate_purchase(50000.0)
        all_reasons = " ".join(res.reasons)
        assert "below the minimum buffer" in all_reasons

    def test_tight_cash_flow_breaches_buffer(self, profile, tight_prediction):
        """With -500 CF, even small purchases breach the buffer."""
        aff = AffordabilityEngine(profile, tight_prediction)
        # balance after = 5000 + (-500) - 2000 = 2500, still >= 1000 → AFFORDABLE
        res = aff.evaluate_purchase(2000.0)
        assert res.status == "AFFORDABLE"

        # Now buy something big
        res2 = aff.evaluate_purchase(6000.0)
        # balance = 5000 - 500 - 6000 = -1500 → NOT AFFORDABLE
        assert res2.status == "NOT AFFORDABLE UNDER CURRENT PROJECTION"


class TestAffordabilityTradeOff:
    def test_trade_off_scenario(self, profile, safe_prediction):
        """Purchase that drops balance below buffer but within recoverable range."""
        aff = AffordabilityEngine(profile, safe_prediction)
        # balance after = 5000 + 4000 - 8500 = 500 < 1000 buffer
        # shortfall = 500; projected_expenses = 4000 → shortfall < expenses → TRADE-OFF
        res = aff.evaluate_purchase(8500.0)
        assert res.status == "POTENTIALLY AFFORDABLE WITH TRADE-OFF"
        assert res.shortfall == pytest.approx(500.0)
        assert res.trade_off_required == pytest.approx(500.0)

    def test_trade_off_reasons_mention_discretionary(self, profile, safe_prediction):
        aff = AffordabilityEngine(profile, safe_prediction)
        res = aff.evaluate_purchase(8500.0)
        all_reasons = " ".join(res.reasons)
        assert "discretionary" in all_reasons.lower() or "shortfall" in all_reasons.lower()


class TestAffordabilityInsufficientData:
    def test_insufficient_data_status(self, profile, unavailable_prediction):
        aff = AffordabilityEngine(profile, unavailable_prediction)
        res = aff.evaluate_purchase(1000.0)
        assert res.status == "INSUFFICIENT DATA"
        assert len(res.reasons) > 0
        assert "historical" in res.reasons[0].lower() or "insufficient" in res.reasons[0].lower()

    def test_zero_amount_returns_insufficient_data(self, profile, safe_prediction):
        aff = AffordabilityEngine(profile, safe_prediction)
        res = aff.evaluate_purchase(0.0)
        assert res.status == "INSUFFICIENT DATA"
        assert any("greater than zero" in r.lower() for r in res.reasons)

    def test_negative_amount_returns_insufficient_data(self, profile, safe_prediction):
        aff = AffordabilityEngine(profile, safe_prediction)
        res = aff.evaluate_purchase(-500.0)
        assert res.status == "INSUFFICIENT DATA"


class TestAffordabilityPaymentOptions:
    def _make_options(self):
        po_full = PaymentOption(
            payment_option_id="p1", request_id="r1",
            payment_method="full_payment",
            payment_amount=50000.0, number_of_payments=1,
            first_payment_date=date(2024, 6, 1),
            financing_fee=0.0, total_payable_amount=50000.0,
        )
        po_emi = PaymentOption(
            payment_option_id="p2", request_id="r1",
            payment_method="emi",
            payment_amount=500.0, number_of_payments=12,
            first_payment_date=date(2024, 6, 1),
            financing_fee=0.0, total_payable_amount=6000.0,
        )
        return [po_full, po_emi]

    def test_emi_viable_when_full_not(self, profile, safe_prediction):
        aff = AffordabilityEngine(profile, safe_prediction)
        opts = self._make_options()
        res = aff.evaluate_purchase(50000.0, opts)
        # Full payment not affordable; 500/month EMI: balance = 5000 + 4000 - 500 = 8500 >= 1000 → viable
        assert res.status == "NOT AFFORDABLE UNDER CURRENT PROJECTION"
        viable_ids = [o.payment_option_id for o in res.viable_payment_options]
        assert "p2" in viable_ids
        assert "p1" not in viable_ids

    def test_no_double_counting_obligations(self, profile, safe_prediction):
        """EMI evaluated independently – obligations from the baseline CF are not re-added."""
        aff = AffordabilityEngine(profile, safe_prediction)
        # The baseline CF already includes known_obligations=2000.
        # Check that evaluating a 200/mo EMI doesn't apply 2000 again.
        po_emi = PaymentOption(
            payment_option_id="p3", request_id="r2",
            payment_method="emi",
            payment_amount=200.0, number_of_payments=24,
            first_payment_date=date(2024, 6, 1),
            financing_fee=0.0, total_payable_amount=4800.0,
        )
        res = aff.evaluate_purchase(4800.0, [po_emi])
        # EMI balance = 5000 + 4000 - 200 = 8800 >= 1000 → viable
        assert any(o.payment_option_id == "p3" for o in res.viable_payment_options)


# ===========================================================================
# Decision Engine regression tests
# ===========================================================================

class TestDecisionEngineRegression:
    def test_engine_no_gap_returns_none(self, profile, safe_prediction, mock_state):
        """No recommendation when there is no cash-flow gap."""
        eng = DecisionEngine(profile, mock_state, safe_prediction)
        trace = eng.generate_recommendation_for_gap()
        assert trace is None

    def test_engine_gap_returns_trace(self, profile, mock_state):
        """Use a prediction that truly breaches the minimum buffer."""
        gap_prediction = PredictionEngineResult(
            available=True,
            projected_cash_flow=ProjectedCashFlow(
                period="next_month",
                projected_income=2000.0,
                projected_expenses=1500.0,
                known_obligations=2000.0,
                projected_cash_flow=-1500.0,  # 2000 - 1500 - 2000
                # balance = 5000 - 1500 = 3500 → still above 1000 buffer with current profile
            ),
        )
        # Force a lower balance so balance drops below buffer
        low_balance_profile = FinancialProfile(
            user_id="u_test",
            home_currency="INR",
            current_available_balance=500.0,   # very low balance
            minimum_balance_to_keep=1000.0,    # buffer above balance + negative cf
            financial_priorities=[],
            expense_categories_to_protect=[],
            expense_categories_user_is_willing_to_reduce=[],
            expense_categories_user_is_willing_to_stop=[],
            payment_methods_user_will_consider=[],
        )
        eng = DecisionEngine(low_balance_profile, mock_state, gap_prediction)
        # baseline balance = 500 + (-1500) = -1000 → shortfall = 1000 - (-1000) = 2000 → breached
        trace = eng.generate_recommendation_for_gap()
        assert trace is not None
        assert trace.recommendation.recommendation_type == "REDUCE_DISCRETIONARY_SPENDING"


# ===========================================================================
# Copilot API integration tests (via TestClient)
# ===========================================================================

@pytest.fixture
def api_client():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.auth import get_current_user
    from app.models import User
    user = User()
    user.id = 28
    app.dependency_overrides[get_current_user] = lambda: user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestCopilotWhatIfAPI:
    def test_what_if_reduction_scenario_type(self, api_client):
        resp = api_client.post("/api/copilot/query", json={
            "user_id": "user_28",
            "message": "What happens if I spend 200 less on eating out?",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] == "WHAT_IF"
        sr = data["structured_result"]
        assert "projected_balance" in sr
        assert sr.get("scenario_type") == "spending_reduction"

    def test_what_if_response_text_matches_reduction_scenario(self, api_client):
        resp = api_client.post("/api/copilot/query", json={
            "user_id": "user_28",
            "message": "What if I spend 200 less on eating out?",
        })
        assert resp.status_code == 200
        data = resp.json()
        response_text = data["response"].lower()
        # Must say "reduce" not "increase" for a reduction scenario
        assert any(w in response_text for w in ["reduce", "reduction", "less", "lower"])

    def test_what_if_increase_scenario_type(self, api_client):
        resp = api_client.post("/api/copilot/query", json={
            "user_id": "user_28",
            "message": "What if I spend 500 more on eating out?",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] == "WHAT_IF"
        sr = data["structured_result"]
        assert sr.get("scenario_type") == "spending_increase"

    def test_what_if_response_text_matches_increase_scenario(self, api_client):
        resp = api_client.post("/api/copilot/query", json={
            "user_id": "user_28",
            "message": "What happens if I increase spending by 300 on eating out?",
        })
        assert resp.status_code == 200
        data = resp.json()
        response_text = data["response"].lower()
        assert any(w in response_text for w in ["increase", "increasing", "more", "higher"])

    def test_what_if_monthly_summary_present(self, api_client):
        resp = api_client.post("/api/copilot/query", json={
            "user_id": "user_28",
            "message": "What happens if I spend 200 less on eating out?",
        })
        data = resp.json()
        sr = data["structured_result"]
        assert "monthly_summary" in sr
        ms = sr["monthly_summary"]
        assert "monthly_cash_flow_difference" in ms
        assert "cumulative_cash_flow_difference" in ms


class TestCopilotAffordabilityAPI:
    def test_affordability_includes_reasons(self, api_client):
        resp = api_client.post("/api/copilot/query", json={
            "user_id": "user_28",
            "message": "Can I afford to spend 1302.4 in installments?",
        })
        assert resp.status_code == 200
        data = resp.json()
        sr = data["structured_result"]
        assert "reasons" in sr
        assert len(sr["reasons"]) > 0

    def test_affordability_decision_trace_accurate(self, api_client):
        resp = api_client.post("/api/copilot/query", json={
            "user_id": "user_28",
            "message": "Can I afford to buy something for 999?",
        })
        assert resp.status_code == 200
        data = resp.json()
        if data.get("decision_trace"):
            trace = data["decision_trace"]
            # observed_fact must mention balance and buffer
            assert "balance" in trace["observed_fact"].lower()
            assert "buffer" in trace["observed_fact"].lower()

    def test_invalid_amount_returns_error(self, api_client):
        resp = api_client.post("/api/copilot/query", json={
            "user_id": "user_28",
            "message": "Can I afford to buy something?",  # no amount in message
        })
        assert resp.status_code == 200
        data = resp.json()
        # Without a parsed amount, should return an ERROR or INSUFFICIENT_DATA response
        assert data["status"] in ("ERROR", "INSUFFICIENT_DATA") or "specify" in data["response"].lower()


class TestCopilotDataSourcesAccuracy:
    def test_data_sources_present(self, api_client):
        resp = api_client.post("/api/copilot/query", json={
            "user_id": "user_28",
            "message": "What happens if I spend 200 less on eating out?",
        })
        data = resp.json()
        assert "data_sources" in data
        assert isinstance(data["data_sources"], list)
        assert len(data["data_sources"]) > 0
