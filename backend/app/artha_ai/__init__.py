"""
Artha AI: Local, Privacy-First Financial LLM Subsystem Using Ollama.
"""

from app.artha_ai.config import ArthaAIConfig, get_artha_config, set_artha_config
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
    OllamaError,
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaTimeoutError,
    OllamaInferenceError,
)
from app.artha_ai.context_builder import ArthaContextBuilder
from app.artha_ai.retrieval import LocalFinancialRAG
from app.artha_ai.response_validator import ArthaResponseValidator
from app.artha_ai.service import ArthaAIService, get_artha_service

__all__ = [
    "ArthaAIConfig",
    "get_artha_config",
    "set_artha_config",
    "ArthaFinancialContextContract",
    "ArthaInferenceRequest",
    "ArthaInferenceResponse",
    "ValidationResult",
    "SourceReference",
    "CalculationStatus",
    "OllamaClient",
    "OllamaError",
    "OllamaConnectionError",
    "OllamaModelNotFoundError",
    "OllamaTimeoutError",
    "OllamaInferenceError",
    "ArthaContextBuilder",
    "LocalFinancialRAG",
    "ArthaResponseValidator",
    "ArthaAIService",
    "get_artha_service",
]
