"""
Artha AI Grounded Response Generator
====================================
Translates verified deterministic tool results into explainable, structured responses.
Distinguishes:
A. OBSERVED FACTS
B. FORECASTS (with horizon, uncertainty, reserve breach probability)
C. RECOMMENDATIONS
D. ASSUMPTIONS
E. CONFIDENCE AND LIMITATIONS

If an external LLM is configured, synthesizes grounded narrative.
Otherwise, produces deterministic Markdown reports with exact formatting.
"""

from typing import Dict, Any, List, Optional
import json
from app.schemas.copilot import ParsedIntent, IntentType
from app.copilot.provider import BaseLLMProvider


def _fmt(value: Any, currency: str = "") -> str:
    """Format a numeric value as a readable currency string with correct symbol."""
    if value is None:
        return "N/A"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value)

    symbols = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "ZAR": "R",
        "IDR": "Rp",
    }
    sym = symbols.get(currency.upper(), f"{currency} " if currency else "")

    if abs(v) >= 1_000_000:
        return f"{sym}{v:,.0f}"
    elif abs(v) >= 1_000:
        return f"{sym}{v:,.2f}"
    else:
        return f"{sym}{v:.2f}"


class StructuredFinancialExplanation:
    def __init__(
        self,
        direct_answer: str,
        observed_facts: List[str],
        forecast_details: Optional[Dict[str, Any]] = None,
        recommendations: Optional[List[str]] = None,
        assumptions: Optional[List[str]] = None,
        limitations: Optional[List[str]] = None,
        trade_offs: Optional[List[str]] = None,
    ):
        self.direct_answer = direct_answer
        self.observed_facts = observed_facts
        self.forecast_details = forecast_details or {}
        self.recommendations = recommendations or []
        self.assumptions = assumptions or []
        self.limitations = limitations or []
        self.trade_offs = trade_offs or []

    def to_markdown(self) -> str:
        parts = [self.direct_answer.strip(), ""]

        if self.observed_facts:
            parts.append("### A. Observed Facts")
            for fact in self.observed_facts:
                parts.append(f"• {fact}")
            parts.append("")

        if self.forecast_details:
            parts.append("### B. Forecast & Projections")
            for k, v in self.forecast_details.items():
                parts.append(f"• **{k}**: {v}")
            parts.append("")

        if self.trade_offs:
            parts.append("### C. Risks & Trade-Offs")
            for to in self.trade_offs:
                parts.append(f"• {to}")
            parts.append("")

        if self.recommendations:
            parts.append("### D. Recommendations & Actionable Steps")
            for rec in self.recommendations:
                parts.append(f"• {rec}")
            parts.append("")

        if self.assumptions:
            parts.append("### E. Assumptions")
            for asm in self.assumptions:
                parts.append(f"• {asm}")
            parts.append("")

        if self.limitations:
            parts.append("### F. Confidence & Limitations")
            for lim in self.limitations:
                parts.append(f"• {lim}")

        return "\n".join(parts).strip()


