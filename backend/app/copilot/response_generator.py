from app.schemas.copilot import ParsedIntent, IntentType
from typing import Dict, Any

def _fmt(value, currency: str = '') -> str:
    """Format a numeric value as a readable currency string."""
    if value is None:
        return 'N/A'
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value)
    
    symbols = {'EUR': '€', 'USD': '$', 'ZAR': 'R', 'IDR': 'Rp', 'INR': '₹'}
    sym = symbols.get((currency or 'INR').upper(), '₹')
    
    if abs(v) >= 1_000_000:
        return f"{sym}{v:,.0f}"
    elif abs(v) >= 1_000:
        return f"{sym}{v:,.2f}"
    else:
        return f"{sym}{v:.2f}"

class ResponseGenerator:
    """
    Translates deterministic financial results into clear, formatted natural language.
    All numeric values are formatted — no raw floating-point output.
    """
    def generate(self, parsed: ParsedIntent, result: Dict[str, Any], currency: str = '') -> str:
        if parsed.intent == IntentType.UNKNOWN:
            return (
                "I can help you with questions about your finances. Try asking me about:\n"
                "• Your spending breakdown or cash flow\n"
                "• Whether you can afford a purchase\n"
                "• What your next month looks like\n"
                "• What happens if you change your spending\n"
                "• Personalized recommendations"
            )

        if result.get("status") == "INSUFFICIENT_DATA":
            return "I don't have enough historical data (minimum 3 months required) to confidently analyze that for you."

        if parsed.intent == IntentType.AFFORDABILITY_CHECK:
            aff_status = result.get("affordability_status", "")
            bal = result.get("resulting_balance", 0)
            trade_off = result.get("trade_off", 0)
            amount_str = _fmt(parsed.amount, currency)
            bal_str = _fmt(bal, currency)
            
            opts = result.get("viable_options", [])
            opt_text = ""
            if opts:
                opt_lines = []
                for i, o in enumerate(opts[:3], 1):
                    n = o.get('number_of_payments', 1)
                    pmt = _fmt(o.get('payment_amount', 0), currency)
                    method = o.get('payment_method', 'payment')
                    if n == 1:
                        opt_lines.append(f"• Option {i}: Full payment of {pmt} ({method})")
                    else:
                        opt_lines.append(f"• Option {i}: {n} x {pmt}/mo ({method})")
                
                opt_text = (
                    f"\n\nHere are some affordable alternatives (EMI/Installments) that maintain your safety buffer:\n"
                    + "\n".join(opt_lines)
                )

            if aff_status == "AFFORDABLE":
                return (
                    f"Yes, {amount_str} is affordable as a full payment based on your current projections.\n\n"
                    f"After this purchase, your projected balance would be {bal_str}, "
                    f"which remains above your required safety buffer.{opt_text}"
                )
            elif aff_status == "POTENTIALLY AFFORDABLE WITH TRADE-OFF":
                trade_str = _fmt(trade_off, currency)
                return (
                    f"{amount_str} is potentially affordable, but requires a trade-off.\n\n"
                    f"Your projected balance after a full purchase would be {bal_str}. "
                    f"You would need to reduce discretionary spending by {trade_str} to stay above your minimum buffer.{opt_text}"
                )
            else:
                trace_text = (
                    f"\n\n**Decision Trace:**\n"
                    f"• **Observed:** Current Balance is {result.get('current_balance', 0)}, Minimum Buffer is {result.get('minimum_buffer', 0)}\n"
                    f"• **Prediction:** Projected net cash flow next month is {result.get('projected_cash_flow', 0)}\n"
                    f"• **Simulation:** Paying {amount_str} upfront leads to a projected balance of {bal_str}\n"
                    f"• **Impact:** Buffer breached (Shortfall: {result.get('shortfall', 0)})\n"
                )
                return (
                    f"No, {amount_str} is not affordable as a single upfront payment under your current projection.\n\n"
                    f"This purchase would bring your projected balance to {bal_str}, "
                    f"which breaches your required minimum buffer.{opt_text}{trace_text}"
                )

        elif parsed.intent == IntentType.PAYMENT_OPTION_ANALYSIS:
            opts = result.get("viable_options", [])
            amount_str = _fmt(parsed.amount, currency)
            if not opts:
                return (
                    f"No affordable installment plans were found for {amount_str}. "
                    f"The monthly payment for available options would breach your minimum balance buffer. "
                    f"Consider a smaller purchase or saving first."
                )
            opt_lines = []
            for i, o in enumerate(opts[:4], 1):
                n = o.get('number_of_payments', 1)
                pmt = _fmt(o.get('payment_amount', 0), currency)
                method = o.get('payment_method', 'payment')
                total = _fmt(o.get('total_payable_amount', 0), currency)
                if n == 1:
                    opt_lines.append(f"  Option {i}: Full payment of {pmt} ({method})")
                else:
                    opt_lines.append(f"  Option {i}: {n} x {pmt}/installment, total {total} ({method})")
            options_text = "\n".join(opt_lines)
            return (
                f"Here are the affordable installment options for {amount_str}:\n\n"
                f"{options_text}\n\n"
                f"All options above maintain your minimum balance buffer."
            )

        elif parsed.intent == IntentType.WHAT_IF:
            bal = result.get("projected_balance", 0)
            buf_status = result.get("buffer_status_change", "maintained")
            change_amount = result.get("change_amount", 0)
            scenario_type = result.get("scenario_type", "spending_reduction")
            bal_str = _fmt(bal, currency)
            change_str = _fmt(abs(change_amount), currency)

            status_map = {
                "maintained": "Your minimum buffer would be maintained.",
                "breached": "This would breach your minimum balance buffer.",
                "restored": "This would restore your minimum balance buffer.",
                "improved_but_still_breached": "This improves your position but the buffer remains breached.",
                "worsened_breach": "This would further worsen your buffer breach.",
            }
            status_text = status_map.get(buf_status, f"Buffer status: {buf_status}")

            if scenario_type == "spending_increase":
                action_text = f"If you increase spending by {change_str}"
            elif scenario_type == "spending_reduction":
                action_text = f"If you reduce spending by {change_str}"
            else:
                # no_change or unknown
                note = result.get("note", "")
                return (
                    f"Here is your baseline financial projection.\\n\\n"
                    f"Your projected balance would be {bal_str}. "
                    f"{status_text}"
                    + (f"\\n\\n{note}" if note else "")
                )

            return (
                f"{action_text}, "
                f"your projected balance would be {bal_str}. "
                f"{status_text}"
            )


        elif parsed.intent == IntentType.FINANCIAL_SUMMARY:
            bal = _fmt(result.get('balance', 0), currency)
            cf = result.get('cash_flow', 0)
            cf_str = _fmt(cf, currency)
            cf_dir = "positive" if cf >= 0 else "negative"
            return (
                f"Financial Summary:\n\n"
                f"Your current available balance is {bal}. "
                f"Your historical net cash flow is {cf_str} ({cf_dir}). "
                f"Check the Insights and Forecast pages for a complete breakdown."
            )

        elif parsed.intent == IntentType.RECOMMENDATION:
            rec_text = result.get("recommendation_text")
            if rec_text:
                trace_text = (
                    f"\n\n**Decision Trace:**\n"
                    f"• **Observed:** {result.get('observed_fact')}\n"
                    f"• **Calculation:** {result.get('calculation')}\n"
                    f"• **Prediction:** {result.get('prediction')}\n"
                    f"• **Simulation:** {result.get('simulation')}\n"
                    f"• **Confidence:** {result.get('confidence_level')} ({result.get('confidence_reason')})"
                )
                return f"**Recommendation:** {rec_text}{trace_text}"
            return "Your projected cash flow and buffer are within acceptable ranges. No critical action is required at this time."

        elif parsed.intent in [IntentType.CASH_FLOW_FORECAST, IntentType.FINANCIAL_FORECAST]:
            pcf = result.get('projected_cash_flow', 0)
            bal = result.get('projected_balance', 0)
            pcf_str = _fmt(pcf, currency)
            bal_str = _fmt(bal, currency)
            direction = "positive" if pcf >= 0 else "negative"
            return (
                f"Next Month Forecast:\n\n"
                f"Projected net cash flow: {pcf_str} ({direction}). "
                f"Projected balance: {bal_str}. "
                f"See the Forecast page for the full income, expenses, and obligations breakdown."
            )

        elif parsed.intent == IntentType.GREETING:
            return "Hey! Welcome to Fin4You. How can I help you manage your money today?"

        elif parsed.intent == IntentType.SAVING_PLAN:
            return (
                "### 4-Week Actionable Savings Plan\n\n"
                "Here is a structured blueprint to help you save money within one month:\n\n"
                "**Week 1: Audit & Cut Subscriptions**\n"
                "• Cancel unneeded subscriptions or streaming services.\n"
                "• Review food delivery and dining out expenses.\n\n"
                "**Week 2: Set Category Caps**\n"
                "• Cap discretionary spending (entertainment, impulse buys) by 20–30%.\n"
                "• Use cash or dedicated sub-accounts for daily spending.\n\n"
                "**Week 3: Reduce Recurring Bills**\n"
                "• Negotiate utility bills, internet plans, or insurance policies.\n"
                "• Cook meals at home and meal-prep for the week.\n\n"
                "**Week 4: Review & Automate Savings**\n"
                "• Transfer all savings into a high-yield savings account or emergency buffer.\n"
                "• Set up automatic payday transfers for future months."
            )

        elif parsed.intent == IntentType.BUDGETING:
            return (
                "### 50/30/20 Budgeting Rule\n\n"
                "• **50% Needs:** Essential bills (rent, utilities, groceries, transportation)\n"
                "• **30% Wants:** Discretionary spending (dining out, entertainment, hobbies)\n"
                "• **20% Savings:** Emergency buffer, debt paydown, or long-term investments\n\n"
                "Adjust these percentages based on your current financial goals."
            )

        elif parsed.intent == IntentType.BALANCE_QUERY:
            bal = _fmt(result.get("balance", 0), currency)
            buf = _fmt(result.get("minimum_buffer", 0), currency)
            return f"Your current available balance is **{bal}** (minimum safety buffer: {buf})."

        elif parsed.intent == IntentType.CASH_FLOW_QUERY:
            cf = _fmt(result.get("cash_flow", 0), currency)
            direction = "positive" if result.get("cash_flow", 0) >= 0 else "negative"
            return f"Your current net cash flow is **{cf}** ({direction})."

        elif parsed.intent == IntentType.INCOME_QUERY:
            inc = _fmt(result.get("income", 0), currency)
            return f"Your total monthly income is **{inc}**."

        elif parsed.intent == IntentType.EXPENSE_QUERY:
            exp = _fmt(result.get("expenses", 0), currency)
            ess = _fmt(result.get("essential_expenses", 0), currency)
            disc = _fmt(result.get("discretionary_expenses", 0), currency)
            return f"Your total monthly expenses are **{exp}** (Essential: {ess}, Discretionary: {disc})."

        elif parsed.intent == IntentType.GENERAL_FINANCE:
            return "Managing money effectively starts with tracking cash flow, maintaining a safety buffer, and setting clear monthly savings targets."

        elif parsed.intent == IntentType.GENERAL_CONVERSATION or parsed.intent == IntentType.CLARIFICATION:
            return "I am Artha AI, your Fin4You personal finance assistant. Ask me anything about your balance, cash flow, savings plans, or budgeting strategies!"

        return "Here is your financial analysis. See the details below."
