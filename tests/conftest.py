import os
os.environ["ENVIRONMENT"] = "test"

import pytest
from unittest.mock import patch
from app.copilot.provider import BaseLLMProvider, LLMResult

def mock_generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.2, max_tokens: int = 800) -> LLMResult:
    prompt_lower = prompt.lower()
    
    # Intent Parsing Mocking
    if system_prompt and "intent extractor" in system_prompt.lower():
        if "afford" in prompt_lower and "1302" in prompt_lower:
            content = '{"intent": "AFFORDABILITY_CHECK", "amount": 1302.4}'
        elif "afford" in prompt_lower:
            if "999" in prompt_lower:
                content = '{"intent": "AFFORDABILITY_CHECK", "amount": 999.0}'
            elif "5000" in prompt_lower:
                content = '{"intent": "AFFORDABILITY_CHECK", "amount": 5000.0}'
            else:
                content = '{"intent": "UNKNOWN"}'
        elif "what if" in prompt_lower or "what happens if" in prompt_lower:
            if "200 less" in prompt_lower:
                content = '{"intent": "WHAT_IF", "change_amount": -200, "category": "eating out"}'
            elif "500 less" in prompt_lower:
                content = '{"intent": "WHAT_IF", "change_amount": -500, "category": "eating out"}'
            elif "300 more" in prompt_lower or "increase spending by 300" in prompt_lower:
                content = '{"intent": "WHAT_IF", "change_amount": 300, "category": "eating out"}'
            elif "500 more" in prompt_lower:
                content = '{"intent": "WHAT_IF", "change_amount": 500, "category": "eating out"}'
            elif "change my spending habits" in prompt_lower:
                content = '{"intent": "WHAT_IF"}'
            else:
                content = '{"intent": "WHAT_IF"}'
        else:
            content = '{"intent": "UNKNOWN"}'
            
        return LLMResult(content=content, provider_name="mock_groq", model_name="mock_model")
    
    # Response Generation Mocking
    else:
        if "installment" in prompt_lower and "1302" in prompt_lower:
            content = "You can afford this in installments. Option 1: 12 x 108.5/installment, total 1,302 (installment)."
        elif "reduce" in prompt_lower or "less" in prompt_lower or "lower" in prompt_lower:
            content = "If you reduce spending, you will increase your balance."
        elif "increase" in prompt_lower or "more" in prompt_lower or "higher" in prompt_lower:
            content = "If you increase spending, you will reduce your balance and may breach the buffer."
        elif "no_change" in prompt_lower:
            content = "No change amount was specified."
        elif "breached" in prompt_lower or "breach" in prompt_lower:
            content = "This purchase would breach your minimum buffer."
        elif "unknown" in prompt_lower or "bitcoin" in prompt_lower or "unsupported" in prompt_lower:
            content = "I can only help with finance, afford, or spend questions."
        else:
            content = "This is a mocked financial explanation. 1,302 in installments."
            
        return LLMResult(content=content, provider_name="mock_groq", model_name="mock_model")


@pytest.fixture(autouse=True)
def mock_llm_provider(request):
    """Automatically mock GroqProvider.generate for all tests unless marked live."""
    if "live" in request.keywords:
        yield
        return
        
    with patch("app.copilot.provider.GroqProvider.generate", new=mock_generate):
        yield
