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
    UNKNOWN = "UNKNOWN"

class ParsedIntent(BaseModel):
    intent: IntentType
    amount: Optional[float] = None
    category: Optional[str] = None
    payment_option_id: Optional[str] = None
    change_amount: Optional[float] = None

class CopilotRequest(BaseModel):
    user_id: str
    message: str

class CopilotResponse(BaseModel):
    intent: IntentType
    response: str
    decision_trace: Optional[DecisionTrace] = None
    structured_result: Optional[Dict[str, Any]] = None
    confidence: str # e.g. "HIGH", "UNKNOWN"
    status: str # "SUCCESS", "UNSUPPORTED", "INSUFFICIENT_DATA", "ERROR"
    data_sources: List[str] = []
