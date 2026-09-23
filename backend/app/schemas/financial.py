from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
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

class AnomalySignal(BaseModel):
    transaction_id: str
    is_anomaly: bool
    anomaly_score: float
    reason: str

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

class ForecastEvaluation(BaseModel):
    mae: Optional[float] = None
    rmse: Optional[float] = None

class ForecastResult(BaseModel):
    target: str
    period: str
    predicted_value: float
    model: str
    uncertainty: float
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
