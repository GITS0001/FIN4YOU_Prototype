import time
import logging
from typing import Optional, Dict, Any, List

from app.artha_ai.config import ArthaAIConfig, get_artha_config
from app.artha_ai.schemas import (
    ArthaFinancialContextContract,
    ArthaInferenceRequest,
    ArthaInferenceResponse,
    ValidationResult,
    SourceReference,
    CalculationStatus,
)
from app.artha_ai.ollama_client import (
    OllamaClient,
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaTimeoutError,
    OllamaError,
)
from app.artha_ai.prompts import (
    build_system_prompt,
    build_user_prompt,
    build_repair_prompt,
)
from app.artha_ai.context_builder import ArthaContextBuilder
from app.artha_ai.retrieval import LocalFinancialRAG
from app.artha_ai.response_validator import ArthaResponseValidator

logger = logging.getLogger("artha_ai.service")


class ArthaAIService:
    """
    Main orchestration service for Artha AI.
    Integrates local Ollama inference, privacy-preserving context preparation,
    local RAG, response validation, and deterministic fallbacks.
    """
    def __init__(self, config: Optional[ArthaAIConfig] = None):
        self.config = config or get_artha_config()
        self.client = OllamaClient(self.config)
        self.rag = LocalFinancialRAG() if self.config.rag_enabled else None
        self.validator = ArthaResponseValidator()

    def is_operational(self) -> bool:
        """Check if local Ollama runtime and primary/fallback model are ready."""
        try:
            if not self.client.is_healthy():
                return False
            return self.client.has_model(self.config.model_name) or self.client.has_model(self.config.fallback_model)
        except Exception:
            return False

    def generate_explanation(
        self,
        user_message: str,
        context: ArthaFinancialContextContract,
        deterministic_fallback_fn=None
    ) -> ArthaInferenceResponse:
        """
        Produce a safe, grounded natural-language explanation for financial context.
        """
        start_time = time.perf_counter()
        retrieved_docs: List[SourceReference] = []

        # 1. Local RAG retrieval if enabled
        if self.rag and self.config.rag_enabled:
            try:
                retrieved_docs = self.rag.retrieve(user_message, top_k=self.config.rag_top_k)
                context.source_references = retrieved_docs
            except Exception as e:
                logger.warning("RAG retrieval skipped due to local error: %s", e)

        # 2. Check if local Ollama is available
        ollama_ready = False
        active_model = self.config.model_name

        try:
            if self.client.is_healthy():
                if self.client.has_model(self.config.model_name):
                    ollama_ready = True
                    active_model = self.config.model_name
                elif self.client.has_model(self.config.fallback_model):
                    ollama_ready = True
                    active_model = self.config.fallback_model
        except Exception:
            ollama_ready = False

        # 3. If Ollama is offline or model missing, apply deterministic fallback
        if not ollama_ready:
            if deterministic_fallback_fn and self.config.fallback_to_deterministic:
                fallback_text = deterministic_fallback_fn()
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                return ArthaInferenceResponse(
                    text=fallback_text,
                    intent=context.intent,
                    grounded=True,
                    model_used="deterministic_rule_engine",
                    latency_ms=elapsed_ms,
                    validation=ValidationResult(is_valid=True),
                    fallback_used=True,
                    source_references=retrieved_docs,
                    data_sources=["deterministic_fallback"]
                )
            raise OllamaConnectionError(
                f"Local Ollama is offline at {self.config.ollama_host} or model '{self.config.model_name}' is not installed."
            )

        # 4. Construct prompts
        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(context, user_message, retrieved_docs)

        # 5. Execute local inference
        raw_text = ""
        try:
            raw_text = self.client.generate(
                prompt=user_prompt,
                system=system_prompt,
                model=active_model
            )
        except OllamaError as e:
            logger.warning("Local Ollama inference failed: %s", e)
            if deterministic_fallback_fn and self.config.fallback_to_deterministic:
                fallback_text = deterministic_fallback_fn()
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                return ArthaInferenceResponse(
                    text=fallback_text,
                    intent=context.intent,
                    grounded=True,
                    model_used="deterministic_rule_engine",
                    latency_ms=elapsed_ms,
                    validation=ValidationResult(is_valid=True),
                    fallback_used=True,
                    source_references=retrieved_docs,
                    data_sources=["deterministic_fallback_after_error"]
                )
            raise

        # 6. Response Validation & Grounding Check
        val_res = self.validator.validate(raw_text, context)

        # 7. Attempt Repair if validation failed
        final_text = raw_text
        if not val_res.is_valid:
            logger.info("Response validation failed (%s errors). Attempting repair...", len(val_res.error_reasons))
            repair_prompt = build_repair_prompt(raw_text, val_res.error_reasons, context)
            try:
                repaired_text = self.client.generate(
                    prompt=repair_prompt,
                    system=system_prompt,
                    model=active_model
                )
                repaired_val = self.validator.validate(repaired_text, context)
                if repaired_val.is_valid:
                    final_text = repaired_text
                    val_res = repaired_val
                    val_res.repaired = True
                else:
                    # Repair still invalid: fallback to verified deterministic output
                    if deterministic_fallback_fn and self.config.fallback_to_deterministic:
                        logger.warning("Repair revalidation failed. Using deterministic verified fallback.")
                        final_text = deterministic_fallback_fn()
                        val_res = ValidationResult(is_valid=True, repaired=False)
            except Exception:
                if deterministic_fallback_fn and self.config.fallback_to_deterministic:
                    final_text = deterministic_fallback_fn()
                    val_res = ValidationResult(is_valid=True, repaired=False)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return ArthaInferenceResponse(
            text=final_text,
            intent=context.intent,
            grounded=val_res.is_valid,
            model_used=active_model,
            latency_ms=elapsed_ms,
            validation=val_res,
            fallback_used=False,
            source_references=retrieved_docs,
            data_sources=["local_ollama", "DecisionEngine", "PredictionEngine"]
        )

    def explain_decision_trace(self, trace: Any, currency: str = "INR") -> str:
        """
        Transforms a DecisionTrace object into a human-friendly narrative
        without fabricating missing numbers.
        """
        if not trace:
            return "No Decision Trace is available for this inquiry."

        obs = getattr(trace, "observed_fact", "N/A")
        calc = getattr(trace, "calculation", "N/A")
        pred = getattr(trace, "prediction", "N/A")
        sim = getattr(trace, "simulation", "N/A")
        rec = getattr(trace, "recommendation", None)
        action_text = getattr(rec, "actionable_text", "None") if rec else "None"
        conf = getattr(rec, "confidence_level", "HIGH") if rec else "HIGH"

        return (
            f"**Decision Trace Analysis:**\n"
            f"• **Observed Baseline:** {obs}\n"
            f"• **Calculation:** {calc}\n"
            f"• **Prediction:** {pred}\n"
            f"• **Simulation:** {sim}\n"
            f"• **Recommendation:** {action_text} (Confidence: {conf})"
        )


_service_instance: Optional[ArthaAIService] = None

def get_artha_service() -> ArthaAIService:
    global _service_instance
    if _service_instance is None:
        _service_instance = ArthaAIService()
    return _service_instance
