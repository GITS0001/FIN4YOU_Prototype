import re
from app.schemas.copilot import ParsedIntent, IntentType

class IntentParser:
    """
    Parses natural language into a structured intent.
    In a full production environment, this would call a lightweight LLM (e.g. Gemini) 
    with a strict JSON schema. For this robust MVP and deterministic fallback, 
    we use regex/heuristic parsing.
    """
    def parse(self, message: str) -> ParsedIntent:
        msg = message.lower()
        
        # Extract potential amounts (e.g., 15000, 15,000, 2,000)
        amount = None
        amounts = re.findall(r'[\d,]+(?:\.\d+)?', msg)
        if amounts:
            try:
                amount = float(amounts[0].replace(',', ''))
            except ValueError:
                pass

        if "afford" in msg and "installment" in msg:
            return ParsedIntent(intent=IntentType.PAYMENT_OPTION_ANALYSIS, amount=amount)
        elif "afford" in msg:
            return ParsedIntent(intent=IntentType.AFFORDABILITY_CHECK, amount=amount)
        elif "what happens if" in msg or "what if" in msg:
            # simple extraction for "spend X less on Y"
            category = None
            if "eating out" in msg:
                category = "eating out"
            return ParsedIntent(intent=IntentType.WHAT_IF, change_amount=-amount if amount else None, category=category)
        elif "where is most of my money going" in msg or "spending" in msg or "spend" in msg:
            return ParsedIntent(intent=IntentType.SPENDING_ANALYSIS)
        elif ("next month" in msg or "cash flow" in msg or "forecast" in msg or "enough money" in msg) and "bitcoin" not in msg:
            if "improve" in msg or "avoid" in msg or "reduce" in msg:
                return ParsedIntent(intent=IntentType.RECOMMENDATION)
            return ParsedIntent(intent=IntentType.CASH_FLOW_FORECAST)
        elif "finances" in msg or "summary" in msg:
            return ParsedIntent(intent=IntentType.FINANCIAL_SUMMARY)
        elif "improve" in msg or "should i do" in msg:
            return ParsedIntent(intent=IntentType.RECOMMENDATION)
        else:
            return ParsedIntent(intent=IntentType.UNKNOWN)
