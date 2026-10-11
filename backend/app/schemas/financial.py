from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
import pandas as pd

class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    event_type: str
    description: str
    category: str
    direction: str
    amount: float
    currency: str
    event_date: date
    settlement_date: Optional[date] = None
    status: str
    flexibility: str
    ml_confidence: Optional[float] = None
    ml_status: Optional[str] = None
    ml_confidence_level: Optional[str] = None

    @field_validator('amount')
    @classmethod
    def amount_must_be_positive(cls, v):
        if v < 0:
            return abs(v)  # Normalize to positive, direction dictates if it's debit/credit
        return v

class FinancialProfile(BaseModel):
    user_id: str
    home_currency: str
    current_available_balance: float
    minimum_balance_to_keep: float
    financial_priorities: List[str]
    expense_categories_to_protect: List[str]
    expense_categories_user_is_willing_to_reduce: List[str]
    expense_categories_user_is_willing_to_stop: List[str]
    payment_methods_user_will_consider: List[str]
    max_installment_months: Optional[float] = None

    @field_validator('max_installment_months', mode='before')
    @classmethod
    def convert_nan_to_none(cls, v):
        import math
        if isinstance(v, float) and math.isnan(v):
            return None
        return v

    @field_validator(
        'financial_priorities', 
        'expense_categories_to_protect', 
        'expense_categories_user_is_willing_to_reduce', 
        'expense_categories_user_is_willing_to_stop',
        'payment_methods_user_will_consider',
        mode='before'
    )
    @classmethod
    def split_pipe_separated(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            return [x.strip() for x in v.split('|') if x.strip()]
        if pd.isna(v) if 'pd' in globals() else v is None: # handle nan if called directly from df
            return []
        return v or []

class CopilotRequest(BaseModel):
    request_id: str
    user_id: str
    request_date: date
    request_type: str
    requested_amount: float
    desired_completion_date: date
    allows_partial_payment: bool
    request_text: str

class PaymentOption(BaseModel):
    payment_option_id: str
    request_id: str
    payment_method: str
    payment_amount: float
    number_of_payments: int
    first_payment_date: date
    payment_frequency_days: Optional[float] = None
    financing_fee: float
    total_payable_amount: float

class CategoryPrediction(BaseModel):
    transaction_id: str
    category: str
    confidence: float
    status: str = "classified"
    confidence_level: str = "high"

class AnomalySignal(BaseModel):
    transaction_id: str
    is_anomaly: bool
    anomaly_score: float
    reason: str
    severity: str = "low"
    detection_method: str = "z_score"
    confidence: float = 0.95

class CategorySpending(BaseModel):
    category: str
    total_amount: float

class FinancialState(BaseModel):
    user_id: str
    income: float
    expenses: float
    savings: float
    savings_rate: float
    expense_ratio: float
    essential_expenses: float
    discretionary_expenses: float
    recurring_obligations: float
    emi_burden: float
    cash_flow: float
    category_spending: List[CategorySpending]
    anomalies: List[AnomalySignal]
    data_quality_confidence: float
    available_balance: float = 0.0
    minimum_reserve: float = 18000.0
    total_observed_income: float = 0.0
    total_observed_expenses: float = 0.0
    total_fixed_obligations: float = 0.0

class ForecastEvaluation(BaseModel):
    mae: Optional[float] = None
    rmse: Optional[float] = None

class ForecastResult(BaseModel):
    metric: str
    prediction: float
    confidence: float
    uncertainty: float
    horizon: str
    model: str
    evidence: List[str]
    evaluation: Optional[ForecastEvaluation] = None

class FutureObligation(BaseModel):
    description: str
    category: str
    expected_amount: float
    expected_period: str

class ProjectedCashFlow(BaseModel):
    period: str
    projected_income: float
    projected_expenses: float
    known_obligations: float
    projected_cash_flow: float

class CashFlowGap(BaseModel):
    detected: bool
    period: str
    projected_balance: float
    required_buffer: float
    shortfall: float

class PredictionEngineResult(BaseModel):
    available: bool
    reason: Optional[str] = None
    forecasts: List[ForecastResult] = []
    obligations: List[FutureObligation] = []
    projected_cash_flow: Optional[ProjectedCashFlow] = None
    gap_detection: Optional[CashFlowGap] = None
    projected_cash_flows: List[ProjectedCashFlow] = []
    gap_detections: List[CashFlowGap] = []
class MonthlyValueChange(BaseModel):
    current: float
    previous: float
    change: float

class CategoryChange(BaseModel):
    category: str
    current: float
    previous: float
    change: float

class RecurringObligationItem(BaseModel):
    description: str
    amount: float

class MonthlyStatementResponse(BaseModel):
    month: str
    income: MonthlyValueChange
    expenses: MonthlyValueChange
    savings: MonthlyValueChange
    cash_flow: MonthlyValueChange
    category_changes: List[CategoryChange]
    recurring_obligations: List[RecurringObligationItem]
    anomalies: List[Dict[str, Any]]
    forecast: Dict[str, Any]
    observations: List[str]
    recommendations: List[str]

class FinancialOverrides(BaseModel):
    income_override: Optional[float] = None
    balance_override: Optional[float] = None
    minimum_buffer_override: Optional[float] = None
    expenses_override: Optional[float] = None
    
class RiskStatus(BaseModel):
    buffer_status: str
    cash_flow_status: str

class GlobalFinancialState(BaseModel):
    user_id: str
    currency: str
    baseline: FinancialProfile
    current_state: FinancialState
    prediction: PredictionEngineResult
    risk: RiskStatus
    confidence: float
    data_sources: List[str]

# Re-export planner and probabilistic forecasting schemas
from app.schemas.planner import (
    DistributionSummary,
    ProbabilisticForecastPeriod,
    ForecastEvaluationMetrics,
    ProbabilisticForecastRequest,
    ProbabilisticForecastResponse,
    ActionType,
    PeriodAction,
    FinancialGoal,
    GoalFeasibilityStatus,
    PeriodPlanProjection,
    CandidateActionPlan,
    EvaluatedPlanResult,
    PlanEvaluationRequest,
    PlanEvaluationResponse,
)
