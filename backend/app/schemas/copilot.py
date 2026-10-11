from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from app.schemas.decision import DecisionTrace

class IntentType(str, Enum):
    FINANCIAL_SUMMARY = "FINANCIAL_SUMMARY"
    SPENDING_ANALYSIS = "SPENDING_ANALYSIS"
    CASH_FLOW_FORECAST = "CASH_FLOW_FORECAST"
    AFFORDABILITY_CHECK = "AFFORDABILITY_CHECK"
    WHAT_IF = "WHAT_IF"
    RECOMMENDATION = "RECOMMENDATION"
    PAYMENT_OPTION_ANALYSIS = "PAYMENT_OPTION_ANALYSIS"
    PLAN_EVALUATION = "PLAN_EVALUATION"
    GOAL_FEASIBILITY = "GOAL_FEASIBILITY"
    MISSING_DATA_CLARIFICATION = "MISSING_DATA_CLARIFICATION"
    UNKNOWN = "UNKNOWN"

class ParsedIntent(BaseModel):
    intent: IntentType
    amount: Optional[float] = None
    category: Optional[str] = None
    merchant: Optional[str] = None
    payment_option_id: Optional[str] = None
    change_amount: Optional[float] = None
    income_shock_percentage: Optional[float] = 0.0
    unexpected_expense: Optional[float] = 0.0
    horizon_months: Optional[int] = None
    target_goal_amount: Optional[float] = None
    target_goal_months: Optional[int] = None
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    missing_fields: Optional[List[str]] = None
    stated_balance: Optional[float] = None
    stated_income: Optional[float] = None
    stated_expenses: Optional[float] = None
    stated_buffer: Optional[float] = None
    is_annual: Optional[bool] = False
    item_description: Optional[str] = None

class CopilotRequest(BaseModel):
    user_id: Optional[str] = None
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = None

class ActionLink(BaseModel):
    label: str
    url: str

class CopilotResponse(BaseModel):
    intent: IntentType
    response: str
    direct_answer: Optional[str] = None
    decision_trace: Optional[DecisionTrace] = None
    structured_result: Optional[Dict[str, Any]] = None
    confidence: str # e.g. "HIGH", "MEDIUM", "UNKNOWN"
    status: str # "SUCCESS", "UNSUPPORTED", "INSUFFICIENT_DATA", "ERROR"
    data_sources: List[str] = []
    action_links: List[ActionLink] = []
    observed_facts: List[str] = Field(default_factory=list)
    forecast_details: Optional[Dict[str, Any]] = None
    recommendations: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    trade_offs: List[str] = Field(default_factory=list)
    llm_provider: Optional[str] = None
