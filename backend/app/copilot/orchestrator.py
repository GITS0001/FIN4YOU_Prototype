import os
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import pandas as pd

from app.schemas.copilot import (
    CopilotRequest, CopilotResponse, ParsedIntent, IntentType, ActionLink
)
from app.schemas.decision import DecisionTrace, Recommendation, ExpectedImpact
from app.copilot.provider import get_llm_provider, BaseLLMProvider
from app.copilot.intent_parser import IntentParser
from app.copilot.response_generator import ResponseGenerator
from app.copilot.tools import (
    FINANCIAL_TOOLS,
    SpendingAnalysisArgs, FinancialSummaryArgs, AffordabilityCheckArgs,
    WhatIfSimulationArgs, CashFlowForecastArgs, ActionPlanArgs, RecommendationArgs
)
from app.services.db_service import get_user_profile, get_user_transactions

logger = logging.getLogger("fin4you.artha_orchestrator")


class CopilotOrchestrator:
    """
    Artha AI Financial Health Copilot Orchestrator.
    Coordinates:
    - User authentication and financial state extraction
    - Intent parsing (LLM-assisted + deterministic fallback)
    - Pydantic-validated tool dispatch to deterministic financial services
    - Structured explanation and decision-trace generation
    - Safe conversational response delivery
    """

    def __init__(self, provider: Optional[BaseLLMProvider] = None, data_dir: str = "data/prototype"):
        self.provider = provider or get_llm_provider()
        self.parser = IntentParser(provider=self.provider)
        self.generator = ResponseGenerator(provider=self.provider)
        self.data_dir = data_dir

    def process_query(self, request: CopilotRequest, db: Session) -> CopilotResponse:
        # 1. Resolve user ID and retrieve financial state
        user_id_raw = request.user_id
        if not user_id_raw:
            raise ValueError("Missing user id")

        # Support integer IDs as well as strings like "user_28"
        try:
            uid = int(user_id_raw)
        except (ValueError, TypeError):
            uid = user_id_raw

        profile = get_user_profile(db, uid)
        if not profile:
            raise ValueError(f"User {user_id_raw} not found")

        currency = profile.home_currency
        user_events = get_user_transactions(db, uid)

        # 2. Parse User Intent
        parsed = self.parser.parse(request.message, request.conversation_history)

        # 3. Handle Missing Data Clarification Queries
        if parsed.intent == IntentType.MISSING_DATA_CLARIFICATION:
            res_dict = {
                "current_balance": profile.current_available_balance,
                "minimum_buffer": profile.minimum_balance_to_keep,
            }
            resp_text = self.generator.generate(parsed, res_dict, currency=currency, user_message=request.message)
            comp = self.generator.get_components(parsed, res_dict, currency=currency)
            return CopilotResponse(
                intent=parsed.intent,
                response=resp_text,
                direct_answer=comp["direct_answer"],
                observed_facts=comp["observed_facts"],
                forecast_details=comp["forecast_details"],
                recommendations=comp["recommendations"],
                assumptions=comp["assumptions"],
                limitations=comp["limitations"],
                trade_offs=comp["trade_offs"],
                confidence="HIGH",
                status="SUCCESS",
                data_sources=["financial_profiles", "financial_events"],
                llm_provider=self.provider.name,
                action_links=[
                    ActionLink(label="Profile Settings", url="/profile"),
                    ActionLink(label="Insights", url="/insights")
                ]
            )

        # 4. Handle Unknown / Unsupported Queries
        if parsed.intent == IntentType.UNKNOWN:
            resp_text = self.generator.generate(parsed, {}, currency=currency, user_message=request.message)
            comp = self.generator.get_components(parsed, {}, currency=currency)
            return CopilotResponse(
                intent=parsed.intent,
                response=resp_text,
                direct_answer=comp["direct_answer"],
                observed_facts=comp["observed_facts"],
                recommendations=comp["recommendations"],
                limitations=comp["limitations"],
                confidence="UNKNOWN",
                status="UNSUPPORTED",
                data_sources=[],
                llm_provider=self.provider.name,
                action_links=[
                    ActionLink(label="Dashboard", url="/dashboard"),
                    ActionLink(label="Affordability", url="/affordability")
                ]
            )

        # 5. Guard: If transaction records are empty and intent requires history
        if not user_events and parsed.intent not in [IntentType.FINANCIAL_SUMMARY]:
            res_dict = {"status": "INSUFFICIENT_DATA"}
            resp_text = self.generator.generate(parsed, res_dict, currency=currency, user_message=request.message)
            comp = self.generator.get_components(parsed, res_dict, currency=currency)
            return CopilotResponse(
                intent=parsed.intent,
                response=resp_text,
                direct_answer=comp["direct_answer"],
                observed_facts=comp["observed_facts"],
                recommendations=comp["recommendations"],
                limitations=comp["limitations"],
                confidence="UNKNOWN",
                status="INSUFFICIENT_DATA",
                data_sources=["financial_profiles"],
                llm_provider=self.provider.name,
                action_links=[ActionLink(label="Upload Statement", url="/statements")]
            )

        # 6. Execute Deterministic Tool Dispatch
        structured_res: Dict[str, Any] = {}
        trace: Optional[DecisionTrace] = None
        status = "SUCCESS"
        action_links: List[ActionLink] = []

        try:
            # --- AFFORDABILITY CHECK ---
            if parsed.intent in [IntentType.AFFORDABILITY_CHECK, IntentType.PAYMENT_OPTION_ANALYSIS]:
                if not parsed.amount or parsed.amount <= 0:
                    return CopilotResponse(
                        intent=parsed.intent,
                        response=f"Please specify a valid purchase amount. For example: 'Can I afford a purchase worth {currency} 1,000?'",
                        confidence="UNKNOWN",
                        status="ERROR",
                        limitations=["A valid positive amount is required to evaluate purchase affordability."]
                    )

                tool_args = AffordabilityCheckArgs(
                    purchase_amount=parsed.amount,
                    item_description=parsed.item_description,
                    stated_balance=parsed.stated_balance,
                    stated_income=parsed.stated_income,
                    stated_expenses=parsed.stated_expenses,
                    stated_buffer=parsed.stated_buffer,
                    is_annual=parsed.is_annual or False,
                )
                structured_res = FINANCIAL_TOOLS["check_affordability"]["executor"](tool_args, profile, user_events)
                structured_res["type"] = "affordability"
                structured_res["proposed_amount"] = parsed.amount

                # Build Decision Trace
                resulting_b = structured_res.get("resulting_balance", 0.0)
                aff_status = structured_res.get("affordability_status", "")
                shortfall = structured_res.get("shortfall", 0.0)
                viable_opts = structured_res.get("viable_options", [])
                has_conflict = structured_res.get("has_conflict", False)
                active_b = structured_res.get("current_balance", profile.current_available_balance)
                active_buf = structured_res.get("minimum_buffer", profile.minimum_balance_to_keep)
                active_cf = structured_res.get("projected_net_cash_flow", 0.0)

                trace = DecisionTrace(
                    observed_fact=f"Bank balance: {active_b:,.2f}. Required buffer: {active_buf:,.2f}." + (f" (Profile on record: {profile.current_available_balance:,.2f} / {profile.minimum_balance_to_keep:,.2f})" if has_conflict else ""),
                    calculation=f"Proposed purchase: {parsed.amount:,.2f}. Projected net cash flow: {active_cf:,.2f}.",
                    prediction=f"Projected balance after purchase: {resulting_b:,.2f}. Shortfall vs buffer: {shortfall:,.2f}.",
                    simulation=f"Resulting balance if paid upfront: {resulting_b:,.2f}. Buffer shortfall: {shortfall:,.2f}.",
                    recommendation=Recommendation(
                        recommendation_type="AFFORDABILITY",
                        actionable_text=(
                            "Consider paying in installments"
                            if aff_status != "AFFORDABLE" and len(viable_opts) > 0
                            else ("Avoid upfront purchase or save more first" if aff_status != "AFFORDABLE" else "Proceed with purchase")
                        ),
                        expected_impact=ExpectedImpact(
                            cash_flow_difference=0.0,
                            balance_difference=-parsed.amount,
                            buffer_status_change="breached" if resulting_b < active_buf else "maintained"
                        ),
                        confidence_level="MEDIUM" if has_conflict else ("HIGH" if len(user_events) >= 3 else "MEDIUM"),
                        confidence_reason=(
                            f"Input variance detected between user-stated scenario and saved profile. Confidence downgraded to MEDIUM."
                            if has_conflict
                            else "Deterministic calculation based on projected cash flow and user profile."
                        )
                    ),
                    supporting_data={
                        "shortfall": shortfall,
                        "trade_off_required": structured_res.get("trade_off_required", 0.0),
                        "immediate_post_payment_balance": structured_res.get("immediate_post_payment_balance", 0.0),
                        "balance_above_emergency_fund": structured_res.get("balance_above_emergency_fund", 0.0),
                    }
                )

                action_links = [
                    ActionLink(label="Affordability Tool", url="/affordability"),
                    ActionLink(label="What-If Simulator", url="/what-if")
                ]

            # --- WHAT-IF SIMULATION ---
            elif parsed.intent == IntentType.WHAT_IF:
                tool_args = WhatIfSimulationArgs(
                    change_amount=parsed.change_amount,
                    category=parsed.category,
                    income_shock_percentage=parsed.income_shock_percentage or 0.0,
                    unexpected_expense=parsed.unexpected_expense or 0.0
                )
                structured_res = FINANCIAL_TOOLS["simulate_what_if"]["executor"](tool_args, profile, user_events)
                structured_res["type"] = "what_if"

                action_links = [
                    ActionLink(label="Open Simulator", url="/what-if"),
                    ActionLink(label="View Forecast", url="/forecast")
                ]

            # --- PLAN EVALUATION & STRATEGY COMPARISON ---
            elif parsed.intent in [IntentType.PLAN_EVALUATION, IntentType.GOAL_FEASIBILITY]:
                tool_args = ActionPlanArgs(
                    horizon_months=parsed.horizon_months or 6,
                    income_shock_percentage=parsed.income_shock_percentage or 0.0,
                    unexpected_expense=parsed.unexpected_expense or 0.0
                )
                structured_res = FINANCIAL_TOOLS["evaluate_action_plans"]["executor"](tool_args, profile, user_events)
                structured_res["type"] = "action_plan"

                action_links = [
                    ActionLink(label="Financial Planner", url="/planner"),
                    ActionLink(label="View Forecast", url="/forecast")
                ]

            # --- SPENDING ANALYSIS ---
            elif parsed.intent == IntentType.SPENDING_ANALYSIS:
                tool_args = SpendingAnalysisArgs(
                    category=parsed.category,
                    merchant=getattr(parsed, "merchant", None)
                )
                structured_res = FINANCIAL_TOOLS["analyze_spending"]["executor"](tool_args, profile, user_events)
                structured_res["type"] = "spending_analysis"

                action_links = [
                    ActionLink(label="Detailed Insights", url="/insights"),
                    ActionLink(label="Dashboard", url="/dashboard")
                ]

            # --- CASH FLOW FORECAST ---
            elif parsed.intent == IntentType.CASH_FLOW_FORECAST:
                tool_args = CashFlowForecastArgs(
                    horizon_months=parsed.horizon_months or 6,
                    income_shock_percentage=parsed.income_shock_percentage or 0.0
                )
                structured_res = FINANCIAL_TOOLS["forecast_cash_flow"]["executor"](tool_args, profile, user_events)
                structured_res["type"] = "cash_flow_forecast"

                action_links = [
                    ActionLink(label="View Full Forecast", url="/forecast"),
                    ActionLink(label="Scenario Simulator", url="/what-if")
                ]

            # --- RECOMMENDATION EXPLANATION ---
            elif parsed.intent == IntentType.RECOMMENDATION:
                tool_args = RecommendationArgs(category_focus=parsed.category)
                structured_res = FINANCIAL_TOOLS["explain_recommendation"]["executor"](tool_args, profile, user_events)
                structured_res["type"] = "recommendation"

                if structured_res.get("recommendation_text"):
                    trace = DecisionTrace(
                        observed_fact=structured_res.get("observed_fact") or f"Current balance: {profile.current_available_balance:.2f}",
                        calculation=structured_res.get("calculation") or "Computed trailing cash-flow margin",
                        prediction=structured_res.get("prediction") or "Cash flow projection",
                        simulation=structured_res.get("simulation") or "Buffer preservation scenario",
                        recommendation=Recommendation(
                            recommendation_type=structured_res.get("recommendation_type") or "REDUCTION",
                            actionable_text=structured_res["recommendation_text"],
                            expected_impact=ExpectedImpact(
                                cash_flow_difference=structured_res.get("cash_flow_difference", 0.0),
                                balance_difference=structured_res.get("balance_difference", 0.0),
                                buffer_status_change=structured_res.get("buffer_status_change", "maintained")
                            ),
                            confidence_level=structured_res.get("confidence_level", "HIGH"),
                            confidence_reason="Derived deterministically by DecisionEngine."
                        )
                    )

                action_links = [
                    ActionLink(label="View Forecast", url="/forecast"),
                    ActionLink(label="Insights", url="/insights")
                ]

            # --- FINANCIAL SUMMARY ---
            elif parsed.intent == IntentType.FINANCIAL_SUMMARY:
                tool_args = FinancialSummaryArgs()
                structured_res = FINANCIAL_TOOLS["get_financial_summary"]["executor"](tool_args, profile, user_events)
                structured_res["type"] = "financial_summary"

                action_links = [
                    ActionLink(label="View Dashboard", url="/dashboard"),
                    ActionLink(label="View Insights", url="/insights")
                ]

        except Exception as e:
            logger.error(f"Error executing tool for intent {parsed.intent}: {e}", exc_info=True)
            status = "ERROR"
            structured_res = {"error": str(e), "currency": currency}

        # 7. Generate Grounded Explanation
        resp_text = self.generator.generate(
            parsed=parsed,
            result=structured_res,
            currency=currency,
            user_message=request.message,
        )
        comp = self.generator.get_components(
            parsed=parsed,
            result=structured_res,
            currency=currency,
        )

        has_conflict = structured_res.get("has_conflict", False)
        if has_conflict:
            overall_confidence = "MEDIUM"
        elif len(user_events) >= 3 and status == "SUCCESS":
            overall_confidence = "HIGH"
        else:
            overall_confidence = "MEDIUM"

        return CopilotResponse(
            intent=parsed.intent,
            response=resp_text,
            direct_answer=comp["direct_answer"],
            decision_trace=trace,
            structured_result=structured_res,
            confidence=overall_confidence,
            status=status,
            data_sources=[
                "financial_profiles", "financial_events",
                "FinancialStateEngine", "PredictionEngine", "ConstrainedPlannerEngine", "AffordabilityEngine"
            ] + (["stated_scenario_inputs"] if has_conflict or parsed.stated_balance is not None else []),
            action_links=action_links,
            observed_facts=comp["observed_facts"],
            forecast_details=comp["forecast_details"],
            recommendations=comp["recommendations"],
            assumptions=comp["assumptions"],
            limitations=comp["limitations"],
            trade_offs=comp["trade_offs"],
            llm_provider=self.provider.name,
        )
