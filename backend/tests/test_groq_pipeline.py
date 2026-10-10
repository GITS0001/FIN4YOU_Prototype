import os
import json
import unittest
from unittest.mock import patch, MagicMock
from app.copilot.groq_service import GroqLLMService, groq_llm_service
from app.copilot.orchestrator import CopilotOrchestrator
from app.schemas.copilot import CopilotRequest, IntentType

class TestGroqPipeline(unittest.TestCase):

    def test_01_missing_groq_api_key(self):
        service = GroqLLMService()
        service.api_key = ""
        self.assertFalse(service.is_available())
        res = service.generate_explanation("test", "UNKNOWN", "Fallback Text", {})
        self.assertEqual(res, "Fallback Text")

    def test_02_invalid_api_credentials(self):
        service = GroqLLMService()
        service.api_key = "invalid_key_format"
        self.assertFalse(service.is_available())
        res = service.generate_explanation("test", "UNKNOWN", "Fallback Text", {})
        self.assertEqual(res, "Fallback Text")

    @patch("urllib.request.urlopen")
    def test_03_successful_groq_response(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "choices": [{"message": {"content": "Enhanced Groq LLM Response"}}]
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        service = GroqLLMService()
        service.api_key = "gsk_dummy_test_key_for_unit_tests"
        res = service.generate_explanation("Can I afford?", "AFFORDABILITY_CHECK", "Fallback", {"balance": 1000})
        self.assertEqual(res, "Enhanced Groq LLM Response")

    @patch("urllib.request.urlopen")
    def test_04_empty_or_malformed_groq_response(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"choices": []}).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        service = GroqLLMService()
        service.api_key = "gsk_dummy_test_key"
        res = service.generate_explanation("test", "UNKNOWN", "Rule Fallback", {})
        self.assertEqual(res, "Rule Fallback")

    @patch("urllib.request.urlopen")
    def test_05_model_unavailable_or_rate_limited(self, mock_urlopen):
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError("http://test", 429, "Rate limit", {}, None)

        service = GroqLLMService()
        service.api_key = "gsk_dummy_key"
        res = service.generate_explanation("test", "UNKNOWN", "Rule Fallback RateLimit", {})
        self.assertEqual(res, "Rule Fallback RateLimit")

    @patch("urllib.request.urlopen")
    def test_06_network_timeout(self, mock_urlopen):
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("Timeout")

        service = GroqLLMService()
        service.api_key = "gsk_dummy_key"
        res = service.generate_explanation("test", "UNKNOWN", "Rule Fallback Timeout", {})
        self.assertEqual(res, "Rule Fallback Timeout")

    def test_07_no_secrets_in_outputs(self):
        service = GroqLLMService()
        service.api_key = "gsk_super_secret_key_123456789"
        info = service.test_connectivity()
        # Verify secret key is masked
        self.assertNotIn("gsk_super_secret_key_123456789", str(info))
        if info.get("key_prefix"):
            self.assertTrue(info["key_prefix"].endswith("..."))

    def test_08_live_connectivity_check(self):
        # Safe live connectivity check without exposing key
        if groq_llm_service.is_available():
            info = groq_llm_service.test_connectivity()
            self.assertEqual(info.get("status"), "SUCCESS")

if __name__ == "__main__":
    unittest.main()
