from typing import List, Dict, Optional
from app.schemas.financial import FinancialState, PredictionEngineResult, FinancialProfile
from app.schemas.decision import DecisionTrace, Recommendation, ScenarioResult, ExpectedImpact
from app.decision.simulation import WhatIfSimulator
from app.decision.impact import ImpactEngine

class DecisionEngine:
    """
    Ties together the simulation and impact engines to produce actionable recommendations
    and a fully traceable DecisionTrace.
    """
    def __init__(self, profile: FinancialProfile, state: FinancialState, prediction: PredictionEngineResult):
        self.profile = profile
        self.state = state
        self.prediction = prediction
        self.simulator = WhatIfSimulator(profile, prediction)

    def generate_recommendation_for_gap(self) -> Optional[DecisionTrace]:
        """
        Generates a recommendation if the baseline has a cash flow gap.
        """
        if not self.prediction.available:
            return None
        
        baseline_scenario = self.simulator.baseline_scenario()
        if not baseline_scenario.buffer_breached:
            return None # No gap to fix

        shortfall = baseline_scenario.shortfall
        current_discretionary = self.prediction.projected_cash_flow.projected_expenses
        
        if current_discretionary <= 0:
            return None # Cannot reduce discretionary if it's already 0

        # Try to reduce discretionary spending by exactly the shortfall, or up to 50% max.
        max_reduction = current_discretionary * 0.5
        reduction_amount = min(shortfall, max_reduction)
        
        scenario = self.simulator.simulate_reduce_discretionary_spending(reduction_amount)
        impact = ImpactEngine.calculate_impact(baseline_scenario, scenario)
        
        if impact.buffer_status_change == "restored":
            rec_text = f"Reduce discretionary spending by {reduction_amount:.2f} next month to maintain your minimum balance."
        else:
            rec_text = f"Reduce discretionary spending by {reduction_amount:.2f} to minimize the buffer breach."
            
        recommendation = Recommendation(
            recommendation_type="REDUCE_DISCRETIONARY_SPENDING",
            actionable_text=rec_text,
            expected_impact=impact,
            confidence_level="HIGH" if len(self.state.anomalies) < 3 else "MEDIUM", # Simple heuristic
            confidence_reason="Based on historical projection and mathematical simulation."
        )

        return DecisionTrace(
            observed_fact=f"Your historical discretionary spending drives a projected variable expense of {current_discretionary:.2f}.",
            calculation=f"Shortfall calculated at {shortfall:.2f} below the {self.profile.minimum_balance_to_keep} threshold.",
            prediction=f"Projected balance next month is {baseline_scenario.projected_balance:.2f} without changes.",
            simulation=f"If you reduce spending by {reduction_amount:.2f}, projected balance becomes {scenario.projected_balance:.2f}.",
            recommendation=recommendation,
            supporting_data={"shortfall": shortfall, "suggested_reduction": reduction_amount}
        )
