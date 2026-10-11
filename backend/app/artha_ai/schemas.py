from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class CalculationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    UNSUPPORTED = "UNSUPPORTED"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


class FinancialEvidenceItem(BaseModel):
    category: str
    amount: float
    currency: str = "INR"
    period: Optional[str] = None
    is_verified: bool = True
    source: str = "financial_events"


class ForecastContext(BaseModel):
    is_available: bool = True
    projected_income: Optional[float] = None
    projected_expenses: Optional[float] = None
    known_obligations: Optional[float] = None
    projected_cash_flow: Optional[float] = None
    projected_balance: Optional[float] = None
    buffer_breached: Optional[bool] = None
    assumptions: List[str] = Field(default_factory=list)


class ScenarioResultsContext(BaseModel):
    scenario_name: str
    scenario_type: str  # "spending_reduction", "spending_increase", "no_change"
    change_amount: float
    baseline_balance: float
    scenario_balance: float
    cash_flow_difference: float
    buffer_status_change: str  # "maintained", "breached", "restored", etc.
    buffer_breached: bool


class RecommendationContext(BaseModel):
    recommendation_type: str
    actionable_text: str
    confidence_level: str  # "HIGH", "MEDIUM", "LOW"
    confidence_reason: str
    observed_fact: Optional[str] = None
    calculation: Optional[str] = None
    prediction: Optional[str] = None
    simulation: Optional[str] = None


class SourceReference(BaseModel):
    doc_id: str
    title: str
    section: Optional[str] = None
    snippet: str
    relevance_score: float = 1.0


class ArthaFinancialContextContract(BaseModel):
    """
    Standardized, privacy-preserving contract for financial data
    supplied to the Artha AI LLM.
    Strictly decouples calculation logic from LLM explanation.
    """
    request_id: str
    user_id: str
    currency: str = "INR"
    intent: str
    financial_evidence: List[FinancialEvidenceItem] = Field(default_factory=list)
    calculated_results: Dict[str, Any] = Field(default_factory=dict)
    forecast: Optional[ForecastContext] = None
    scenario_results: Optional[ScenarioResultsContext] = None
    existing_recommendation: Optional[RecommendationContext] = None
    source_references: List[SourceReference] = Field(default_factory=list)
    missing_inputs: List[str] = Field(default_factory=list)
    calculation_status: CalculationStatus = CalculationStatus.SUCCESS
    data_freshness_timestamp: Optional[str] = None


class ArthaInferenceRequest(BaseModel):
    user_message: str
    context: ArthaFinancialContextContract
    stream: bool = False


class ValidationResult(BaseModel):
    is_valid: bool
    detected_numbers: List[float] = Field(default_factory=list)
    unsupported_numbers: List[float] = Field(default_factory=list)
    currency_mismatches: List[str] = Field(default_factory=list)
    error_reasons: List[str] = Field(default_factory=list)
    repaired: bool = False


class ArthaInferenceResponse(BaseModel):
    text: str
    intent: str
    grounded: bool = True
    model_used: str
    latency_ms: float = 0.0
    validation: ValidationResult
    fallback_used: bool = False
    source_references: List[SourceReference] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)
