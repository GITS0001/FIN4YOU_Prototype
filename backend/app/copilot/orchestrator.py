from typing import Optional, List, Dict
from app.schemas.copilot import CopilotRequest, CopilotResponse, ParsedIntent, IntentType, ActionLink
from app.copilot.intent_parser import IntentParser
from app.copilot.response_generator import ResponseGenerator
from app.services.db_service import get_user_profile, get_user_transactions
from app.financial.state import FinancialStateEngine
from sqlalchemy.orm import Session
from app.ml.forecasting import PredictionEngine
from app.decision.engine import DecisionEngine
from app.decision.affordability import AffordabilityEngine
from app.decision.simulation import WhatIfSimulator
from app.decision.impact import ImpactEngine
from app.schemas.financial import PaymentOption
from app.schemas.decision import DecisionTrace, Recommendation, ExpectedImpact

import pandas as pd

class CopilotOrchestrator:
    def __init__(self, data_dir: str = "data/prototype"):
        self.parser = IntentParser()
        self.generator = ResponseGenerator()
        self.data_dir = data_dir

        try:
            self.payment_opts_df = pd.read_csv(f"{self.data_dir}/request_payment_options.csv")
        except FileNotFoundError:
            self.payment_opts_df = pd.DataFrame()

    def process_query(self, request: CopilotRequest, db: Session) -> CopilotResponse:
        # Find user
        try:
            uid = int(request.user_id)
        except ValueError:
            raise ValueError("Invalid user id")

        profile = get_user_profile(db, uid)
        if not profile:
            raise ValueError(f"User {request.user_id} not found")

        currency = profile.home_currency

        # Parse Intent
        parsed = self.parser.parse(request.message)

        if parsed.intent == IntentType.UNKNOWN:
            resp_text = self.generator.generate(parsed, {}, currency)
            return CopilotResponse(
                intent=parsed.intent,
                response=resp_text,
                confidence="UNKNOWN",
                status="UNSUPPORTED"
            )

        # Retrieve Financial Context
        user_events = get_user_transactions(db, uid)
        state = FinancialStateEngine(profile.user_id).calculate_state(user_events)
        pred = PredictionEngine().run_prediction(user_events, profile)

        REQUIRES_PREDICTION = [
            IntentType.AFFORDABILITY_CHECK,
            IntentType.PAYMENT_OPTION_ANALYSIS,
            IntentType.WHAT_IF,
            IntentType.RECOMMENDATION,
            IntentType.CASH_FLOW_FORECAST,
            IntentType.FINANCIAL_FORECAST,
        ]

        if not pred.available and parsed.intent in REQUIRES_PREDICTION:
            resp_text = self.generator.generate(parsed, {"status": "INSUFFICIENT_DATA"}, currency)
            return CopilotResponse(
                intent=parsed.intent,
                response=resp_text,
                confidence="UNKNOWN",
                status="INSUFFICIENT_DATA",
                data_sources=["financial_profiles", "financial_events"]
            )

        structured_res = {}
        trace = None
        status = "SUCCESS"
        action_links = []

        if parsed.intent == IntentType.AFFORDABILITY_CHECK:
            if not parsed.amount or parsed.amount <= 0:
                return CopilotResponse(
                    intent=parsed.intent,
                    response=f"Please specify a valid purchase amount. For example: 'Can I afford {currency} 1,000?'",
                    confidence="UNKNOWN",
                    status="ERROR"
                )
            aff_eng = AffordabilityEngine(profile, pred)
            try:
                requests_df = pd.read_csv(f"{self.data_dir}/requests.csv")
                req_id = None
                for _, r in requests_df.iterrows():
                    if r["user_id"] == profile.user_id and abs(r["requested_amount"] - parsed.amount) < 1.0:
                        req_id = r["request_id"]
                        break
                po_list = []
                if req_id and not self.payment_opts_df.empty:
                    opts = self.payment_opts_df[self.payment_opts_df["request_id"] == req_id]
                    for _, o in opts.iterrows():
                        pfq = o["payment_frequency_days"]
                        if pd.isna(pfq): pfq = None
                        po_list.append(PaymentOption(
                            payment_option_id=o["payment_option_id"],
                            request_id=o["request_id"],
                            payment_method=o["payment_method"],
                            payment_amount=o["payment_amount"],
                            number_of_payments=o["number_of_payments"],
                            first_payment_date=o["first_payment_date"],
                            payment_frequency_days=pfq,
                            financing_fee=o["financing_fee"],
                            total_payable_amount=o["total_payable_amount"]
                        ))
            except Exception:
                po_list = []

            res = aff_eng.evaluate_purchase(parsed.amount, po_list)
            structured_res = {
                "type": "affordability",
                "affordability_status": res.status,
                "proposed_amount": parsed.amount,
                "resulting_balance": res.resulting_balance,
                "shortfall": res.shortfall,
                "trade_off": res.trade_off_required,
                "viable_options": [o.model_dump() for o in res.viable_payment_options],
                "current_balance": profile.current_available_balance,
                "minimum_buffer": profile.minimum_balance_to_keep,
                "projected_cash_flow": pred.projected_cash_flow.projected_cash_flow if pred.projected_cash_flow else 0,
                "reasons": res.reasons,
                "currency": currency,
            }

            simulation_text = (
                f"Resulting balance if paid upfront: {res.resulting_balance:.2f}. "
                + " | ".join(res.reasons[-2:])  # include last two reasons for brevity
            )
            trace = DecisionTrace(
                observed_fact=f"Current balance: {profile.current_available_balance:.2f}. Required buffer: {profile.minimum_balance_to_keep:.2f}.",
                calculation=f"Proposed purchase: {parsed.amount:.2f}. Projected net cash flow: {pred.projected_cash_flow.projected_cash_flow if pred.projected_cash_flow else 0:.2f}.",
                prediction=f"Projected balance after purchase: {res.resulting_balance:.2f}. Shortfall vs buffer: {res.shortfall:.2f}.",
                simulation=simulation_text,
                recommendation=Recommendation(
                    recommendation_type="AFFORDABILITY",
                    actionable_text=(
                        "Consider paying in installments"
                        if res.status == "NOT AFFORDABLE UNDER CURRENT PROJECTION" and len(res.viable_payment_options) > 0
                        else ("Avoid this purchase or save more first" if res.status == "NOT AFFORDABLE UNDER CURRENT PROJECTION"
                              else "Proceed with purchase")
                    ),
                    expected_impact=ExpectedImpact(
                        cash_flow_difference=0,
                        balance_difference=-parsed.amount,
                        buffer_status_change="breached" if res.resulting_balance < profile.minimum_balance_to_keep else "maintained"
                    ),
                    confidence_level="HIGH",
                    confidence_reason="Deterministic calculation based on projected cash flow and user profile."
                ),
                supporting_data={"shortfall": res.shortfall, "trade_off_required": res.trade_off_required}
            )

            action_links = [
                ActionLink(label="Affordability Tool", url="/affordability"),
                ActionLink(label="What-If Simulator", url="/what-if")
            ]

        elif parsed.intent == IntentType.PAYMENT_OPTION_ANALYSIS:
            if not parsed.amount or parsed.amount <= 0:
                return CopilotResponse(
                    intent=parsed.intent,
                    response="Please specify a valid purchase amount to check installment options.",
                    confidence="UNKNOWN",
                    status="ERROR"
                )

            try:
                requests_df = pd.read_csv(f"{self.data_dir}/requests.csv")
                req_id = None
                for _, r in requests_df.iterrows():
                    if r["user_id"] == profile.user_id and abs(r["requested_amount"] - parsed.amount) < 1.0:
                        req_id = r["request_id"]
                        break
                po_list = []
                if req_id and not self.payment_opts_df.empty:
                    opts = self.payment_opts_df[self.payment_opts_df["request_id"] == req_id]
                    for _, o in opts.iterrows():
                        pfq = o["payment_frequency_days"]
                        if pd.isna(pfq): pfq = None
                        po_list.append(PaymentOption(
                            payment_option_id=o["payment_option_id"],
                            request_id=o["request_id"],
                            payment_method=o["payment_method"],
                            payment_amount=o["payment_amount"],
                            number_of_payments=o["number_of_payments"],
                            first_payment_date=o["first_payment_date"],
                            payment_frequency_days=pfq,
                            financing_fee=o["financing_fee"],
                            total_payable_amount=o["total_payable_amount"]
                        ))
            except Exception:
                po_list = []

            aff_eng = AffordabilityEngine(profile, pred)
            res = aff_eng.evaluate_purchase(parsed.amount, po_list)
            structured_res = {
                "type": "payment_options",
                "affordability_status": res.status,
                "proposed_amount": parsed.amount,
                "resulting_balance": res.resulting_balance,
                "viable_options": [o.model_dump() for o in res.viable_payment_options],
                "current_balance": profile.current_available_balance,
                "minimum_buffer": profile.minimum_balance_to_keep,
                "currency": currency,
            }

            action_links = [
                ActionLink(label="Affordability Tool", url="/affordability")
            ]

        elif parsed.intent == IntentType.WHAT_IF:
            sim = WhatIfSimulator(profile, pred)
            baseline = sim.baseline_scenario()

            change = parsed.change_amount

            if change is None or change == 0:
                # No valid change specified – return baseline as the scenario
                structured_res = {
                    "type": "what_if",
                    "scenario_type": "no_change",
                    "projected_balance": baseline.projected_balance,
                    "baseline_cash_flow": baseline.projected_cash_flow,
                    "scenario_cash_flow": baseline.projected_cash_flow,
                    "buffer_status_change": "maintained" if not baseline.buffer_breached else "breached",
                    "buffer_breached": baseline.buffer_breached,
                    "minimum_buffer": profile.minimum_balance_to_keep,
                    "change_amount": 0.0,
                    "currency": currency,
                    "note": "No change amount was specified; showing baseline projection.",
                }
            elif change < 0:
                # Spending REDUCTION scenario (change_amount negative means less spending)
                reduction = abs(change)
                scenario = sim.simulate_reduce_discretionary_spending(reduction)
                impact = ImpactEngine.calculate_impact(baseline, scenario)
                summary = sim.compute_what_if_summary(baseline, scenario)
                structured_res = {
                    "type": "what_if",
                    "scenario_type": "spending_reduction",
                    "baseline_balance": baseline.projected_balance,
                    "scenario_balance": scenario.projected_balance,
                    "baseline_cash_flow": baseline.projected_cash_flow,
                    "scenario_cash_flow": scenario.projected_cash_flow,
                    "cash_flow_change": impact.cash_flow_difference,
                    "balance_change": impact.balance_difference,
                    "projected_balance": scenario.projected_balance,
                    "buffer_status_change": impact.buffer_status_change,
                    "buffer_breached": scenario.buffer_breached,
                    "minimum_buffer": profile.minimum_balance_to_keep,
                    "change_amount": reduction,
                    "monthly_summary": summary.model_dump(),
                    "currency": currency,
                }
            else:
                # Spending INCREASE scenario (change_amount positive means more spending)
                scenario = sim.simulate_increase_spending(change)
                impact = ImpactEngine.calculate_impact(baseline, scenario)
                summary = sim.compute_what_if_summary(baseline, scenario)
                structured_res = {
                    "type": "what_if",
                    "scenario_type": "spending_increase",
                    "baseline_balance": baseline.projected_balance,
                    "scenario_balance": scenario.projected_balance,
                    "baseline_cash_flow": baseline.projected_cash_flow,
                    "scenario_cash_flow": scenario.projected_cash_flow,
                    "cash_flow_change": impact.cash_flow_difference,
                    "balance_change": impact.balance_difference,
                    "projected_balance": scenario.projected_balance,
                    "buffer_status_change": impact.buffer_status_change,
                    "buffer_breached": scenario.buffer_breached,
                    "minimum_buffer": profile.minimum_balance_to_keep,
                    "change_amount": change,
                    "monthly_summary": summary.model_dump(),
                    "currency": currency,
                }

            action_links = [
                ActionLink(label="Open Simulator", url="/what-if")
            ]

        elif parsed.intent == IntentType.RECOMMENDATION:
            dec_eng = DecisionEngine(profile, state, pred)
            trace = dec_eng.generate_recommendation_for_gap()
            if trace:
                structured_res = {
                    "type": "recommendation",
                    "recommendation_text": trace.recommendation.actionable_text,
                    "confidence_level": trace.recommendation.confidence_level,
                    "confidence_reason": trace.recommendation.confidence_reason,
                    "cash_flow_difference": trace.recommendation.expected_impact.cash_flow_difference,
                    "balance_difference": trace.recommendation.expected_impact.balance_difference,
                    "buffer_status_change": trace.recommendation.expected_impact.buffer_status_change,
                    "observed_fact": trace.observed_fact,
                    "calculation": trace.calculation,
                    "prediction": trace.prediction,
                    "simulation": trace.simulation,
                    "currency": currency,
                }
            else:
                structured_res = {
                    "type": "recommendation",
                    "recommendation_text": None,
                    "currency": currency,
                }

            action_links = [
                ActionLink(label="View Forecast", url="/forecast")
            ]

        elif parsed.intent in [IntentType.CASH_FLOW_FORECAST, IntentType.FINANCIAL_FORECAST]:
            if pred.projected_cash_flow:
                sim = WhatIfSimulator(profile, pred)
                baseline = sim.baseline_scenario()
                structured_res = {
                    "type": "cash_flow_forecast",
                    "projected_income": pred.projected_cash_flow.projected_income,
                    "projected_expenses": pred.projected_cash_flow.projected_expenses,
                    "known_obligations": pred.projected_cash_flow.known_obligations,
                    "projected_cash_flow": pred.projected_cash_flow.projected_cash_flow,
                    "projected_balance": baseline.projected_balance,
                    "buffer_breached": baseline.buffer_breached,
                    "minimum_buffer": profile.minimum_balance_to_keep,
                    "current_balance": profile.current_available_balance,
                    "currency": currency,
                }
            else:
                structured_res = {"type": "cash_flow_forecast", "currency": currency}

            action_links = [
                ActionLink(label="View Full Forecast", url="/forecast")
            ]

        elif parsed.intent == IntentType.FINANCIAL_SUMMARY:
            top_categories = sorted(state.category_spending, key=lambda x: x.total_amount, reverse=True)[:3]
            structured_res = {
                "type": "financial_summary",
                "balance": profile.current_available_balance,
                "minimum_buffer": profile.minimum_balance_to_keep,
                "cash_flow": state.cash_flow,
                "income": state.income,
                "expenses": state.expenses,
                "savings": state.savings,
                "savings_rate": state.savings_rate,
                "expense_ratio": state.expense_ratio,
                "essential_expenses": state.essential_expenses,
                "discretionary_expenses": state.discretionary_expenses,
                "top_categories": [{"category": c.category, "amount": c.total_amount} for c in top_categories],
                "currency": currency,
            }

            action_links = [
                ActionLink(label="View Dashboard", url="/dashboard"),
                ActionLink(label="View Insights", url="/insights")
            ]

        elif parsed.intent == IntentType.SPENDING_ANALYSIS:
            top_categories = sorted(state.category_spending, key=lambda x: x.total_amount, reverse=True)[:5]
            structured_res = {
                "type": "spending_analysis",
                "total_expenses": state.expenses,
                "essential_expenses": state.essential_expenses,
                "discretionary_expenses": state.discretionary_expenses,
                "top_categories": [{"category": c.category, "amount": c.total_amount} for c in top_categories],
                "anomaly_count": len([a for a in state.anomalies if a.is_anomaly]),
                "currency": currency,
            }

            action_links = [
                ActionLink(label="Detailed Insights", url="/insights")
            ]

        elif parsed.intent == IntentType.GREETING:
            structured_res = {"type": "greeting"}

        elif parsed.intent == IntentType.SAVING_PLAN:
            structured_res = {
                "type": "saving_plan",
                "income": state.income,
                "expenses": state.expenses,
                "savings": state.savings,
                "currency": currency,
            }
            action_links = [
                ActionLink(label="View Insights", url="/insights"),
                ActionLink(label="What-If Simulator", url="/what-if"),
            ]

        elif parsed.intent == IntentType.BUDGETING:
            structured_res = {
                "type": "budgeting",
                "income": state.income,
                "expenses": state.expenses,
                "currency": currency,
            }
            action_links = [
                ActionLink(label="View Dashboard", url="/dashboard")
            ]

        elif parsed.intent == IntentType.BALANCE_QUERY:
            structured_res = {
                "type": "balance_query",
                "balance": profile.current_available_balance,
                "minimum_buffer": profile.minimum_balance_to_keep,
                "currency": currency,
            }

        elif parsed.intent == IntentType.CASH_FLOW_QUERY:
            structured_res = {
                "type": "cash_flow_query",
                "cash_flow": state.cash_flow,
                "income": state.income,
                "expenses": state.expenses,
                "currency": currency,
            }

        elif parsed.intent == IntentType.INCOME_QUERY:
            structured_res = {
                "type": "income_query",
                "income": state.income,
                "currency": currency,
            }

        elif parsed.intent == IntentType.EXPENSE_QUERY:
            structured_res = {
                "type": "expense_query",
                "expenses": state.expenses,
                "essential_expenses": state.essential_expenses,
                "discretionary_expenses": state.discretionary_expenses,
                "currency": currency,
            }

        elif parsed.intent in [IntentType.GENERAL_FINANCE, IntentType.GENERAL_CONVERSATION, IntentType.CLARIFICATION]:
            structured_res = {"type": "general_query", "currency": currency}

        resp_text = self.generator.generate(parsed, structured_res, currency)

        # Enhance response via Groq LLM engine if active
        try:
            from app.copilot.groq_service import groq_llm_service
            if groq_llm_service.is_available():
                if parsed.intent == IntentType.GREETING:
                    financial_context = {}
                else:
                    financial_context = {
                        "balance": profile.current_available_balance,
                        "buffer": profile.minimum_balance_to_keep,
                        "currency": currency,
                        "structured_result": structured_res,
                    }
                resp_text = groq_llm_service.generate_explanation(
                    user_query=request.message,
                    intent_name=str(parsed.intent),
                    rule_response=resp_text,
                    financial_context=financial_context,
                )
        except Exception:
            pass

        return CopilotResponse(
            intent=parsed.intent,
            response=resp_text,
            decision_trace=trace,
            structured_result=structured_res,
            confidence="HIGH" if pred.available else "MEDIUM",
            status=status,
            data_sources=["financial_profiles", "financial_events", "PredictionEngine", "DecisionEngine", "GroqLLaMA3"],
            action_links=action_links
        )
