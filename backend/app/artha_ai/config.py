import os
from typing import Optional
from pydantic import BaseModel, Field


class ArthaAIConfig(BaseModel):
    """
    Configuration for Artha AI Local LLM subsystem.
    Enforces privacy-first defaults and local-only runtime execution.
    """
    ollama_host: str = Field(
        default="http://127.0.0.1:11434",
        description="Local Ollama runtime HTTP endpoint. Must not be exposed publicly."
    )
    model_name: str = Field(
        default="llama3.2:3b",
        description="Local instruction-tuned model. Recommended: llama3.2:3b or qwen2.5:3b."
    )
    fallback_model: str = Field(
        default="qwen2.5:3b",
        description="Alternative local model candidate if primary is absent."
    )
    connect_timeout: float = Field(
        default=5.0,
        description="Max seconds to connect to local Ollama daemon."
    )
    inference_timeout: float = Field(
        default=30.0,
        description="Max seconds for complete local model generation."
    )
    max_retries: int = Field(
        default=1,
        description="Controlled retries on transient local timeout."
    )
    temperature: float = Field(
        default=0.1,
        description="Conservative sampling temperature for deterministic financial explanation."
    )
    top_p: float = Field(
        default=0.9,
        description="Nucleus sampling cutoff."
    )
    max_tokens: int = Field(
        default=512,
        description="Bounded response length to maintain low latency on local hardware."
    )
    seed: int = Field(
        default=42,
        description="Deterministic random seed for reproducible outputs."
    )
    context_window: int = Field(
        default=4096,
        description="Bounded context size in tokens to preserve VRAM."
    )
    strict_privacy_logging: bool = Field(
        default=True,
        description="When true, sensitive numeric context and PII are redacted from default logs."
    )
    fallback_to_deterministic: bool = Field(
        default=True,
        description="If Ollama is offline or model fails validation, gracefully return verified rule output."
    )
    rag_enabled: bool = Field(
        default=True,
        description="Enable local RAG for financial documentation and formula reference grounding."
    )
    rag_top_k: int = Field(
        default=3,
        description="Number of relevant documentation passages to inject."
    )

    @classmethod
    def from_env(cls) -> "ArthaAIConfig":
        """Load settings from environment variables with safe local defaults."""
        host = os.getenv("ARTHA_OLLAMA_HOST", "http://127.0.0.1:11434").strip()
        # Enforce that Ollama host cannot accidentally point to cloud/external URLs
        if not (host.startswith("http://127.0.0.1") or host.startswith("http://localhost")):
            # Log warning or reset to local
            host = "http://127.0.0.1:11434"

        return cls(
            ollama_host=host,
            model_name=os.getenv("ARTHA_OLLAMA_MODEL", "llama3.2:3b").strip(),
            fallback_model=os.getenv("ARTHA_OLLAMA_FALLBACK_MODEL", "qwen2.5:3b").strip(),
            connect_timeout=float(os.getenv("ARTHA_CONNECT_TIMEOUT", "5.0")),
            inference_timeout=float(os.getenv("ARTHA_INFERENCE_TIMEOUT", "30.0")),
            max_retries=int(os.getenv("ARTHA_MAX_RETRIES", "1")),
            temperature=float(os.getenv("ARTHA_TEMPERATURE", "0.1")),
            top_p=float(os.getenv("ARTHA_TOP_P", "0.9")),
            max_tokens=int(os.getenv("ARTHA_MAX_TOKENS", "512")),
            seed=int(os.getenv("ARTHA_SEED", "42")),
            context_window=int(os.getenv("ARTHA_CONTEXT_WINDOW", "4096")),
            strict_privacy_logging=os.getenv("ARTHA_STRICT_PRIVACY_LOGGING", "true").lower() in ("true", "1", "yes"),
            fallback_to_deterministic=os.getenv("ARTHA_FALLBACK_TO_DETERMINISTIC", "true").lower() in ("true", "1", "yes"),
            rag_enabled=os.getenv("ARTHA_RAG_ENABLED", "true").lower() in ("true", "1", "yes"),
            rag_top_k=int(os.getenv("ARTHA_RAG_TOP_K", "3")),
        )


_config_instance: Optional[ArthaAIConfig] = None

def get_artha_config() -> ArthaAIConfig:
    global _config_instance
    if _config_instance is None:
        _config_instance = ArthaAIConfig.from_env()
    return _config_instance

def set_artha_config(cfg: ArthaAIConfig) -> None:
    global _config_instance
    _config_instance = cfg
