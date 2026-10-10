import re
from app.schemas.copilot import ParsedIntent, IntentType

class IntentParser:
    """
    Parses natural language queries into a structured ParsedIntent.
    Supports 12 distinct financial & conversational intent categories.
    """

    def parse(self, message: str) -> ParsedIntent:
        msg = message.lower().strip()

        # 1. Greetings (Hi, Hello, Hey, Good morning...)
        greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "howdy", "greetings"]
        if msg in greetings or any(msg.startswith(g + " ") or msg.startswith(g + "!") or msg.startswith(g + ",") for g in greetings if len(msg) < 15):
            return ParsedIntent(intent=IntentType.GREETING)

        # Extract numeric amounts
        amount: float | None = None
        amounts = re.findall(r'[\d,]+(?:\.\d+)?', msg)
        if amounts:
            try:
                amount = float(amounts[0].replace(',', ''))
            except ValueError:
                pass

        # 2. What-If scenarios
        what_if_keywords = ["what happens if", "what if"]
        if any(kw in msg for kw in what_if_keywords):
            category: str | None = None
            if "eating out" in msg or "dining" in msg:
                category = "Dining Out"

            increase_signals = ["spend more", "spend extra", "increase", "more on", "add", "higher", "raise"]
            decrease_signals = ["spend less", "cut", "reduce", "lower", "spend fewer", "stop", "eliminate"]

            is_increase = any(sig in msg for sig in increase_signals)
            is_decrease = any(sig in msg for sig in decrease_signals)

            if is_increase and not is_decrease:
                change_amount = amount
            elif is_decrease and not is_increase:
                change_amount = -amount if amount is not None else None
            else:
                change_amount = -amount if amount is not None else None

            return ParsedIntent(intent=IntentType.WHAT_IF, change_amount=change_amount, category=category)

        # 3. Affordability Check
        affordability_keywords = ["afford", "can i buy", "purchase", "costing", "pay upfront", "installment"]
        if any(kw in msg for kw in affordability_keywords) and "what if" not in msg:
            return ParsedIntent(intent=IntentType.AFFORDABILITY_CHECK, amount=amount)

        # 4. Account Specific Balance Query
        if any(kw in msg for kw in ["balance", "available balance", "how much money do i have", "my bank balance", "account balance"]):
            return ParsedIntent(intent=IntentType.BALANCE_QUERY)

        # 5. Account Specific Cash Flow Query
        if any(kw in msg for kw in ["cash flow", "my cash flow", "inflows and outflows", "inflow and outflow"]):
            return ParsedIntent(intent=IntentType.CASH_FLOW_QUERY)

        # 6. Account Specific Income Query
        if any(kw in msg for kw in ["my income", "salary payout", "how much do i earn", "total income"]):
            return ParsedIntent(intent=IntentType.INCOME_QUERY)

        # 7. Account Specific Expense Query / Reduction
        if any(kw in msg for kw in ["reduce unnecessary expenses", "cut expenses", "reduce expenses", "my expenses", "total expenses"]):
            return ParsedIntent(intent=IntentType.EXPENSE_QUERY)

        # 8. Savings Plan (e.g. "How can I save money in one month?")
        if any(kw in msg for kw in ["save money", "savings plan", "how to save", "save in 1 month", "save in one month", "how can i save", "build savings", "ways to save", "way to save"]):
            return ParsedIntent(intent=IntentType.SAVING_PLAN)

        # 9. Budgeting (e.g. "Help me create a monthly budget")
        if any(kw in msg for kw in ["create a budget", "monthly budget", "build a budget", "budgeting", "how to budget", "50/30/20", "budget"]):
            return ParsedIntent(intent=IntentType.BUDGETING)

        # 10. Spending Analysis
        if any(kw in msg for kw in ["spending pattern", "where is my money going", "spending breakdown", "my spending"]):
            return ParsedIntent(intent=IntentType.SPENDING_ANALYSIS)

        # 11. Financial Forecast
        if any(kw in msg for kw in ["next month forecast", "future balance", "runway", "forecast"]):
            return ParsedIntent(intent=IntentType.FINANCIAL_FORECAST)

        # 12. General Finance
        if any(kw in msg for kw in ["what is inflation", "interest rate", "how does interest work", "emergency fund definition"]):
            return ParsedIntent(intent=IntentType.GENERAL_FINANCE)

        # 13. Financial summary
        if "finances" in msg or "summary" in msg or "overview" in msg:
            return ParsedIntent(intent=IntentType.FINANCIAL_SUMMARY)

        # Default: General Conversation / Unknown
        return ParsedIntent(intent=IntentType.GENERAL_CONVERSATION)
