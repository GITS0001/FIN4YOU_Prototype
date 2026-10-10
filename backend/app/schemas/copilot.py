from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from app.schemas.decision import DecisionTrace

class IntentType(str, Enum):
    GREETING = "GREETING"
    GENERAL_FINANCE = "GENERAL_FINANCE"
    SAVING_PLAN = "SAVING_PLAN"
    BUDGETING = "BUDGETING"
    EXPENSE_ANALYSIS = "EXPENSE_ANALYSIS"
    BALANCE_QUERY = "BALANCE_QUERY"
    CASH_FLOW_QUERY = "CASH_FLOW_QUERY"
    INCOME_QUERY = "INCOME_QUERY"
    EXPENSE_QUERY = "EXPENSE_QUERY"
    FINANCIAL_FORECAST = "FINANCIAL_FORECAST"
    CASH_FLOW_FORECAST = "CASH_FLOW_FORECAST"
    CLARIFICATION = "CLARIFICATION"
    GENERAL_CONVERSATION = "GENERAL_CONVERSATION"
    AFFORDABILITY_CHECK = "AFFORDABILITY_CHECK"
    WHAT_IF = "WHAT_IF"
    RECOMMENDATION = "RECOMMENDATION"
    PAYMENT_OPTION_ANALYSIS = "PAYMENT_OPTION_ANALYSIS"
    SPENDING_ANALYSIS = "SPENDING_ANALYSIS"
    FINANCIAL_SUMMARY = "FINANCIAL_SUMMARY"
    UNKNOWN = "UNKNOWN"

class ParsedIntent(BaseModel):
    intent: IntentType
    amount: Optional[float] = None
    category: Optional[str] = None
    payment_option_id: Optional[str] = None
    change_amount: Optional[float] = None

class CopilotRequest(BaseModel):
    user_id: Optional[str] = None
    message: str

class ActionLink(BaseModel):
    label: str
    url: str

class CopilotResponse(BaseModel):
    intent: IntentType
    response: str
    decision_trace: Optional[DecisionTrace] = None
    structured_result: Optional[Dict[str, Any]] = None
    confidence: str # e.g. "HIGH", "UNKNOWN"
    status: str # "SUCCESS", "UNSUPPORTED", "INSUFFICIENT_DATA", "ERROR"
    data_sources: List[str] = []
    action_links: List[ActionLink] = []
