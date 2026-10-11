import time
import logging
from typing import Optional, List, Dict, Any
import httpx
from app.artha_ai.config import ArthaAIConfig, get_artha_config

logger = logging.getLogger("artha_ai.ollama_client")


class OllamaError(Exception):
    """Base exception for local Ollama interactions."""
    pass


class OllamaConnectionError(OllamaError):
    """Raised when Ollama daemon is not running or unreachable on localhost."""
    pass


class OllamaModelNotFoundError(OllamaError):
    """Raised when the specified model is not downloaded locally."""
    pass


class OllamaTimeoutError(OllamaError):
    """Raised when local inference exceeds timeout threshold."""
    pass


class OllamaInferenceError(OllamaError):
    """Raised when Ollama returns an error payload during generation."""
    pass


class OllamaClient:
    """
    Local-first HTTP client for Ollama daemon.
    Strictly constrained to localhost to ensure privacy and zero cloud egress.
    """
    def __init__(self, config: Optional[ArthaAIConfig] = None):
        self.config = config or get_artha_config()
        self._validate_local_host(self.config.ollama_host)

    @staticmethod
    def _validate_local_host(host: str) -> None:
        """Enforces privacy boundary: prevents connecting to non-local endpoints."""
        allowed_prefixes = ("http://127.0.0.1", "http://localhost", "http://[::1]")
        if not any(host.startswith(p) for p in allowed_prefixes):
            raise ValueError(
                f"Privacy violation: Artha AI Ollama client is strictly local. Host '{host}' is not permitted."
            )

    def get_version(self) -> Dict[str, Any]:
        """Check if local Ollama daemon is reachable and return version."""
        url = f"{self.config.ollama_host}/api/version"
        try:
            with httpx.Client(timeout=self.config.connect_timeout) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    return resp.json()
                raise OllamaConnectionError(f"Ollama returned unexpected HTTP {resp.status_code}")
        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"Cannot connect to local Ollama at {url}: {e}") from e
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(f"Timed out connecting to local Ollama at {url}") from e
        except Exception as e:
            raise OllamaConnectionError(f"Failed to communicate with local Ollama: {e}") from e

    def is_healthy(self) -> bool:
        """Quick boolean health check."""
        try:
            self.get_version()
            return True
        except Exception:
            return False

    def list_models(self) -> List[str]:
        """Fetch list of available local models."""
        url = f"{self.config.ollama_host}/api/tags"
        try:
            with httpx.Client(timeout=self.config.connect_timeout) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                    return models
                raise OllamaConnectionError(f"Failed to list models: HTTP {resp.status_code}")
        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"Cannot connect to local Ollama: {e}") from e
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError("Timed out listing models from local Ollama") from e
        except Exception as e:
            raise OllamaConnectionError(f"Error listing local models: {e}") from e

    def has_model(self, model_name: str) -> bool:
        """Verify if a specific model or base tag is available locally."""
        try:
            models = self.list_models()
            clean_target = model_name.split(":")[0]
            for m in models:
                if m == model_name or m.startswith(f"{clean_target}:"):
                    return True
            return False
        except Exception:
            return False

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute local prompt completion with strict privacy logging and timeouts.
        """
        target_model = model or self.config.model_name
        url = f"{self.config.ollama_host}/api/generate"

        payload: Dict[str, Any] = {
            "model": target_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "num_predict": self.config.max_tokens,
                "seed": self.config.seed,
                "num_ctx": self.config.context_window,
                **(options or {})
            }
        }
        if system:
            payload["system"] = system

        start_time = time.perf_counter()
        if not self.config.strict_privacy_logging:
            logger.debug("Ollama prompt dispatch: %s...", prompt[:80])

        try:
            with httpx.Client(timeout=self.config.inference_timeout) as client:
                resp = client.post(url, json=payload)
                elapsed_ms = (time.perf_counter() - start_time) * 1000

                if resp.status_code == 200:
                    data = resp.json()
                    response_text = data.get("response", "").strip()
                    logger.info(
                        "Ollama local inference completed: model=%s, elapsed_ms=%.1f",
                        target_model, elapsed_ms
                    )
                    return response_text

                if resp.status_code == 404:
                    raise OllamaModelNotFoundError(
                        f"Model '{target_model}' not found in local Ollama. Run: ollama pull {target_model}"
                    )

                raise OllamaInferenceError(
                    f"Ollama inference error HTTP {resp.status_code}: {resp.text}"
                )

        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"Local Ollama connection failed at {url}: {e}") from e
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(
                f"Local Ollama inference timed out after {self.config.inference_timeout}s"
            ) from e
        except OllamaError:
            raise
        except Exception as e:
            raise OllamaInferenceError(f"Unexpected error in local Ollama inference: {e}") from e

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute local chat completion with system and user messages separated.
        """
        target_model = model or self.config.model_name
        url = f"{self.config.ollama_host}/api/chat"

        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "num_predict": self.config.max_tokens,
                "seed": self.config.seed,
                "num_ctx": self.config.context_window,
                **(options or {})
            }
        }

        start_time = time.perf_counter()
        try:
            with httpx.Client(timeout=self.config.inference_timeout) as client:
                resp = client.post(url, json=payload)
                elapsed_ms = (time.perf_counter() - start_time) * 1000

                if resp.status_code == 200:
                    data = resp.json()
                    msg = data.get("message", {})
                    response_text = msg.get("content", "").strip()
                    logger.info(
                        "Ollama local chat completed: model=%s, elapsed_ms=%.1f",
                        target_model, elapsed_ms
                    )
                    return response_text

                if resp.status_code == 404:
                    raise OllamaModelNotFoundError(
                        f"Model '{target_model}' not found in local Ollama. Run: ollama pull {target_model}"
                    )

                raise OllamaInferenceError(
                    f"Ollama chat error HTTP {resp.status_code}: {resp.text}"
                )

        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"Local Ollama connection failed at {url}: {e}") from e
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(
                f"Local Ollama chat timed out after {self.config.inference_timeout}s"
            ) from e
        except OllamaError:
            raise
        except Exception as e:
            raise OllamaInferenceError(f"Unexpected error in local Ollama chat: {e}") from e
