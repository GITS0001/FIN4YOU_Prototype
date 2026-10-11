import pytest
import os
from unittest.mock import patch
from app.copilot.provider import GroqProvider, DeterministicFallbackProvider, get_llm_provider
from app.copilot.orchestrator import CopilotOrchestrator

def test_provider_selection():
    # If API key is not present or invalid, it should use fallback
    with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
        provider = get_llm_provider()
        assert isinstance(provider, DeterministicFallbackProvider)

def test_groq_invalid_api_key():
    with patch.dict(os.environ, {"GROQ_API_KEY": "invalid_key"}):
        provider = get_llm_provider()
        # provider.is_available() checks for length > 5 and not placeholder
        if isinstance(provider, GroqProvider):
            res = provider.generate("Hello")
            assert res.is_fallback is True
            assert "error" in res.error.lower() or "401" in res.error or "timeout" in res.error

def test_deterministic_fallback():
    provider = DeterministicFallbackProvider()
    res = provider.generate("How much did I spend?")
    assert res.is_fallback is True
    assert res.content == ""
    assert "deterministic" in res.error.lower()

def test_copilot_financial_question_without_data(db, test_user):
    from app.schemas.copilot import CopilotRequest
    orchestrator = CopilotOrchestrator()
    # Provide an empty database state for this user via the db fixture
    req = CopilotRequest(message="What is my total income?", user_id=str(test_user.id))
    # It will fetch from DB internally
    reply = orchestrator.process_query(req, db)
    assert reply is not None
    assert reply.response != ""
