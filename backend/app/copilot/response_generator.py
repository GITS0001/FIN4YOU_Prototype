from app.schemas.copilot import ParsedIntent, IntentType
from typing import Dict, Any

class ResponseGenerator:
    """
    Translates deterministic financial results into natural language.
    In a full production environment, this calls an LLM with the structured data.
    For this MVP, it provides robust templated fallbacks based strictly on the data.
    """
    def generate(self, parsed: ParsedIntent, result: Dict[str, Any]) -> str:
        if parsed.intent == IntentType.UNKNOWN:
            return "I'm sorry, I cannot safely answer that question with your available financial data."

        if result.get("status") == "INSUFFICIENT_DATA":
            return "I don't have enough historical data to confidently analyze that for you."

        if parsed.intent == IntentType.AFFORDABILITY_CHECK:
            aff_status = result.get("affordability_status")
            if aff_status == "AFFORDABLE":
                return f"Yes, based on your projected cash flow and balance, spending {parsed.amount} is affordable."
            elif aff_status == "POTENTIALLY AFFORDABLE WITH TRADE-OFF":
                return f"You can afford {parsed.amount}, but it will require you to reduce your discretionary spending by {result.get('trade_off')} to maintain your safety buffer."
            else:
                return f"No, based on current projections, spending {parsed.amount} is not affordable because it would breach your minimum balance."
        
        elif parsed.intent == IntentType.PAYMENT_OPTION_ANALYSIS:
            opts = result.get("viable_options", [])
            if not opts:
                return f"I couldn't find any affordable installment plans for {parsed.amount}."
            opt_texts = [f"Option {o['payment_option_id']}: {o['number_of_payments']} payments of {o['payment_amount']}" for o in opts]
            return f"While paying upfront might be tight, you can afford these installment options:\n" + "\n".join(opt_texts)

        elif parsed.intent == IntentType.WHAT_IF:
            return f"If you change spending by {parsed.change_amount}, your projected balance becomes {result.get('projected_balance')}, which {result.get('buffer_status_change')} your buffer."

        elif parsed.intent == IntentType.FINANCIAL_SUMMARY:
            return f"Your current available balance is {result.get('balance')}. Last month you had {result.get('cash_flow')} in net cash flow."

        elif parsed.intent == IntentType.RECOMMENDATION:
            rec_text = result.get("recommendation_text")
            if rec_text:
                return rec_text
            return "Your finances look healthy. No immediate action required."

        elif parsed.intent == IntentType.CASH_FLOW_FORECAST:
            return f"Next month, you are projected to have {result.get('projected_cash_flow')} in cash flow. Your projected balance is {result.get('projected_balance')}."

        elif parsed.intent == IntentType.SPENDING_ANALYSIS:
            return "Based on your recent transactions, your largest discretionary spending areas are visible in your financial state."

        return "Here is your financial analysis."
