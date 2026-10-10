import unittest
from app.copilot.intent_parser import IntentParser
from app.copilot.response_generator import ResponseGenerator
from app.schemas.copilot import ParsedIntent, IntentType

class TestCopilotIntents(unittest.TestCase):

    def setUp(self):
        self.parser = IntentParser()
        self.generator = ResponseGenerator()

    def test_greeting_intent(self):
        greetings = ["Hi", "Hello", "Hey", "Good morning", "Hi Artha"]
        for g in greetings:
            parsed = self.parser.parse(g)
            self.assertEqual(parsed.intent, IntentType.GREETING, f"Failed for prompt: '{g}'")
            res = self.generator.generate(parsed, {}, "USD")
            self.assertIn("Welcome to Fin4You", res)
            self.assertNotIn("available balance", res.lower())

    def test_saving_plan_intent(self):
        prompts = [
            "How can I save money in 1 month?",
            "Give me a 30 day savings plan",
            "How do I build savings fast?",
            "What is a good way to save money?",
        ]
        for p in prompts:
            parsed = self.parser.parse(p)
            self.assertEqual(parsed.intent, IntentType.SAVING_PLAN, f"Failed for prompt: '{p}'")
            res = self.generator.generate(parsed, {}, "USD")
            self.assertIn("Savings Plan", res)

    def test_budgeting_intent(self):
        prompts = [
            "How do I create a budget?",
            "What is the 50/30/20 rule?",
            "Help me set up a budget allocation",
        ]
        for p in prompts:
            parsed = self.parser.parse(p)
            self.assertEqual(parsed.intent, IntentType.BUDGETING, f"Failed for prompt: '{p}'")
            res = self.generator.generate(parsed, {}, "USD")
            self.assertIn("50/30/20", res)

    def test_balance_query_intent(self):
        prompts = [
            "What is my current balance?",
            "How much balance do I have left?",
            "Show my available account balance",
        ]
        for p in prompts:
            parsed = self.parser.parse(p)
            self.assertEqual(parsed.intent, IntentType.BALANCE_QUERY, f"Failed for prompt: '{p}'")
            res = self.generator.generate(parsed, {"balance": 15000, "minimum_buffer": 2000}, "USD")
            self.assertIn("$15,000.00", res)

    def test_cash_flow_query_intent(self):
        prompts = [
            "What is my net cash flow?",
            "Show my cash flow summary",
        ]
        for p in prompts:
            parsed = self.parser.parse(p)
            self.assertEqual(parsed.intent, IntentType.CASH_FLOW_QUERY, f"Failed for prompt: '{p}'")
            res = self.generator.generate(parsed, {"cash_flow": 2500}, "USD")
            self.assertIn("$2,500.00", res)

    def test_affordability_check_intent(self):
        parsed = self.parser.parse("Can I afford a $1,500 laptop?")
        self.assertEqual(parsed.intent, IntentType.AFFORDABILITY_CHECK)
        self.assertEqual(parsed.amount, 1500.0)

    def test_what_if_intent(self):
        parsed = self.parser.parse("What if I cut spending by $300?")
        self.assertEqual(parsed.intent, IntentType.WHAT_IF)
        self.assertEqual(parsed.change_amount, -300.0)

if __name__ == "__main__":
    unittest.main()
