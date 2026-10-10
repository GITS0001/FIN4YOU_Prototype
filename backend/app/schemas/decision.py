from pydantic import BaseModel
from typing import Optional, List, Dict
from app.schemas.financial import FinancialState, PredictionEngineResult, PaymentOption


class ScenarioResult(BaseModel):
    scenario_name: str
    projected_income: float
    projected_expenses: float
    known_obligations: float
    projected_cash_flow: float
    projected_balance: float
    shortfall: float
    buffer_breached: bool


class WhatIfSummary(BaseModel):
    """
    Multi-month deterministic summary comparing baseline vs. a what-if scenario.
    All monetary values are in the user's home currency.
    """
    baseline_monthly_income: float
    baseline_monthly_expenses: float
    baseline_monthly_cash_flow: float
    scenario_monthly_income: float
    scenario_monthly_expenses: float
    scenario_monthly_cash_flow: float
    monthly_cash_flow_difference: float
    monthly_balance_difference: float
    cumulative_cash_flow_difference: float
    cumulative_balance_difference: float
    forecast_months: int


class ExpectedImpact(BaseModel):
    cash_flow_difference: float
    balance_difference: float
    buffer_status_change: str  # "maintained", "breached", "restored", etc.


class AffordabilityResult(BaseModel):
    """
    Result of an affordability evaluation.

    status values
    -------------
    * "AFFORDABLE"
    * "POTENTIALLY AFFORDABLE WITH TRADE-OFF"
    * "NOT AFFORDABLE UNDER CURRENT PROJECTION"
    * "INSUFFICIENT DATA"
    """
    status: str
    proposed_expense_amount: float
    resulting_balance: float
    shortfall: float
    viable_payment_options: List[PaymentOption] = []
    trade_off_required: float = 0.0   # amount of discretionary spending that must be cut
    reasons: List[str] = []           # auditable explanations of the decision


class Recommendation(BaseModel):
    recommendation_type: str
    actionable_text: str
    expected_impact: ExpectedImpact
    confidence_level: str   # "HIGH", "MEDIUM", "LOW"
    confidence_reason: str


class DecisionTrace(BaseModel):
    observed_fact: str
    calculation: str
    prediction: str
    simulation: str
    recommendation: Recommendation
    supporting_data: Dict[str, float]
