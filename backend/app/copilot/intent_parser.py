import re
from app.schemas.copilot import ParsedIntent, IntentType


class IntentParser:
    """
    Parses natural language queries into a structured ParsedIntent.

    In production this would call a lightweight LLM with a strict JSON schema.
    For this deterministic MVP we use regex / heuristic matching.

    What-if change_amount sign convention
    --------------------------------------
    Positive  → spending *increases* by that amount  ("I spend 200 more")
    Negative  → spending *decreases* by that amount  ("I spend 200 less")

    This sign is passed directly to the orchestrator, which selects the
    correct simulator method and describes the scenario accurately.
    """

    def parse(self, message: str) -> ParsedIntent:
        msg = message.lower().strip()

        # ------------------------------------------------------------------
        # Extract the first recognisable numeric amount
        # ------------------------------------------------------------------
        amount: float | None = None
        amounts = re.findall(r'[\d,]+(?:\.\d+)?', msg)
        if amounts:
            try:
                amount = float(amounts[0].replace(',', ''))
            except ValueError:
                pass

        # ------------------------------------------------------------------
        # What-if scenarios
        # ------------------------------------------------------------------
        what_if_keywords = ["what happens if", "what if"]

        if any(kw in msg for kw in what_if_keywords):
            category: str | None = None
            if "eating out" in msg:
                category = "eating out"

            # Determine direction: increase or decrease?
            increase_signals = [
                "spend more", "spend extra", "increase", "more on",
                "add", "higher", "raise",
            ]
            decrease_signals = [
                "spend less", "cut", "reduce", "lower", "save",
                "spend fewer", "stop", "eliminate",
            ]

            is_increase = any(sig in msg for sig in increase_signals)
            is_decrease = any(sig in msg for sig in decrease_signals)

            # Resolve ambiguity: prefer the more specific signal that appears.
            # "spend X less" → decrease; "spend X more" → increase.
            if is_increase and not is_decrease:
                change_amount = amount  # positive → increase
            elif is_decrease and not is_increase:
                change_amount = -amount if amount is not None else None  # negative → decrease
            else:
                # Default: if neither or both signals fire, treat "spend X less" semantics
                # (most common what-if phrasing) as a decrease.
                change_amount = -amount if amount is not None else None

            return ParsedIntent(
                intent=IntentType.WHAT_IF,
                change_amount=change_amount,
                category=category,
            )

        # ------------------------------------------------------------------
        # Affordability / payment-option analysis
        # ------------------------------------------------------------------
        affordability_keywords = [
            "afford", "buy", "purchase", "cost", "costing",
            "pay upfront", "installments",
        ]
        if any(kw in msg for kw in affordability_keywords) and "what if" not in msg:
            return ParsedIntent(intent=IntentType.AFFORDABILITY_CHECK, amount=amount)

        # ------------------------------------------------------------------
        # Spending analysis
        # ------------------------------------------------------------------
        if (
            "where is most of my money going" in msg
            or "spending" in msg
            or "spend" in msg
        ):
            return ParsedIntent(intent=IntentType.SPENDING_ANALYSIS)

        # ------------------------------------------------------------------
        # Cash-flow forecast / recommendation
        # ------------------------------------------------------------------
        if (
            "next month" in msg
            or "cash flow" in msg
            or "forecast" in msg
            or "enough money" in msg
        ) and "bitcoin" not in msg:
            if "improve" in msg or "avoid" in msg or "reduce" in msg:
                return ParsedIntent(intent=IntentType.RECOMMENDATION)
            return ParsedIntent(intent=IntentType.CASH_FLOW_FORECAST)

        # ------------------------------------------------------------------
        # Financial summary
        # ------------------------------------------------------------------
        if "finances" in msg or "summary" in msg:
            return ParsedIntent(intent=IntentType.FINANCIAL_SUMMARY)

        # ------------------------------------------------------------------
        # Recommendations
        # ------------------------------------------------------------------
        if "improve" in msg or "should i do" in msg:
            return ParsedIntent(intent=IntentType.RECOMMENDATION)

        # ------------------------------------------------------------------
        # Unknown intent
        # ------------------------------------------------------------------
        return ParsedIntent(intent=IntentType.UNKNOWN)
