import pytest
from app.copilot.intent_parser import IntentParser
from app.schemas.copilot import IntentType
from app.copilot.provider import BaseLLMProvider, LLMResult

class DummyLLMProvider(BaseLLMProvider):
    @property
    def name(self) -> str: return "dummy"
    @property
    def model_name(self) -> str: return "dummy"
    def is_available(self) -> bool: return False
    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.2, max_tokens: int = 800) -> LLMResult:
        return LLMResult(content="", provider_name="dummy", model_name="dummy")

@pytest.fixture
def deterministic_parser():
    return IntentParser(provider=DummyLLMProvider())

class TestIntentParsingAdversarial:
    def test_what_if_spend_less(self, deterministic_parser):
        parsed = deterministic_parser.parse("I want to spend ₹2,000 less.")
        assert parsed.intent == IntentType.WHAT_IF
        assert parsed.change_amount == -2000.0
        
    def test_what_if_spend_more(self, deterministic_parser):
        parsed = deterministic_parser.parse("Increase my spending by ₹2,000.")
        assert parsed.intent == IntentType.WHAT_IF
        assert parsed.change_amount == 2000.0
        
    def test_income_drop_percentage(self, deterministic_parser):
        parsed = deterministic_parser.parse("My income will drop by 20%.")
        assert parsed.intent == IntentType.WHAT_IF
        assert parsed.income_shock_percentage == -0.2
        assert parsed.change_amount is None # Should distinguish % from amount
        
    def test_earn_more(self, deterministic_parser):
        parsed = deterministic_parser.parse("What if I earn ₹5,000 more each month?")
        # Schema does not support absolute income changes safely, returns UNKNOWN instead of hallucinating.
        assert parsed.intent == IntentType.UNKNOWN

    def test_ambiguous_or_missing_amount(self, deterministic_parser):
        parsed = deterministic_parser.parse("What if I spend less?")
        assert parsed.intent == IntentType.WHAT_IF
        assert parsed.change_amount is None

    def test_zero_amount(self, deterministic_parser):
        parsed = deterministic_parser.parse("What if I increase my spending by 0?")
        assert parsed.intent == IntentType.WHAT_IF
        assert parsed.change_amount is None 


from app.schemas.financial import FinancialProfile, Transaction, PredictionEngineResult, ProjectedCashFlow
from app.financial.state import FinancialStateEngine
from app.decision.affordability import AffordabilityEngine
from app.decision.simulation import WhatIfSimulator
from app.schemas.decision import AffordabilityResult

class TestFinancialEngineAdversarial:
    def _profile(self, bal: float, min_buf: float) -> FinancialProfile:
        return FinancialProfile(
            user_id="u1", 
            current_available_balance=bal, 
            minimum_balance_to_keep=min_buf,
            home_currency="INR",
            financial_priorities=[],
            expense_categories_to_protect=[],
            expense_categories_user_is_willing_to_reduce=[],
            expense_categories_user_is_willing_to_stop=[],
            payment_methods_user_will_consider=[]
        )

    def test_zero_and_negative_balances(self):
        profile = self._profile(0.0, 100.0)
        baseline_pred = PredictionEngineResult(
            available=True,
            projected_cash_flow=ProjectedCashFlow(period="2023-11", projected_income=1000.0, projected_expenses=500.0, known_obligations=0.0, projected_cash_flow=500.0)
        )
        engine = AffordabilityEngine(profile, baseline_pred)
        # Resulting balance = 0 + 500 - 200 = 300 >= 100
        res = engine.evaluate_purchase(200.0)
        assert res.status == "AFFORDABLE"
        
        # Negative balance
        profile.current_available_balance = -50.0
        # Resulting balance = -50 + 500 - 200 = 250 >= 100
        res2 = engine.evaluate_purchase(200.0)
        assert res2.status == "AFFORDABLE"

    def test_affordability_threshold_exact(self):
        profile = self._profile(100.0, 100.0)
        baseline_pred = PredictionEngineResult(
            available=True,
            projected_cash_flow=ProjectedCashFlow(period="2023-11", projected_income=500.0, projected_expenses=200.0, known_obligations=0.0, projected_cash_flow=300.0)
        )
        engine = AffordabilityEngine(profile, baseline_pred)
        # resulting = 100 + 300 - 300 = 100 == min_buffer
        res = engine.evaluate_purchase(300.0)
        assert res.status == "AFFORDABLE"

    def test_breach_reserve_by_1(self):
        profile = self._profile(100.0, 100.0)
        baseline_pred = PredictionEngineResult(
            available=True,
            projected_cash_flow=ProjectedCashFlow(period="2023-11", projected_income=500.0, projected_expenses=200.0, known_obligations=0.0, projected_cash_flow=300.0)
        )
        engine = AffordabilityEngine(profile, baseline_pred)
        # resulting = 100 + 300 - 301 = 99
        res = engine.evaluate_purchase(301.0)
        assert res.status == "POTENTIALLY AFFORDABLE WITH TRADE-OFF"
        assert res.shortfall == 1.0

    def test_no_transaction_history(self):
        engine = FinancialStateEngine(user_id="u1")
        state = engine.calculate_state([])
        assert state.income == 0.0
        assert state.expenses == 0.0
        assert state.cash_flow == 0.0

    def test_refunds_larger_than_category_spending(self):
        engine = FinancialStateEngine(user_id="u1")
        txns = [
            Transaction(transaction_id="1", user_id="u1", description="desc", event_date="2023-01-01", amount=50.0, direction="debit", event_type="purchase", category="shopping", currency="INR", status="completed", flexibility="variable"),
            Transaction(transaction_id="2", user_id="u1", description="desc", event_date="2023-01-02", amount=150.0, direction="credit", event_type="refund", category="shopping", currency="INR", status="completed", flexibility="variable"),
        ]
        state = engine.calculate_state(txns)
        # Expenses should be 50 - 150 = -100
        assert state.expenses == -100.0
        # Category spending for shopping should be -100
        shop_cat = next((c for c in state.category_spending if c.category == "shopping"), None)
        assert shop_cat is not None
        assert shop_cat.total_amount == -100.0

    def test_zero_and_negative_simulation_horizons(self):
        profile = self._profile(100.0, 100.0)
        baseline_pred = PredictionEngineResult(
            available=True,
            projected_cash_flow=ProjectedCashFlow(period="2023-11", projected_income=1000.0, projected_expenses=500.0, known_obligations=0.0, projected_cash_flow=500.0)
        )
        sim = WhatIfSimulator(profile, baseline_pred)
        base = sim.baseline_scenario()
        scen = sim.simulate_increase_spending(100.0)
        
        with pytest.raises(ValueError):
            sim.compute_what_if_summary(base, scen, months=0)
            
        with pytest.raises(ValueError):
            sim.compute_what_if_summary(base, scen, months=-5)

    def test_large_values_rounding(self):
        profile = self._profile(1.0, 0.0)
        baseline_pred = PredictionEngineResult(
            available=True,
            projected_cash_flow=ProjectedCashFlow(period="2023-11", projected_income=999999999999.99, projected_expenses=0.01, known_obligations=0.0, projected_cash_flow=999999999999.98)
        )
        engine = AffordabilityEngine(profile, baseline_pred)
        res = engine.evaluate_purchase(999999999999.98)
        assert res.status == "AFFORDABLE"
        assert res.resulting_balance == 1.0
