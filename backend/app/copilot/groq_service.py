import os
import json
import urllib.request
import urllib.error
import logging

logger = logging.getLogger("fin4you.copilot.groq")

# Load environment variables from .env if present
def _load_dotenv():
    try:
        from dotenv import load_dotenv, find_dotenv
        env_file = find_dotenv(usecwd=True)
        if env_file:
            load_dotenv(env_file)
            if os.getenv("GROQ_API_KEY"):
                return
    except Exception:
        pass

    current = os.path.abspath(os.getcwd())
    while current:
        candidate = os.path.join(current, ".env")
        if os.path.exists(candidate):
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip(), v.strip())
            except Exception:
                pass
            break
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

_load_dotenv()

FALLBACK_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "llama-3.3-70b-versatile",
]

class GroqLLMService:
    """
    High-speed Groq LLM Service powering Artha AI.
    Integrates real-time financial context into conversational explanations with zero hallucination.
    """
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.startswith("gsk_"))

    def test_connectivity(self):
        """
        Safely test API key connectivity without exposing secrets.
        """
        if not self.is_available():
            return {"status": "UNCONFIGURED", "detail": "GROQ_API_KEY is not set in environment."}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        try:
            req = urllib.request.Request("https://api.groq.com/openai/v1/models", headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                models = [m.get("id") for m in res.get("data", [])]
                return {
                    "status": "SUCCESS",
                    "key_prefix": self.api_key[:8] + "...",
                    "active_model": self.model,
                    "available_models_count": len(models),
                }
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            return {"status": "HTTP_ERROR", "code": e.code, "detail": err_body[:200]}
        except Exception as e:
            return {"status": "NETWORK_ERROR", "detail": str(e)}

    def generate_explanation(
        self,
        user_query: str,
        intent_name: str,
        rule_response: str,
        financial_context: dict
    ) -> str:
        """
        Enhance the copilot response using Groq LLM, grounding it with exact deterministic financial facts.
        """
        if not self.is_available():
            return rule_response

        system_prompt = (
            "You are Artha AI, the intelligent personal financial assistant for Fin4You.\n"
            "Your role is to answer user financial questions with precision, empathy, and practical advice.\n\n"
            "CRITICAL RESPONSE RULES:\n"
            "1. GREETINGS (e.g., 'Hi', 'Hello', 'Good morning'): Respond naturally, warmly, and concisely in 1-2 sentences. Ask how you can help with their money today. DO NOT list account metrics, balances, cash flow, or financial reports unless specifically asked.\n"
            "2. SAVINGS PLANS (e.g., 'How can I save money in 1 month?'): Provide a comprehensive, highly actionable 4-week savings guide. Include:\n"
            "   - Weekly target goals.\n"
            "   - At least 5 specific, high-impact expense reduction strategies.\n"
            "   - Recommended budgeting allocations (such as the 50/30/20 rule).\n"
            "   - Practical tracking methods.\n"
            "   - Clearly mark any example dollar amounts as hypothetical illustrative calculations.\n"
            "3. ACCOUNT & DATA QUERIES (Balance, Cash Flow, Affordability): Ground all figures strictly on the provided verified financial context. Never hallucinate fake balance numbers.\n"
            "4. Never output truncated or incomplete sentences. Write complete, well-structured Markdown responses."
        )

        user_content = (
            f"User Question: {user_query}\n\n"
            f"Identified Intent: {intent_name}\n\n"
            f"Verified Financial Context:\n"
            f"{json.dumps(financial_context, indent=2, default=str)}\n\n"
            f"Base Rule Response:\n"
            f"{rule_response}\n\n"
            f"Synthesize this into an articulate, complete, friendly, and expert financial response for the user."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # Try active model first, then fallback models if 400/404 occurs
        models_to_try = [self.model] + [m for m in FALLBACK_MODELS if m != self.model]

        for model_id in models_to_try:
            payload = {
                "model": model_id,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                "temperature": 0.3,
                "max_tokens": 1800
            }

            try:
                req = urllib.request.Request(
                    self.api_url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=12) as resp:
                    res_body = json.loads(resp.read().decode("utf-8"))
                    choices = res_body.get("choices", [])
                    if choices:
                        ai_text = choices[0].get("message", {}).get("content", "").strip()
                        if ai_text:
                            return ai_text
            except urllib.error.HTTPError as e:
                logger.warning(f"Groq model '{model_id}' failed ({e.code}). Trying fallback...")
                continue
            except Exception as e:
                logger.warning(f"Groq LLM call exception: {type(e).__name__}")
                break

        return rule_response

groq_llm_service = GroqLLMService()
