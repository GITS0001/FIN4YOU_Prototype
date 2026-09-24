from app.schemas.financial import FinancialProfile, PredictionEngineResult
from app.schemas.decision import ScenarioResult

class WhatIfSimulator:
    """
    Deterministic What-If Simulation Engine.
    Creates scenario results by applying deterministic adjustments to the baseline PredictionEngineResult.
    """
    def __init__(self, profile: FinancialProfile, baseline_prediction: PredictionEngineResult):
        self.profile = profile
        self.baseline = baseline_prediction

    def _get_baseline_cash_flow(self):
        return self.baseline.projected_cash_flow

    def _calculate_scenario(self, name: str, adj_income: float, adj_expenses: float, adj_obligations: float) -> ScenarioResult:
        baseline_cf = self._get_baseline_cash_flow()
        
        # New components
        new_income = max(0.0, baseline_cf.projected_income + adj_income)
        new_expenses = max(0.0, baseline_cf.projected_expenses + adj_expenses)
        new_obligations = max(0.0, baseline_cf.known_obligations + adj_obligations)
        
        new_cash_flow = new_income - new_expenses - new_obligations
        new_balance = self.profile.current_available_balance + new_cash_flow
        
        shortfall = max(0.0, self.profile.minimum_balance_to_keep - new_balance)
        buffer_breached = shortfall > 0
        
        return ScenarioResult(
            scenario_name=name,
            projected_income=new_income,
            projected_expenses=new_expenses,
            known_obligations=new_obligations,
            projected_cash_flow=new_cash_flow,
            projected_balance=new_balance,
            shortfall=shortfall,
            buffer_breached=buffer_breached
        )

    def baseline_scenario(self) -> ScenarioResult:
        if not self.baseline.available:
             raise ValueError("Baseline is not available")
        return self._calculate_scenario("Baseline", 0.0, 0.0, 0.0)

    def simulate_reduce_discretionary_spending(self, reduction_amount: float) -> ScenarioResult:
        if not self.baseline.available:
            raise ValueError("Baseline is not available")
        # Reduction amount should be positive, meaning we reduce expenses
        # e.g., adj_expenses = -reduction_amount
        return self._calculate_scenario(f"Reduce Discretionary by {reduction_amount}", 0.0, -reduction_amount, 0.0)

    def simulate_add_obligation(self, amount: float) -> ScenarioResult:
        if not self.baseline.available:
            raise ValueError("Baseline is not available")
        return self._calculate_scenario(f"Add Obligation of {amount}", 0.0, 0.0, amount)

    def simulate_reduce_discretionary_percentage(self, percentage: float) -> ScenarioResult:
        if not self.baseline.available:
            raise ValueError("Baseline is not available")
        if percentage < 0 or percentage > 1:
            raise ValueError("Percentage must be between 0 and 1")
        
        current_expenses = self._get_baseline_cash_flow().projected_expenses
        reduction_amount = current_expenses * percentage
        return self._calculate_scenario(f"Reduce Discretionary by {percentage*100}%", 0.0, -reduction_amount, 0.0)
