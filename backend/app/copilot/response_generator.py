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

    cur = (currency or "INR").upper()
    symbols = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "ZAR": "R",
        "IDR": "Rp",
    }
    sym = symbols.get(cur, "₹")

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
        parts = []
        if self.direct_answer:
            parts.append(self.direct_answer.strip())
            parts.append("")

        if self.observed_facts:
            parts.append("### 📊 Observed Facts")
            for fact in self.observed_facts:
                parts.append(f"• {fact}")
            parts.append("")

        if self.forecast_details:
            parts.append("### 🔮 Projections & Scenario Impact")
            for k, v in self.forecast_details.items():
                parts.append(f"• **{k}**: {v}")
            parts.append("")

        if self.trade_offs:
            parts.append("### ⚠️ Risks & Considerations")
            for to in self.trade_offs:
                parts.append(f"• {to}")
            parts.append("")

        if self.recommendations:
            has_questions = any("Ask:" in r or "“" in r or '"' in r for r in self.recommendations)
            if has_questions:
                parts.append("### 💬 Suggested Questions to Try")
            else:
                parts.append("### 💡 Recommended Next Steps")
            for rec in self.recommendations:
                parts.append(f"• {rec}")
            parts.append("")

        if self.assumptions:
            parts.append("### 📋 Assumptions")
            for asm in self.assumptions:
                parts.append(f"• {asm}")
            parts.append("")

        if self.limitations:
            parts.append("### ℹ️ Grounded Verification")
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
        cur_code = (currency or "INR").upper()
        symbols = {
            "INR": "₹",
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "ZAR": "R",
            "IDR": "Rp",
        }
        sym = symbols.get(cur_code, "₹")

        system_prompt = (
            "You are Artha AI, the Financial Health Copilot for FIN4YOU. "
            "You explain verified financial facts clearly, empathetically, and accurately.\n\n"
            "CRITICAL RULES:\n"
            f"1. CURRENCY LOCK: The user's active currency is {cur_code} with symbol '{sym}'. ALWAYS use '{sym}' (e.g. {sym}60,000) for all monetary amounts. STRICTLY NEVER use any other currency symbol such as ₦, $, €, etc.\n"
            "2. GROUNDED TRUTH: NEVER invent balances, dates, interest rates, or financial statistics. Preserve all numbers and amounts exactly as provided in the grounded facts.\n"
            "3. NO PLACEHOLDER TABLES: NEVER output markdown tables or sections with placeholder values like '(none provided yet)', '(none listed)', or '(none at this moment)'. If a section has no data, omit it completely.\n"
            "4. EXECUTIVE STRUCTURE: Format your response beautifully using clear Markdown sections with emojis:\n"
            "   - Lead with a clear, concise Executive Summary / Direct Answer.\n"
            "   - '### 📊 Observed Facts' (only if verified facts exist in the data).\n"
            "   - '### 🔮 Projections & Scenario Impact' (only if forecast/simulation details exist).\n"
            "   - '### ⚠️ Risks & Considerations' (only if risks or trade-offs exist).\n"
            "   - '### 💡 Recommendations & Next Steps' (actionable guidance).\n"
            "   - '### 💬 Sample Questions to Try' (when giving examples or guiding the user).\n"
            "5. If answering an introductory greeting or help request, provide a warm, structured onboarding guide highlighting your core capabilities with sample questions.\n"
            "6. Never say a plan is safe if there is a reserve breach risk."
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
            cur_code = (currency or "INR").upper()
            sym = "₹" if cur_code in ["INR", ""] else _fmt(0, currency)[0]
            return StructuredFinancialExplanation(
                direct_answer=(
                    "**Hello! I’m Artha AI — your Financial Health Copilot.**\n\n"
                    "I help you understand and manage your money with clear, factual answers grounded directly in your verified financial transactions and profile.\n\n"
                    "### 📌 What I Can Help You With\n"
                    "• **Spending Breakdown & Cash Flow**: Discover exactly where your money goes across essential vs. discretionary categories.\n"
                    "• **Affordability Analysis**: Test whether a major purchase or installment plan fits your budget without depleting your emergency reserve.\n"
                    "• **Next-Month Projections**: Forecast upcoming income, expenses, and net cash flow with probabilistic safety bounds.\n"
                    "• **What-If Simulations**: Stress-test your finances against salary shocks or explore the impact of cutting discretionary spend.\n"
                    "• **Personalized Strategy**: Compare plans to improve savings, accelerate debt payoff, and safeguard your minimum buffer."
                ),
                observed_facts=[],
                recommendations=[
                    f"Ask: “Can I afford a phone worth {sym}60,000 next month?”",
                    f"Ask: “What happens if my salary drops by 20%?”",
                    f"Ask: “Which plan protects my emergency reserve best?”",
                    f"Ask: “How much did I spend on food last month?”"
                ],
                assumptions=[],
                limitations=[
                    "I answer only based on your verified transactions and profile—no guesswork, no invented numbers."
                ],
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

            monthly_inc = res.get("monthly_income")
            monthly_exp = res.get("monthly_expenses")
            monthly_sav = res.get("monthly_savings")
            monthly_prov = res.get("monthly_premium_provision")
            immediate_bal = res.get("immediate_post_payment_balance")
            balance_above_buf = res.get("balance_above_emergency_fund")
            is_annual = res.get("is_annual_premium", False)
            has_conflict = res.get("has_conflict", False)
            data_sources = res.get("data_sources", {})
            prof_bal = res.get("profile_balance")
            prof_buf = res.get("profile_buffer")

            if status == "AFFORDABLE":
                if immediate_bal is not None and balance_above_buf is not None:
                    direct = (
                        f"Yes, {amt_str} is affordable based on your financial scenario.\n\n"
                        f"Paying upfront leaves an immediate bank balance of {_fmt(immediate_bal, currency)}, "
                        f"retaining {_fmt(balance_above_buf, currency)} above your required emergency reserve of {_fmt(min_buf, currency)}."
                        + (f"\n\nWith monthly savings of {_fmt(monthly_sav, currency)} (provision: {_fmt(monthly_prov, currency)}/mo), your projected month-end balance is {bal_str}." if monthly_prov else f"\n\nYour projected month-end balance after monthly cash flow is {bal_str}.")
                    )
                else:
                    direct = (
                        f"Yes, {amt_str} is affordable as a full payment based on your current projections.\n\n"
                        f"After this purchase, your projected balance would be {bal_str}, "
                        f"which remains above your required safety buffer."
                    )
            elif status == "POTENTIALLY AFFORDABLE WITH TRADE-OFF":
                direct = (
                    f"{amt_str} is potentially affordable, but requires a trade-off.\n\n"
                    f"Your projected balance after purchase would be {bal_str}. "
                    f"You would need to reduce discretionary spending by {_fmt(trade_off, currency)} to stay above your minimum buffer."
                )
            else:
                direct = (
                    f"No, {amt_str} is not affordable as a single upfront payment under your current projection.\n\n"
                    f"This purchase would bring your projected balance to {bal_str}, "
                    f"which breaches your required minimum buffer."
                )

            facts = [
                f"Bank balance: {_fmt(cur_bal, currency)} (Source: {data_sources.get('current_balance', 'Profile on Record')})",
            ]
            if monthly_inc is not None and monthly_inc > 0:
                facts.append(f"Monthly income: {_fmt(monthly_inc, currency)} (Source: {data_sources.get('monthly_income', 'Stated Scenario')})")
            if monthly_exp is not None and monthly_exp > 0:
                facts.append(f"Monthly expenses: {_fmt(monthly_exp, currency)} (Source: {data_sources.get('monthly_expenses', 'Stated Scenario')})")
            if monthly_sav is not None:
                facts.append(f"Monthly savings: {_fmt(monthly_sav, currency)} (Calculation: Income - Expenses)")
            facts.append(f"Purchase / Premium amount: {amt_str}" + (" (Annual Premium)" if is_annual else ""))
            if monthly_prov is not None:
                facts.append(f"Monthly premium provision: {_fmt(monthly_prov, currency)}/mo (Calculation: Annual Premium ÷ 12)")
            if immediate_bal is not None:
                facts.append(f"Immediate post-payment balance: {_fmt(immediate_bal, currency)} (Calculation: Balance - Purchase Amount)")
            facts.append(f"Minimum emergency fund: {_fmt(min_buf, currency)} (Source: {data_sources.get('minimum_buffer', 'Target Buffer')})")
            if balance_above_buf is not None:
                facts.append(f"Balance above emergency fund: {_fmt(balance_above_buf, currency)} (Calculation: Immediate Balance - Emergency Fund)")
            facts.append(f"Projected next-month net cash flow: {_fmt(res.get('projected_net_cash_flow', 0.0), currency)}")
            facts.append(f"Projected end-of-month balance: {bal_str}")

            trade_offs = []
            if has_conflict:
                trade_offs.append(
                    f"Data Discrepancy Note: Stated scenario values differ from saved profile "
                    f"(Saved balance: {_fmt(prof_bal, currency)}, Saved buffer: {_fmt(prof_buf, currency)}). "
                    f"Calculations were evaluated using your stated scenario inputs."
                )
            if shortfall > 0:
                trade_offs.append(f"An upfront purchase leaves a projected balance of {bal_str}, breaching your buffer by {_fmt(shortfall, currency)}.")
            else:
                trade_offs.append(
                    f"Projected balance remains at {bal_str}, safely above your minimum reserve of {_fmt(min_buf, currency)}."
                )

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

            limitations = []
            if has_conflict:
                limitations.append("Confidence is set to MEDIUM because stated scenario values differ from your saved profile on record.")
            else:
                limitations.append("Affordability is evaluated against declared cash buffers and known obligations only.")

            return StructuredFinancialExplanation(
                direct_answer=direct,
                observed_facts=facts,
                trade_offs=trade_offs,
                recommendations=recs,
                assumptions=[
                    "Evaluated upfront purchase with cash flow provision for the billing cycle."
                    if is_annual else "Assumes variable living expenses remain consistent with your profile."
                ],
                limitations=limitations
            )

        # ------------------------------------------------------------------
        # WHAT-IF SIMULATION
        # ------------------------------------------------------------------
        if intent == IntentType.WHAT_IF:
            sc_type = res.get("scenario_type", "spending_reduction")
            bal = res.get("projected_balance")
            bal_str = _fmt(bal, currency) if bal is not None else "Unavailable"
            cf_change = res.get("cash_flow_change")
            buf_status = res.get("buffer_status_change")
            shortfall_prob = res.get("shortfall_probability", 0.0)

            status_map = {
                "maintained": "Your minimum buffer would be maintained.",
                "breached": "This would breach your minimum balance buffer.",
                "restored": "This would restore your minimum balance buffer.",
                "improved_but_still_breached": "This improves your position but the buffer remains breached.",
                "worsened_breach": "This would further worsen your buffer breach.",
            }
            if buf_status and buf_status in status_map:
                status_text = status_map[buf_status]
            elif bal is None or res.get("baseline_balance") is None or res.get("minimum_buffer") is None:
                status_text = "Buffer status is unavailable due to missing baseline profile."
            else:
                status_text = status_map.get(buf_status, f"Buffer status: {buf_status or 'Unavailable'}")

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
                chg = res.get("change_amount")
                chg_str = _fmt(chg, currency) if chg is not None else "your specified amount"
                direct = f"If you reduce spending by {chg_str}, your projected balance would be {bal_str}. {status_text}"
            elif sc_type == "spending_increase":
                chg = res.get("change_amount")
                chg_str = _fmt(chg, currency) if chg is not None else "your specified amount"
                direct = f"If you increase spending by {chg_str}, your projected balance would be {bal_str}. {status_text}"
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
                "Net Cash Flow Change": _fmt(cf_change, currency) if cf_change is not None else "N/A",
            }
            if shortfall_prob > 0:
                fc_details["Reserve Breach Probability"] = f"{shortfall_prob:.1%}"

            trade_offs = [
                f"Buffer status: {status_text}"
            ]

            recs = []
            if buf_status in ["breached", "worsened_breach"]:
                recs.append("Mitigate shortfall risk by immediately reducing discretionary spending or activating contingency reserves.")
            elif bal is not None and res.get("minimum_buffer") is not None:
                recs.append("This scenario maintains financial stability without breaching your declared reserve buffer.")
            else:
                recs.append("Configure your monthly minimum reserve buffer in Settings for complete safety analysis.")

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
            q_merchant = res.get("queried_merchant")
            q_m_amt = res.get("queried_merchant_amount")
            cat_dist = res.get("category_distribution", [])
            merchants_by_cat = res.get("merchants_by_category", {})
            detected_apps_count = res.get("detected_apps_count", 0)

            cat_icons = {
                "shopping": "🛍️",
                "food": "🍔",
                "travel": "🚗",
                "entertainment": "🎬",
                "utilities": "💡",
                "healthcare": "💊",
                "rent": "🏠",
                "investments": "📈",
                "salary": "💰",
            }

            facts = [
                f"Total analyzed expenses: {_fmt(tot, currency)}",
                f"Essential expenses (fixed/debt/living): {_fmt(ess, currency)}",
                f"Discretionary expenses (variable/lifestyle): {_fmt(disc, currency)}",
            ]
            recs = []

            # 1. User queried a specific app / merchant (e.g. Myntra, Swiggy, Blinkit, Uber, Amazon)
            if q_merchant and q_m_amt is not None:
                cat_label = f" ({q_cat.title()})" if q_cat else ""
                direct = (
                    f"### 💳 App Spending: **{q_merchant}**\n\n"
                    f"You spent **{_fmt(q_m_amt, currency)}** on **{q_merchant}**{cat_label} based on historical transactions."
                )
                facts.insert(0, f"Direct spend on {q_merchant}: {_fmt(q_m_amt, currency)}")

                if q_cat and q_amt is not None and q_amt > 0:
                    pct_of_cat = (q_m_amt / q_amt * 100)
                    facts.append(f"Total {q_cat.title()} category spending: {_fmt(q_amt, currency)} ({q_merchant} represents {pct_of_cat:.1f}%)")

                    other_apps = [
                        f"{name} ({_fmt(amt, currency)})"
                        for name, amt in merchants_by_cat.get(q_cat.lower(), {}).items()
                        if name.lower() != q_merchant.lower()
                    ]
                    if other_apps:
                        facts.append(f"Other recognized apps in {q_cat.title()}: {', '.join(other_apps)}")

                recs.append(f"Monitor orders on {q_merchant} to optimize monthly discretionary cash flow.")

            # 2. User queried a specific category (e.g. food, shopping, travel)
            elif q_cat and q_amt is not None:
                cat_key = q_cat.lower()
                icon = cat_icons.get(cat_key, "🏷️")
                apps_in_cat = [
                    f"• **{name}**: {_fmt(amt, currency)}"
                    for name, amt in sorted(merchants_by_cat.get(cat_key, {}).items(), key=lambda x: x[1], reverse=True)
                ]

                app_text = ""
                if apps_in_cat:
                    app_text = "\n\n**Detected Apps & Merchants:**\n" + "\n".join(apps_in_cat)

                direct = (
                    f"### {icon} Category Spending: **{q_cat.title()}**\n\n"
                    f"You spent **{_fmt(q_amt, currency)}** on **{q_cat.title()}** based on your transaction history.{app_text}"
                )
                facts.insert(0, f"Total {q_cat.title()} expenses: {_fmt(q_amt, currency)}")
                if apps_in_cat:
                    facts.append(f"Recognized apps in {q_cat.title()}: {len(apps_in_cat)} merchants mapped")

                recs.append(f"Review {q_cat.title()} trends on the Insights page to spot potential savings.")

            # 3. General category-wise distribution & detected apps
            else:
                dist_lines = []
                for entry in cat_dist:
                    c_name = entry["category"]
                    c_key = c_name.lower()
                    c_tot = entry["total_amount"]
                    c_pct = entry["percentage"]
                    icon = cat_icons.get(c_key, "🏷️")

                    apps = entry.get("apps", [])
                    if apps:
                        app_summary = ", ".join([f"{a['name']} ({_fmt(a['amount'], currency)})" for a in apps[:4]])
                        dist_lines.append(f"• {icon} **{c_name.title()}**: {_fmt(c_tot, currency)} ({c_pct:.1f}%)\n  ↳ *Detected Apps: {app_summary}*")
                    else:
                        dist_lines.append(f"• {icon} **{c_name.title()}**: {_fmt(c_tot, currency)} ({c_pct:.1f}%)")

                direct = (
                    f"### 📊 Category-Wise Spending Distribution\n\n"
                    f"Here is your expense breakdown categorized by known consumer apps and spending types:\n\n"
                    + "\n".join(dist_lines)
                )

                if detected_apps_count > 0:
                    facts.append(f"Auto-categorized apps: {detected_apps_count} transactions mapped to merchants like Myntra, Amazon, Swiggy, Blinkit, and Uber")

                top_cats = res.get("top_categories", [])
                if top_cats:
                    facts.append("Top categories: " + ", ".join([f"{c['category'].title()}: {_fmt(c['total_amount'], currency)}" for c in top_cats[:3]]))

                recs.append("Review discretionary categories (Shopping, Food, Travel) on the Insights page to identify savings.")

            fc_details = {}
            for entry in cat_dist[:6]:
                apps_label = f" ({len(entry.get('apps', []))} apps detected)" if entry.get("apps") else ""
                fc_details[f"{entry['category'].title()} Spending"] = f"{_fmt(entry['total_amount'], currency)} ({entry['percentage']:.1f}%){apps_label}"

            return StructuredFinancialExplanation(
                direct_answer=direct,
                observed_facts=facts,
                forecast_details=fc_details if cat_dist else None,
                recommendations=recs,
                assumptions=["Transactions categorized by merchant intelligence rules (e.g. Myntra/Amazon → Shopping, Swiggy/Blinkit → Food, Uber → Travel) and deterministic categorization model."],
                limitations=["Transactions with unknown descriptions or generic bank transfer IDs default to 'unknown' category."]
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
