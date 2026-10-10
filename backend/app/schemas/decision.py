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

class ExpectedImpact(BaseModel):
    cash_flow_difference: float
    balance_difference: float
    buffer_status_change: str # e.g., "maintained", "breached", "restored"

class AffordabilityResult(BaseModel):
    status: str # "AFFORDABLE", "POTENTIALLY AFFORDABLE WITH TRADE-OFF", "NOT AFFORDABLE UNDER CURRENT PROJECTION", "INSUFFICIENT DATA"
    proposed_expense_amount: float
    resulting_balance: float
    shortfall: float
    viable_payment_options: List[PaymentOption] = []
    trade_off_required: float = 0.0 # Amount of spending that needs to be reduced

class Recommendation(BaseModel):
    recommendation_type: str
    actionable_text: str
    expected_impact: ExpectedImpact
    confidence_level: str # "HIGH", "MEDIUM", "LOW"
    confidence_reason: str

class DecisionTrace(BaseModel):
    observed_fact: str
    calculation: str
    prediction: str
    simulation: str
    recommendation: Recommendation
    supporting_data: Dict[str, float]
