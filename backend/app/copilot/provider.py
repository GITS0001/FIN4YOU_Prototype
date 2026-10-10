"""
Artha AI LLM Provider — Groq Integration with Deterministic Fallback
====================================================================
Uses Groq as the single LLM provider for the hackathon.
Handles API timeouts, rate limits (HTTP 429), and failures gracefully.
When credentials are missing or errors occur, seamlessly falls back
to DeterministicFallbackProvider without breaking financial flows.
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import httpx

logger = logging.getLogger("fin4you.artha_provider")


class LLMResult(BaseModel):
    content: str
    provider_name: str
    model_name: str
    tokens_used: Optional[int] = None
    is_fallback: bool = False
    error: Optional[str] = None


class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 800,
    ) -> LLMResult:
        pass


class GroqProvider(BaseLLMProvider):
    """
    Groq API Provider implementation using httpx.
    Single LLM provider for FIN4YOU Artha AI.
    Configurable via GROQ_API_KEY, GROQ_MODEL, GROQ_BASE_URL.
    """

    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: float = 12.0,
    ):
        self._api_key = api_key or os.getenv("GROQ_API_KEY", "").strip()
        self._model = model or os.getenv("GROQ_MODEL", self.DEFAULT_MODEL).strip()
        self._base_url = (base_url or os.getenv("GROQ_BASE_URL", self.DEFAULT_BASE_URL)).rstrip("/")
        self._timeout = timeout_seconds

    @property
    def name(self) -> str:
        return "groq"

    @property
    def model_name(self) -> str:
        return self._model

    def is_available(self) -> bool:
        return bool(
            self._api_key
            and len(self._api_key) > 5
            and not self._api_key.startswith("your_")
            and not self._api_key.startswith("gsk_placeholder")
        )

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 800,
    ) -> LLMResult:
        if not self.is_available():
            return LLMResult(
                content="",
                provider_name=self.name,
                model_name=self.model_name,
                is_fallback=True,
                error="GROQ_API_KEY is not configured.",
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Bounded retry with timeout
        retries = 2
        last_error = None
        for attempt in range(retries):
            try:
                with httpx.Client(timeout=self._timeout) as client:
                    resp = client.post(f"{self._base_url}/chat/completions", headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        choice = data.get("choices", [{}])[0]
                        text = choice.get("message", {}).get("content", "").strip()
                        total_tokens = data.get("usage", {}).get("total_tokens")
                        return LLMResult(
                            content=text,
                            provider_name=self.name,
                            model_name=self.model_name,
                            tokens_used=total_tokens,
                            is_fallback=False,
                        )
                    elif resp.status_code == 429:
                        last_error = "Groq rate limit exceeded (HTTP 429)."
                        logger.warning(f"Groq attempt {attempt+1}: {last_error}")
                    else:
                        last_error = f"Groq HTTP {resp.status_code}: {resp.text[:200]}"
                        logger.warning(f"Groq attempt {attempt+1}: {last_error}")
            except httpx.TimeoutException:
                last_error = f"Groq API timed out after {self._timeout}s"
                logger.warning(f"Groq attempt {attempt+1}: {last_error}")
            except Exception as e:
                last_error = f"Groq client error: {str(e)}"
                logger.warning(f"Groq attempt {attempt+1}: {last_error}")

        return LLMResult(
            content="",
            provider_name=self.name,
            model_name=self.model_name,
            is_fallback=True,
            error=last_error,
        )


class DeterministicFallbackProvider(BaseLLMProvider):
    """
    High-precision deterministic provider.
    Never invents facts, balances, or formulas.
    Operates when Groq credentials are not yet supplied or API calls fail.
    """

    @property
    def name(self) -> str:
        return "deterministic_fallback"

    @property
    def model_name(self) -> str:
        return "deterministic-v1"

    def is_available(self) -> bool:
        return True

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 800,
    ) -> LLMResult:
        return LLMResult(
            content="",
            provider_name=self.name,
            model_name=self.model_name,
            is_fallback=True,
            error="Operating in deterministic fallback mode.",
        )


def get_llm_provider() -> BaseLLMProvider:
    """
    Returns GroqProvider if configured, otherwise DeterministicFallbackProvider.
    """
    groq = GroqProvider()
    if groq.is_available():
        return groq
    return DeterministicFallbackProvider()
