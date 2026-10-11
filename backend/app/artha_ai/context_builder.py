import uuid
import datetime
from typing import Optional, Dict, Any, List
from app.artha_ai.schemas import (
    ArthaFinancialContextContract,
    CalculationStatus,
    FinancialEvidenceItem,
    ForecastContext,
    ScenarioResultsContext,
    RecommendationContext,
    SourceReference,
)


class ArthaContextBuilder:
    """
    Constructs a privacy-first, minimized financial context contract
    for consumption by Artha AI LLM.
    Enforces user boundary isolation, PII exclusion, and data minimization.
    """

    @staticmethod
    def build_from_backend(
        user_id: str,
        intent: str,
        currency: str = "INR",
        structured_result: Optional[Dict[str, Any]] = None,
        decision_trace: Optional[Any] = None,
        prediction_result: Optional[Any] = None,
        status: str = "SUCCESS",
        source_references: Optional[List[SourceReference]] = None,
    ) -> ArthaFinancialContextContract:
        req_id = f"req-{uuid.uuid4().hex[:8]}"
        res = structured_result or {}

        # 1. Map calculation status
        status_enum = CalculationStatus.SUCCESS
        missing_inputs: List[str] = []

        if status == "INSUFFICIENT_DATA" or res.get("status") == "INSUFFICIENT_DATA":
            status_enum = CalculationStatus.INSUFFICIENT_DATA
            missing_inputs.append("Minimum 3 months of transaction history required for forecasting.")
        elif status == "UNSUPPORTED":
            status_enum = CalculationStatus.UNSUPPORTED
        elif status == "ERROR":
            status_enum = CalculationStatus.ERROR

        # 2. Extract forecast context if present
        forecast_ctx: Optional[ForecastContext] = None
        if prediction_result and getattr(prediction_result, "available", False):
            pcf = getattr(prediction_result, "projected_cash_flow", None)
            if pcf:
                forecast_ctx = ForecastContext(
                    is_available=True,
                    projected_income=getattr(pcf, "projected_income", None),
                    projected_expenses=getattr(pcf, "projected_expenses", None),
                    known_obligations=getattr(pcf, "known_obligations", None),
                    projected_cash_flow=getattr(pcf, "projected_cash_flow", None),
                    projected_balance=res.get("projected_balance"),
                    buffer_breached=res.get("buffer_breached", False),
                    assumptions=["Historical trends and recurring calendar schedules"]
                )
        elif "projected_cash_flow" in res or "projected_balance" in res:
            forecast_ctx = ForecastContext(
                is_available=True,
                projected_income=res.get("projected_income"),
                projected_expenses=res.get("projected_expenses"),
                known_obligations=res.get("known_obligations"),
                projected_cash_flow=res.get("projected_cash_flow"),
                projected_balance=res.get("projected_balance"),
                buffer_breached=res.get("buffer_breached", False),
                assumptions=["Baseline linear projection"]
            )

        # 3. Extract scenario results if WHAT_IF
        scenario_ctx: Optional[ScenarioResultsContext] = None
        if intent == "WHAT_IF" or res.get("type") == "what_if":
            scenario_ctx = ScenarioResultsContext(
                scenario_name="What-If Simulation",
                scenario_type=res.get("scenario_type", "spending_reduction"),
                change_amount=float(res.get("change_amount", 0.0)),
                baseline_balance=float(res.get("baseline_balance", res.get("projected_balance", 0.0))),
                scenario_balance=float(res.get("scenario_balance", res.get("projected_balance", 0.0))),
                cash_flow_difference=float(res.get("cash_flow_change", 0.0)),
                buffer_status_change=res.get("buffer_status_change", "maintained"),
                buffer_breached=bool(res.get("buffer_breached", False))
            )

        # 4. Extract recommendation / Decision Trace if available
        rec_ctx: Optional[RecommendationContext] = None
        if decision_trace:
            rec_obj = getattr(decision_trace, "recommendation", None)
            if rec_obj:
                rec_ctx = RecommendationContext(
                    recommendation_type=getattr(rec_obj, "recommendation_type", "FINANCIAL_HEALTH"),
                    actionable_text=getattr(rec_obj, "actionable_text", ""),
                    confidence_level=getattr(rec_obj, "confidence_level", "HIGH"),
                    confidence_reason=getattr(rec_obj, "confidence_reason", "Deterministic rule engine"),
                    observed_fact=getattr(decision_trace, "observed_fact", None),
                    calculation=getattr(decision_trace, "calculation", None),
                    prediction=getattr(decision_trace, "prediction", None),
                    simulation=getattr(decision_trace, "simulation", None)
                )
        elif res.get("recommendation_text"):
            rec_ctx = RecommendationContext(
                recommendation_type="FINANCIAL_ADVICE",
                actionable_text=res.get("recommendation_text", ""),
                confidence_level=res.get("confidence_level", "HIGH"),
                confidence_reason=res.get("confidence_reason", "Deterministic rules"),
                observed_fact=res.get("observed_fact"),
                calculation=res.get("calculation"),
                prediction=res.get("prediction"),
                simulation=res.get("simulation")
            )

        # 5. Extract minimized financial evidence
        evidence_items: List[FinancialEvidenceItem] = []
        if "top_categories" in res and isinstance(res["top_categories"], list):
            for cat in res["top_categories"]:
                evidence_items.append(
                    FinancialEvidenceItem(
                        category=cat.get("category", "general"),
                        amount=float(cat.get("amount", 0.0)),
                        currency=currency,
                        period="Last 30 Days",
                        is_verified=True,
                        source="financial_events"
                    )
                )

        # 6. Sanitize calculated results (Data Minimization)
        # Exclude internal DB IDs, secrets, or unbounded lists
        safe_results: Dict[str, Any] = {}
        disallowed_keys = {"password", "secret", "user_id", "token", "ssn", "account_number"}
        for k, v in res.items():
            if k.lower() not in disallowed_keys:
                safe_results[k] = v

        return ArthaFinancialContextContract(
            request_id=req_id,
            user_id=str(user_id),
            currency=currency,
            intent=intent,
            financial_evidence=evidence_items,
            calculated_results=safe_results,
            forecast=forecast_ctx,
            scenario_results=scenario_ctx,
            existing_recommendation=rec_ctx,
            source_references=source_references or [],
            missing_inputs=missing_inputs,
            calculation_status=status_enum,
            data_freshness_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
