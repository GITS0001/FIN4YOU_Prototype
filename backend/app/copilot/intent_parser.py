import re
import json
import logging
from typing import Optional, List, Dict, Any

from app.schemas.copilot import ParsedIntent, IntentType
from app.copilot.provider import BaseLLMProvider

logger = logging.getLogger("fin4you.intent_parser")


class IntentParser:
    """
    Two-stage intent parser:
    1. If an active LLM provider is present, uses structured JSON prompt to classify intent and extract entities.
    2. Uses deterministic heuristic/regex engine as primary or fallback if LLM is absent, times out, or produces malformed output.
    """

    def __init__(self, provider: Optional[BaseLLMProvider] = None):
        self.provider = provider

    def parse(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> ParsedIntent:
        msg = message.strip()
        if not msg:
            return ParsedIntent(intent=IntentType.UNKNOWN)

        # Stage 1: Try LLM extraction if provider is available
        if self.provider and self.provider.is_available() and not getattr(self.provider, "is_fallback", False):
            try:
                llm_parsed = self._parse_with_llm(msg, conversation_history)
                if llm_parsed and llm_parsed.intent != IntentType.UNKNOWN:
                    return llm_parsed
            except Exception as e:
                logger.warning(f"LLM parsing failed ({e}); falling back to deterministic parser.")

        # Stage 2: Deterministic extraction
        return self._parse_deterministic(msg, conversation_history)

    def _parse_with_llm(self, message: str, history: Optional[List[Dict[str, str]]] = None) -> Optional[ParsedIntent]:
        system_prompt = (
            "You are the NLU intent extractor for Artha AI, a Financial Health Copilot. "
            "Analyze the user's financial question and map it to one of these intents:\n"
            "- FINANCIAL_SUMMARY (overall balance, cash flow, high-level summary)\n"
            "- SPENDING_ANALYSIS (historical spending, category breakdown, food/dining costs)\n"
            "- CASH_FLOW_FORECAST (future income, expenses, cash flow projections)\n"
            "- AFFORDABILITY_CHECK (evaluating if a user can afford a purchase, phone, car, item)\n"
            "- WHAT_IF (simulating spending changes, income drops/increases, unexpected expenses)\n"
            "- PLAN_EVALUATION (comparing financial action plans, strategies, reserve protection)\n"
            "- GOAL_FEASIBILITY (checking if a savings goal can be met within a deadline)\n"
            "- RECOMMENDATION (explaining recommendations, why spend less, advice to improve)\n"
            "- MISSING_DATA_CLARIFICATION (asking what information is needed to make advice reliable)\n"
            "- UNKNOWN (non-financial questions or unsupported queries)\n\n"
            "CRITICAL: For WHAT_IF, if the user wants to spend less/reduce spending, make `change_amount` a negative number. If they want to spend more, make it positive.\n"
            "Return strictly valid JSON with keys: "
            '{"intent": string, "amount": float|null, "category": string|null, "change_amount": float|null, '
            '"income_shock_percentage": float|null, "unexpected_expense": float|null, "horizon_months": int|null, '
            '"target_goal_amount": float|null, "target_goal_months": int|null}'
        )

        prompt = f"User query: \"{message}\"\nJSON:"
        res = self.provider.generate(prompt=prompt, system_prompt=system_prompt, temperature=0.0)
        if not res.content:
            return None

        # Clean JSON markdown fences
        clean_json = res.content.strip()
        if clean_json.startswith("```"):
            clean_json = re.sub(r"^```(?:json)?\n", "", clean_json)
            clean_json = re.sub(r"\n```$", "", clean_json)

        data = json.loads(clean_json)
        raw_intent = data.get("intent", "").upper()

        if raw_intent in IntentType.__members__:
            return ParsedIntent(
                intent=IntentType(raw_intent),
                amount=data.get("amount"),
                category=data.get("category"),
                change_amount=data.get("change_amount"),
                income_shock_percentage=data.get("income_shock_percentage") or 0.0,
                unexpected_expense=data.get("unexpected_expense") or 0.0,
                horizon_months=data.get("horizon_months"),
                target_goal_amount=data.get("target_goal_amount"),
                target_goal_months=data.get("target_goal_months"),
            )
        return None

    def _parse_deterministic(self, message: str, history: Optional[List[Dict[str, str]]] = None) -> ParsedIntent:
        msg = message.lower().strip()

        # ------------------------------------------------------------------
        # Extract numeric amounts (handle currency symbols ₹, $, €, commas)
        # ------------------------------------------------------------------
        amount: Optional[float] = None
        amounts = re.findall(r'[\d,]+(?:\.\d+)?', msg)
        if amounts:
            for cand in amounts:
                try:
                    val = float(cand.replace(',', ''))
                    # Exclude typical month counts like 6 in "6 months" unless it's a stand-alone amount
                    if val > 0:
                        amount = val
                        break
                except ValueError:
                    pass

        # Percentage detection (e.g. 20% salary drop)
        pct_match = re.search(r'(\d+(?:\.\d+)?)\s*%', msg)
        pct_val = float(pct_match.group(1)) / 100.0 if pct_match else 0.0

        # Month horizon detection (e.g. "in six months", "6 months")
        month_word_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "twelve": 12}
        horizon = None
        m_match = re.search(r'(\d+)\s*months?', msg)
        if m_match:
            horizon = int(m_match.group(1))
        else:
            for word, n in month_word_map.items():
                if f"{word} month" in msg:
                    horizon = n
                    break

        # ------------------------------------------------------------------
        # Missing data clarification queries
        # e.g. "Which information do you need to make this recommendation reliable?"
        # ------------------------------------------------------------------
        if (
            "which information" in msg
            or "what information" in msg
            or "data do you need" in msg
            or "make this recommendation reliable" in msg
            or "reliable" in msg and "need" in msg
        ):
            return ParsedIntent(intent=IntentType.MISSING_DATA_CLARIFICATION)

        # ------------------------------------------------------------------
        # Plan evaluation & Strategy comparison
        # e.g. "Which plan protects my emergency reserve best?", "Compare two repayment or savings strategies."
        # ------------------------------------------------------------------
        plan_keywords = [
            "which plan", "compare two", "compare plan", "repayment or savings strategies",
            "protects my emergency reserve", "protects my reserve", "best plan", "action plan",
            "action sequence", "compare strategies"
        ]
        if any(kw in msg for kw in plan_keywords):
            return ParsedIntent(
                intent=IntentType.PLAN_EVALUATION,
                horizon_months=horizon or 6
            )

        # ------------------------------------------------------------------
        # Goal feasibility
        # e.g. "Can I reach my savings goal in six months?", "Can I reach my goal"
        # ------------------------------------------------------------------
        goal_keywords = ["reach my savings goal", "reach my goal", "savings goal", "save for my goal"]
        if any(kw in msg for kw in goal_keywords):
            return ParsedIntent(
                intent=IntentType.GOAL_FEASIBILITY,
                target_goal_amount=amount,
                target_goal_months=horizon or 6,
                horizon_months=horizon or 6
            )

        # ------------------------------------------------------------------
        # What-if scenarios & Shocks
        # e.g. "What happens if my salary drops by 20%?", "What if I have an unexpected medical expense?"
        # ------------------------------------------------------------------
        is_what_if = False
        what_if_phrases = ["what happens if", "what if", "if my salary", "if i spend"]
        if any(kw in msg for kw in what_if_phrases):
            is_what_if = True
        elif ("spend" in msg or "spending" in msg or "expenses" in msg) and any(w in msg for w in ["less", "more", "increase", "decrease", "reduce", "cut", "lower", "drop"]):
            is_what_if = True
        elif ("income" in msg or "salary" in msg or "earn" in msg) and any(w in msg for w in ["less", "more", "increase", "decrease", "reduce", "cut", "lower", "drop", "raise"]):
            is_what_if = True
            
        if is_what_if:
            category = None
            if "eating out" in msg or "dining" in msg:
                category = "eating out"
            elif "shopping" in msg:
                category = "shopping"
            elif "food" in msg or "groceries" in msg:
                category = "food"

            # Salary drop / income shock
            if "income" in msg or "salary" in msg or "earn" in msg:
                if pct_val > 0:
                    is_inc = any(w in msg for w in ["more", "increase", "raise", "higher"])
                    shock = pct_val if is_inc else -pct_val
                    return ParsedIntent(
                        intent=IntentType.WHAT_IF,
                        income_shock_percentage=shock,
                        category="salary"
                    )
                elif "unexpected" not in msg and "expense" not in msg:
                    # Current schema cannot represent absolute income changes safely, and we shouldn't silently guess 20%.
                    return ParsedIntent(intent=IntentType.UNKNOWN)

            # Unexpected expense (e.g. medical, car repair)
            if "unexpected" in msg or "medical expense" in msg or "emergency expense" in msg:
                expense_amt = amount if amount and amount > 0 else 500.0
                return ParsedIntent(
                    intent=IntentType.WHAT_IF,
                    unexpected_expense=expense_amt,
                    category="medical"
                )

            # Spending direction: increase or decrease?
            is_increase = any(sig in msg for sig in ["more", "extra", "increase", "add", "higher", "raise"])
            is_decrease = any(sig in msg for sig in ["less", "cut", "reduce", "lower", "save", "fewer", "stop", "eliminate"])

            if is_increase and not is_decrease:
                change_amount = amount
            elif is_decrease and not is_increase:
                change_amount = -amount if amount is not None else None
            else:
                change_amount = -amount if amount is not None else None

            return ParsedIntent(
                intent=IntentType.WHAT_IF,
                change_amount=change_amount,
                category=category,
            )

        # ------------------------------------------------------------------
        # Affordability / Purchase questions
        # e.g. "Can I afford a phone worth ₹60,000 next month?", "Can I afford to spend 1302.4 in installments?"
        # ------------------------------------------------------------------
        affordability_keywords = [
            "afford", "buy", "purchase", "cost", "costing",
            "pay upfront", "installments", "phone", "iphone", "laptop", "car"
        ]
        if any(kw in msg for kw in affordability_keywords) and "what if" not in msg and "reach" not in msg:
            if "installment" in msg or "emi" in msg:
                return ParsedIntent(intent=IntentType.AFFORDABILITY_CHECK, amount=amount)
            return ParsedIntent(intent=IntentType.AFFORDABILITY_CHECK, amount=amount)

        # ------------------------------------------------------------------
        # Spending analysis
        # e.g. "How much did I spend on food last month?", "where is most of my money going"
        # ------------------------------------------------------------------
        spending_keywords = ["how much did i spend", "where is most of my money going", "spending", "spend on", "expense on"]
        if any(kw in msg for kw in spending_keywords):
            cat = None
            for c in ["food", "groceries", "eating out", "dining", "rent", "shopping", "travel", "entertainment", "transport"]:
                if c in msg:
                    cat = c
                    break
            return ParsedIntent(intent=IntentType.SPENDING_ANALYSIS, category=cat)

        # ------------------------------------------------------------------
        # Recommendations & Explanations
        # e.g. "Why are you recommending that I reduce shopping?", "How can I improve"
        # ------------------------------------------------------------------
        rec_keywords = [
            "why are you recommending", "why do you recommend", "why reduce",
            "recommendation", "improve my finances", "what should i do"
        ]
        if any(kw in msg for kw in rec_keywords):
            cat = None
            for c in ["shopping", "dining", "entertainment", "eating out"]:
                if c in msg:
                    cat = c
                    break
            return ParsedIntent(intent=IntentType.RECOMMENDATION, category=cat)

        # ------------------------------------------------------------------
        # Cash-flow forecast
        # e.g. "What does next month look like?", "cash flow forecast", "enough money"
        # ------------------------------------------------------------------
        if (
            "next month" in msg
            or "cash flow" in msg
            or "forecast" in msg
            or "future income" in msg
            or "enough money" in msg
        ) and "bitcoin" not in msg and "crypto" not in msg:
            return ParsedIntent(
                intent=IntentType.CASH_FLOW_FORECAST,
                horizon_months=horizon or 6
            )

        # ------------------------------------------------------------------
        # Financial summary
        # ------------------------------------------------------------------
        if "finances" in msg or "summary" in msg or "overview" in msg or "balance" in msg:
            return ParsedIntent(intent=IntentType.FINANCIAL_SUMMARY)

        # ------------------------------------------------------------------
        # Unknown intent
        # ------------------------------------------------------------------
        return ParsedIntent(intent=IntentType.UNKNOWN)