class ResponseGenerator:
    def __init__(self, provider: Optional[BaseLLMProvider] = None):
        self.provider = provider

    def generate(
        self,
        parsed: ParsedIntent,
        result: Dict[str, Any],
        currency: str = "",
        user_message: str = "",
    ) -> str:
        """
        Returns natural language / markdown response string.
        """
        explanation = self._build_structured_explanation(parsed, result, currency)

        if self.provider and self.provider.is_available() and not getattr(self.provider, "is_fallback", False):
            try:
                narrative = self._generate_with_llm(user_message, explanation, currency)
                if narrative:
                    return narrative
            except Exception:
                pass

        return explanation.to_markdown()

    def get_components(
        self,
        parsed: ParsedIntent,
        result: Dict[str, Any],
        currency: str = "",
    ) -> Dict[str, Any]:
        """
        Returns the structured breakdown dictionary for API schemas.
        """
        explanation = self._build_structured_explanation(parsed, result, currency)
        return {
            "direct_answer": explanation.direct_answer,
            "observed_facts": explanation.observed_facts,
            "forecast_details": explanation.forecast_details,
            "recommendations": explanation.recommendations,
            "assumptions": explanation.assumptions,
            "limitations": explanation.limitations,
            "trade_offs": explanation.trade_offs,
        }

    def _generate_with_llm(
        self,
        user_query: str,
        explanation: StructuredFinancialExplanation,
        currency: str,
    ) -> Optional[str]:
        system_prompt = (
            "You are Artha AI, the Financial Health Copilot for FIN4YOU. "
            "You explain verified financial facts clearly, empathetically, and accurately.\n"
            "CRITICAL RULES:\n"
            "1. NEVER invent balances, dates, interest rates, or financial statistics.\n"
            "2. Preserve all numbers and currency amounts exactly as provided in the grounded facts.\n"
            "3. Clearly distinguish between Observed Facts, Forecasts, Recommendations, and Assumptions.\n"
            "4. Never say a plan is safe if there is a reserve breach risk.\n"
            "5. Structure the response clearly with bullet points and bold highlights."
        )

        facts_json = {
            "direct_answer": explanation.direct_answer,
            "observed_facts": explanation.observed_facts,
            "forecast_details": explanation.forecast_details,
            "risks_and_trade_offs": explanation.trade_offs,
            "recommendations": explanation.recommendations,
            "assumptions": explanation.assumptions,
            "limitations": explanation.limitations,
        }

        prompt = (
            f"User Question: \"{user_query}\"\n\n"
            f"Verified Grounded Data:\n{json.dumps(facts_json, indent=2)}\n\n"
            f"Please generate the complete, beautifully formatted response."
        )

        res = self.provider.generate(prompt=prompt, system_prompt=system_prompt, temperature=0.1)
        return res.content if res.content else None

    def _build_structured_explanation(
        self,
        parsed: ParsedIntent,
        res: Dict[str, Any],
        currency: str,
    ) -> StructuredFinancialExplanation:
        intent = parsed.intent

        # ------------------------------------------------------------------
        # UNKNOWN / UNSUPPORTED
        # ------------------------------------------------------------------
        if intent == IntentType.UNKNOWN:
            return StructuredFinancialExplanation(
                direct_answer=(
                    "I can help you with questions about your finances. Try asking me about:\n"
                    "• Your spending breakdown or cash flow\n"
                    "• Whether you can afford a purchase\n"
                    "• What your next month looks like\n"
                    "• What happens if you change your spending\n"
                    "• Personalized recommendations"
                ),
                observed_facts=[],
                recommendations=[
                    "Ask: 'Can I afford a phone worth ₹60,000 next month?'",
                    "Ask: 'What happens if my salary drops by 20%?'",
                    "Ask: 'Which plan protects my emergency reserve best?'",
                    "Ask: 'How much did I spend on food last month?'"
                ],
                assumptions=[],
                limitations=["Artha AI answers personal finance questions based on your verified transactions and profile."],
            )

        # ------------------------------------------------------------------
        # INSUFFICIENT DATA
        # ------------------------------------------------------------------
        if res.get("status") == "INSUFFICIENT_DATA":
            return StructuredFinancialExplanation(
                direct_answer="I don't have enough historical data (minimum 3 months required) to confidently analyze that for you.",
                observed_facts=[
                    f"Current account currency: {currency}",
                    "Available transaction records are below the minimum 3-month requirement."
                ],
                recommendations=["Connect additional bank statements or sync past transactions to unlock forecasting."],
                assumptions=[],
                limitations=["A minimum of 3 consecutive monthly cycles is required to estimate cash flow trends accurately."],
            )

        # ------------------------------------------------------------------
        # MISSING DATA CLARIFICATION
        # ------------------------------------------------------------------
        if intent == IntentType.MISSING_DATA_CLARIFICATION:
            return StructuredFinancialExplanation(
                direct_answer="To make personalized recommendations 100% reliable, Artha AI requires four verified inputs:",
                observed_facts=[
                    "Historical settled transactions (minimum 3 full monthly billing cycles)",
                    f"Current liquid balance (currently on file: {_fmt(res.get('current_balance'), currency)})",
                    f"Declared safety buffer (currently on file: {_fmt(res.get('minimum_buffer'), currency)})",
                    "List of fixed debt payments and essential obligations"
                ],
                recommendations=[
                    "Keep your safety buffer updated in your profile settings.",
                    "Tag recurring obligations (rent, EMIs, insurance) so they are carried forward into projections."
                ],
                assumptions=["Without declared buffers, recommendations default to standard liquidity thresholds."],
                limitations=["Recommendations cannot predict unlisted loans, cash transactions, or volatile bonus income."]
            )

        # ------------------------------------------------------------------
        # AFFORDABILITY CHECK
        # ------------------------------------------------------------------
        if intent in [IntentType.AFFORDABILITY_CHECK, IntentType.PAYMENT_OPTION_ANALYSIS]:
            status = res.get("affordability_status", "")
            amt = res.get("purchase_amount") or parsed.amount or 0.0
            amt_str = _fmt(amt, currency)
            bal = res.get("resulting_balance", 0.0)
            bal_str = _fmt(bal, currency)
            cur_bal = res.get("current_balance", 0.0)
            min_buf = res.get("minimum_buffer", 0.0)
            shortfall = res.get("shortfall", 0.0)
            trade_off = res.get("trade_off_required", 0.0)
            options = res.get("viable_options", [])

            if status == "AFFORDABLE":
                direct = (
                    f"Yes, {amt_str} is affordable as a full payment based on your current projections.\n\n"
                    f"After this purchase, your projected balance would be {bal_str}, "
                    f"which remains above your required safety buffer."
                )
            elif status == "POTENTIALLY AFFORDABLE WITH TRADE-OFF":
                direct = (
                    f"{amt_str} is potentially affordable, but requires a trade-off.\n\n"
                    f"Your projected balance after a full purchase would be {bal_str}. "
                    f"You would need to reduce discretionary spending by {_fmt(trade_off, currency)} to stay above your minimum buffer."
                )
            else:
                direct = (
                    f"No, {amt_str} is not affordable as a single upfront payment under your current projection.\n\n"
                    f"This purchase would bring your projected balance to {bal_str}, "
                    f"which breaches your required minimum buffer."
                )

            facts = [
                f"Current available balance: {_fmt(cur_bal, currency)}",
                f"Declared minimum reserve buffer: {_fmt(min_buf, currency)}",
                f"Projected next-month net cash flow: {_fmt(res.get('projected_net_cash_flow', 0.0), currency)}"
            ]

            trade_offs = []
            if shortfall > 0:
                trade_offs.append(f"An upfront purchase leaves a projected balance of {bal_str}, breaching your buffer by {_fmt(shortfall, currency)}.")
            else:
                trade_offs.append(f"Projected balance remains at {bal_str}, safely above your minimum reserve of {_fmt(min_buf, currency)}.")

            recs = []
            if options:
                opt_bullets = []
                for idx, o in enumerate(options[:3], 1):
                    n = o.get("number_of_payments", 1)
                    pmt = _fmt(o.get("payment_amount", 0), currency)
                    tot = _fmt(o.get("total_payable_amount", 0), currency)
                    method = o.get("payment_method", "installment")
                    if n == 1:
                        opt_bullets.append(f"Option {idx}: Full payment of {pmt} ({method})")
                    else:
                        opt_bullets.append(f"Option {idx}: {n} x {pmt}/installment, total {tot} ({method})")
                recs.append("Here are some affordable alternatives (EMI/Installments) that maintain your safety buffer:\n  " + "\n  ".join(opt_bullets))
            elif status != "AFFORDABLE":
                recs.append("Consider postponing this purchase until your cash reserve grows, or negotiate an extended installment plan.")

            return StructuredFinancialExplanation(
                direct_answer=direct,
                observed_facts=facts,
                trade_offs=trade_offs,
                recommendations=recs,
                assumptions=["Assumes variable living expenses remain consistent with your 3-month trailing average."],
                limitations=["Affordability is evaluated against declared cash buffers and known obligations only."]
            )

        # ------------------------------------------------------------------
        # WHAT-IF SIMULATION
        # ------------------------------------------------------------------
        if intent == IntentType.WHAT_IF:
            sc_type = res.get("scenario_type", "spending_reduction")
            bal = res.get("projected_balance", 0.0)
            bal_str = _fmt(bal, currency)
            cf_change = res.get("cash_flow_change", 0.0)
            buf_status = res.get("buffer_status_change", "maintained")
            shortfall_prob = res.get("shortfall_probability", 0.0)

            status_map = {
                "maintained": "Your minimum buffer would be maintained.",
                "breached": "This would breach your minimum balance buffer.",
                "restored": "This would restore your minimum balance buffer.",
                "improved_but_still_breached": "This improves your position but the buffer remains breached.",
                "worsened_breach": "This would further worsen your buffer breach.",
            }
            status_text = status_map.get(buf_status, f"Buffer status: {buf_status}")

            if sc_type == "income_or_expense_shock":
                shock_pct = res.get("income_shock_percentage", 0.0)
                unexp_exp = res.get("unexpected_expense", 0.0)
                if shock_pct < 0:
                    direct = f"If your salary drops by {abs(shock_pct):.0%}, your projected balance would be {bal_str}. {status_text}"
                elif unexp_exp > 0:
                    direct = f"If you have an unexpected expense of {_fmt(unexp_exp, currency)}, your projected balance would be {bal_str}. {status_text}"
                else:
                    direct = f"Under this scenario, your projected balance would be {bal_str}. {status_text}"
            elif sc_type == "spending_reduction":
                chg = res.get("change_amount", 0.0)
                direct = f"If you reduce spending by {_fmt(chg, currency)}, your projected balance would be {bal_str}. {status_text}"
            elif sc_type == "spending_increase":
                chg = res.get("change_amount", 0.0)
                direct = f"If you increase spending by {_fmt(chg, currency)}, your projected balance would be {bal_str}. {status_text}"
            else:
                direct = f"Here is your baseline financial projection.\n\nYour projected balance would be {bal_str}. {status_text}"

            facts = [
                f"Current available balance: {_fmt(res.get('baseline_balance'), currency)}",
                f"Declared minimum buffer: {_fmt(res.get('minimum_buffer'), currency)}",
                f"Baseline monthly net cash flow: {_fmt(res.get('baseline_cash_flow'), currency)}"
            ]

            fc_details = {
                "Scenario Net Cash Flow": _fmt(res.get("scenario_cash_flow"), currency),
                "Projected Balance": bal_str,
                "Net Cash Flow Change": _fmt(cf_change, currency),
            }
            if shortfall_prob > 0:
                fc_details["Reserve Breach Probability"] = f"{shortfall_prob:.1%}"

            trade_offs = [
                f"Buffer status: {status_text}"
            ]

            recs = []
            if buf_status in ["breached", "worsened_breach"]:
                recs.append("Mitigate shortfall risk by immediately reducing discretionary spending or activating contingency reserves.")
            else:
                recs.append("This scenario maintains financial stability without breaching your declared reserve buffer.")

            return StructuredFinancialExplanation(
                direct_answer=direct,
                observed_facts=facts,
                forecast_details=fc_details,
                trade_offs=trade_offs,
                recommendations=recs,
                assumptions=["Simulation assumes all other income and non-discretionary obligations remain unchanged."],
                limitations=["Stochastic shock analysis applies one shock parameter at a time."]
            )

        # ------------------------------------------------------------------
        # PLAN EVALUATION & STRATEGY COMPARISON
        # ------------------------------------------------------------------
        if intent in [IntentType.PLAN_EVALUATION, IntentType.GOAL_FEASIBILITY]:
            rec_plan_id = res.get("recommended_plan_id", "")
            rationale = res.get("recommendation_rationale", "")
            plans = res.get("plans", [])

            direct = f"Recommendation: The safest plan is **{rec_plan_id.replace('_', ' ').title()}**.\n{rationale}"

            facts = [
                f"Starting available balance: {_fmt(res.get('current_balance'), currency)}",
                f"Declared minimum reserve: {_fmt(res.get('declared_minimum_reserve'), currency)}",
                f"Planning horizon: {res.get('horizon_months', 6)} monthly periods"
            ]

            fc_details = {}
            for p in plans:
                p_name = p.get("name", p.get("plan_id"))
                shortfall_p = p.get("shortfall_probability", 0.0)
                ending_b = _fmt(p.get("ending_balance", 0.0), currency)
                fc_details[f"{p_name} Balance & Risk"] = f"Ending Balance: {ending_b} | Shortfall Risk: {shortfall_p:.1%}"

            trade_offs = []
            for p in plans:
                if not p.get("is_feasible"):
                    trade_offs.append(f"**{p.get('name')}**: Infeasible under constraints. Max reserve breach: {_fmt(p.get('max_shortfall'), currency)}.")
                else:
                    trade_offs.append(f"**{p.get('name')}**: Feasible. Trims {_fmt(p.get('total_discretionary_trimmed'), currency)} discretionary spend over horizon.")

            recs = [
                f"Adopt {rec_plan_id.replace('_', ' ').title()} to minimize reserve breach risk while making steady progress.",
                "Review plan milestones at the end of each monthly period."
            ]

            return StructuredFinancialExplanation(
                direct_answer=direct,
                observed_facts=facts,
                forecast_details=fc_details,
                trade_offs=trade_offs,
                recommendations=recs,
                assumptions=["Evaluated using rolling-origin backtested probabilistic cash-flow models across 6 months."],
                limitations=["Assumes candidate action sequence is adhered to each month without unannounced obligations."]
            )

        # ------------------------------------------------------------------
        # SPENDING ANALYSIS
        # ------------------------------------------------------------------
        if intent == IntentType.SPENDING_ANALYSIS:
            tot = res.get("total_expenses", 0.0)
            ess = res.get("essential_expenses", 0.0)
            disc = res.get("discretionary_expenses", 0.0)
            q_cat = res.get("queried_category")
            q_amt = res.get("queried_category_amount")

            if q_cat and q_amt is not None:
                direct = f"You spent {_fmt(q_amt, currency)} on {q_cat.title()} based on historical transactions."
            else:
                direct = (
                    f"Spending Analysis:\n\n"
                    f"Your total expenses were {_fmt(tot, currency)}, split into {_fmt(ess, currency)} essential and {_fmt(disc, currency)} discretionary."
                )

            facts = [
                f"Total analyzed expenses: {_fmt(tot, currency)}",
                f"Essential expenses (fixed/debt/living): {_fmt(ess, currency)}",
                f"Discretionary expenses (variable/lifestyle): {_fmt(disc, currency)}",
            ]
            top_cats = res.get("top_categories", [])
            if top_cats:
                facts.append("Top categories: " + ", ".join([f"{c['category']}: {_fmt(c['total_amount'], currency)}" for c in top_cats[:3]]))

            recs = [
                "Review high discretionary categories on the Insights page to identify sustainable savings opportunities."
            ]

            return StructuredFinancialExplanation(
                direct_answer=direct,
                observed_facts=facts,
                recommendations=recs,
                assumptions=["Transactions categorized by deterministic ML model and merchant rules."],
                limitations=["Transactions missing descriptions default to 'unknown' category."]
            )

        # ------------------------------------------------------------------
        # CASH FLOW FORECAST
        # ------------------------------------------------------------------
        if intent == IntentType.CASH_FLOW_FORECAST:
            pcf = res.get("projected_cash_flow", 0.0)
            bal = res.get("projected_balance", 0.0)
            p_inc = res.get("projected_income", 0.0)
            p_exp = res.get("projected_expenses", 0.0)
            peak_risk = res.get("peak_shortfall_probability", 0.0)
            dir_str = "positive" if pcf >= 0 else "negative"

            direct = (
                f"Next Month Forecast:\n\n"
                f"Projected net cash flow: {_fmt(pcf, currency)} ({dir_str}). "
                f"Projected balance: {_fmt(bal, currency)}. "
                f"See the Forecast page for the full income, expenses, and obligations breakdown."
            )

            facts = [
                f"Current liquid balance: {_fmt(res.get('minimum_buffer'), currency)} buffer threshold on file.",
                f"Projected Monthly Income: {_fmt(p_inc, currency)}",
                f"Projected Monthly Expenses & Obligations: {_fmt(p_exp, currency)}"
            ]

            fc_details = {
                "Forecast Horizon": f"{res.get('horizon_months', 6)} months",
                "Projected Monthly Net Cash Flow": _fmt(pcf, currency),
                "Projected Cumulative Balance": _fmt(bal, currency),
                "Peak Reserve Breach Risk": f"{peak_risk:.1%}"
            }

            metrics = res.get("evaluation_metrics")
            if metrics:
                fc_details["Historical Backtest Accuracy"] = (
                    f"MAE: {_fmt(metrics.get('expense_mae'), currency)} | "
                    f"Interval Coverage: {metrics.get('interval_coverage'):.1%}"
                )

            trade_offs = [
                "Reserve breach risk is " + ("negligible (<5%)" if peak_risk < 0.05 else f"elevated ({peak_risk:.1%})")
            ]

            recs = [
                "Maintain your planned savings rate to keep projected balances well above the buffer."
            ]

            return StructuredFinancialExplanation(
                direct_answer=direct,
                observed_facts=facts,
                forecast_details=fc_details,
                trade_offs=trade_offs,
                recommendations=recs,
                assumptions=["Moving-average and historical mean trends carried forward."],
                limitations=["Forecast cannot predict discretionary windfalls or emergency liabilities."]
            )

        # ------------------------------------------------------------------
        # RECOMMENDATION EXPLANATION
        # ------------------------------------------------------------------
        if intent == IntentType.RECOMMENDATION:
            rec_text = res.get("recommendation_text", "Your finances are on track.")
            direct = f"**Recommendation:** {rec_text}"

            facts = []
            if res.get("observed_fact"):
                facts.append(res.get("observed_fact"))

            fc_details = {}
            if res.get("calculation"):
                fc_details["Calculation"] = res.get("calculation")
            if res.get("prediction"):
                fc_details["Model Prediction"] = res.get("prediction")

            trade_offs = []
            if res.get("simulation"):
                trade_offs.append(res.get("simulation"))

            recs = [rec_text]

            return StructuredFinancialExplanation(
                direct_answer=direct,
                observed_facts=facts,
                forecast_details=fc_details,
                trade_offs=trade_offs,
                recommendations=recs,
                assumptions=["Recommendations derived deterministically by DecisionEngine."],
                limitations=["Confidence is evaluated based on data completeness and reserve margins."]
            )

        # ------------------------------------------------------------------
        # FINANCIAL SUMMARY
        # ------------------------------------------------------------------
        bal = res.get("current_balance", 0.0)
        cf = res.get("net_cash_flow", 0.0)
        cf_dir = "positive" if cf >= 0 else "negative"
        direct = (
            f"Financial Summary:\n\n"
            f"Your current available balance is {_fmt(bal, currency)}. "
            f"Your historical net cash flow is {_fmt(cf, currency)} ({cf_dir}). "
            f"Check the Insights and Forecast pages for a complete breakdown."
        )
        facts = [
            f"Current available balance: {_fmt(bal, currency)}",
            f"Minimum buffer threshold: {_fmt(res.get('minimum_buffer'), currency)}",
            f"Total income: {_fmt(res.get('total_income'), currency)}",
            f"Total expenses: {_fmt(res.get('total_expenses'), currency)}",
            f"Savings rate: {res.get('savings_rate', 0.0):.1%}",
        ]
        return StructuredFinancialExplanation(
            direct_answer=direct,
            observed_facts=facts,
            recommendations=["Monitor upcoming recurring obligations on the Forecast page."],
            assumptions=[],
            limitations=["Based on historical transaction log."]
        )
