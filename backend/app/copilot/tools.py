"""
Artha AI Financial Tool Registry
================================
Provides strictly allowlisted, Pydantic-validated financial tools
that invoke existing deterministic engines.
No arbitrary SQL, shell, or code execution.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
import pandas as pd
from pathlib import Path

from app.schemas.financial import FinancialProfile, Transaction, PaymentOption
from app.financial.state import FinancialStateEngine
from app.ml.forecasting import PredictionEngine
from app.decision.affordability import AffordabilityEngine
from app.decision.simulation import WhatIfSimulator
from app.decision.impact import ImpactEngine
from app.decision.engine import DecisionEngine
from app.decision.planner import ConstrainedPlannerEngine
from app.schemas.planner import (
    FinancialGoal, PlanEvaluationRequest, ProbabilisticForecastRequest,
    ProbabilisticForecastResponse, PlanEvaluationResponse
)


# ============================================================================
# Tool Input Schemas
# ============================================================================

class SpendingAnalysisArgs(BaseModel):
    category: Optional[str] = Field(None, description="Optional spending category to filter by (e.g. food, rent, shopping)")
    period: Optional[str] = Field(None, description="Optional time period filter (e.g. 'last month', 'current')")


class FinancialSummaryArgs(BaseModel):
    include_anomalies: bool = Field(True, description="Whether to include anomalous transactions")


class AffordabilityCheckArgs(BaseModel):
    purchase_amount: float = Field(..., gt=0, description="Purchase amount to evaluate in user currency")
    item_description: Optional[str] = Field(None, description="Description of the item (e.g. phone, car, laptop)")
    payment_method: Optional[str] = Field("upfront", description="Preferred payment method (upfront or installments)")

    @field_validator("purchase_amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Purchase amount must be greater than zero.")
        return round(v, 2)


class WhatIfSimulationArgs(BaseModel):
    change_amount: Optional[float] = Field(None, description="Amount of increase (positive) or reduction (negative)")
    category: Optional[str] = Field(None, description="Category of spending to alter (e.g. eating out, entertainment)")
    income_shock_percentage: float = Field(0.0, description="Income change percentage (e.g. -0.20 for 20% salary drop)")
    unexpected_expense: float = Field(0.0, ge=0.0, description="One-time unexpected expense amount (e.g. medical bill)")


class CashFlowForecastArgs(BaseModel):
    horizon_months: int = Field(6, ge=1, le=24, description="Forecast horizon in months (default 6)")
    include_uncertainty: bool = Field(True, description="Whether to calculate probabilistic reserve breach probability")
    income_shock_percentage: float = Field(0.0, description="Percentage shock to future income")


class ActionPlanArgs(BaseModel):
    horizon_months: int = Field(6, ge=6, le=24, description="Planning horizon in months (minimum 6)")
    goals: List[FinancialGoal] = Field(default_factory=list, description="Target savings or debt payoff goals")
    income_shock_percentage: float = Field(0.0, description="Income shock percentage to test plan resiliency")
    unexpected_expense: float = Field(0.0, ge=0.0, description="Unexpected expense to stress-test plan")


class RecommendationArgs(BaseModel):
    category_focus: Optional[str] = Field(None, description="Specific category to investigate recommendation for")


# ============================================================================
# Tool Implementation Functions (Deterministic Execution)
# ============================================================================

def execute_spending_analysis(
    args: SpendingAnalysisArgs,
    profile: FinancialProfile,
    transactions: List[Transaction]
) -> Dict[str, Any]:
    state_engine = FinancialStateEngine(profile.user_id)
    state = state_engine.calculate_state(transactions)

    currency = profile.home_currency
    category_filter = args.category.lower().strip() if args.category else None

    target_category_spending = 0.0
    category_found = False

    cat_list = []
    for c in state.category_spending:
        cat_list.append({"category": c.category, "total_amount": round(c.total_amount, 2)})
        if category_filter and (category_filter in c.category.lower() or c.category.lower() in category_filter):
            target_category_spending += c.total_amount
            category_found = True

    top_categories = sorted(cat_list, key=lambda x: x["total_amount"], reverse=True)[:5]

    return {
        "tool": "analyze_spending",
        "currency": currency,
        "total_expenses": round(state.expenses, 2),
        "essential_expenses": round(state.essential_expenses, 2),
        "discretionary_expenses": round(state.discretionary_expenses, 2),
        "savings_rate": round(state.savings_rate, 4),
        "top_categories": top_categories,
        "queried_category": args.category,
        "queried_category_amount": round(target_category_spending, 2) if category_found else None,
        "anomaly_count": len([a for a in state.anomalies if a.is_anomaly]),
        "data_period": f"Aggregated across {len(transactions)} historical transactions",
    }


def execute_financial_summary(
    args: FinancialSummaryArgs,
    profile: FinancialProfile,
    transactions: List[Transaction]
) -> Dict[str, Any]:
    state_engine = FinancialStateEngine(profile.user_id)
    state = state_engine.calculate_state(transactions)

    return {
        "tool": "get_financial_summary",
        "currency": profile.home_currency,
        "current_balance": round(profile.current_available_balance, 2),
        "minimum_buffer": round(profile.minimum_balance_to_keep, 2),
        "total_income": round(state.income, 2),
        "total_expenses": round(state.expenses, 2),
        "net_cash_flow": round(state.cash_flow, 2),
        "savings_rate": round(state.savings_rate, 4),
        "expense_ratio": round(state.expense_ratio, 4),
        "essential_expenses": round(state.essential_expenses, 2),
        "discretionary_expenses": round(state.discretionary_expenses, 2),
        "recurring_obligations": round(state.recurring_obligations, 2),
        "emi_burden": round(state.emi_burden, 2),
    }


def _load_prototype_payment_options(user_id: str, amount: float) -> List[PaymentOption]:
    """Helper to locate predefined installment options if available."""
    try:
        req_path = Path("data/prototype/requests.csv")
        opts_path = Path("data/prototype/request_payment_options.csv")
        if not req_path.exists() or not opts_path.exists():
            return []

        requests_df = pd.read_csv(req_path)
        payment_opts_df = pd.read_csv(opts_path)

        req_id = None
        for _, r in requests_df.iterrows():
            if str(r["user_id"]) == user_id and abs(float(r["requested_amount"]) - amount) < 1.0:
                req_id = r["request_id"]
                break

        if not req_id:
            return []

        opts = payment_opts_df[payment_opts_df["request_id"] == req_id]
        po_list = []
        for _, o in opts.iterrows():
            pfq = o["payment_frequency_days"]
            if pd.isna(pfq):
                pfq = None
            po_list.append(PaymentOption(
                payment_option_id=str(o["payment_option_id"]),
                request_id=str(o["request_id"]),
                payment_method=str(o["payment_method"]),
                payment_amount=float(o["payment_amount"]),
                number_of_payments=int(o["number_of_payments"]),
                first_payment_date=str(o["first_payment_date"]),
                payment_frequency_days=float(pfq) if pfq is not None else None,
                financing_fee=float(o["financing_fee"]),
                total_payable_amount=float(o["total_payable_amount"])
            ))
        return po_list
    except Exception:
        return []


def execute_affordability_check(
    args: AffordabilityCheckArgs,
    profile: FinancialProfile,
    transactions: List[Transaction]
) -> Dict[str, Any]:
    pred_engine = PredictionEngine()
    prediction = pred_engine.run_prediction(transactions, profile)

    if not prediction.available:
        return {
            "tool": "check_affordability",
            "status": "INSUFFICIENT_DATA",
            "reason": prediction.reason or "Minimum 3 months of transaction data required.",
            "currency": profile.home_currency,
        }

    payment_options = _load_prototype_payment_options(profile.user_id, args.purchase_amount)

    aff_engine = AffordabilityEngine(profile, prediction)
    result = aff_engine.evaluate_purchase(args.purchase_amount, payment_options)

    viable_options_dict = [o.model_dump() for o in result.viable_payment_options]

    return {
        "tool": "check_affordability",
        "currency": profile.home_currency,
        "purchase_amount": round(args.purchase_amount, 2),
        "affordability_status": result.status,
        "current_balance": round(profile.current_available_balance, 2),
        "minimum_buffer": round(profile.minimum_balance_to_keep, 2),
        "projected_net_cash_flow": round(
            prediction.projected_cash_flow.projected_cash_flow if prediction.projected_cash_flow else 0.0, 2
        ),
        "resulting_balance": round(result.resulting_balance, 2),
        "shortfall": round(result.shortfall, 2),
        "trade_off_required": round(result.trade_off_required, 2),
        "viable_options": viable_options_dict,
        "reasons": result.reasons,
    }


def execute_what_if_simulation(
    args: WhatIfSimulationArgs,
    profile: FinancialProfile,
    transactions: List[Transaction]
) -> Dict[str, Any]:
    pred_engine = PredictionEngine()
    prediction = pred_engine.run_prediction(transactions, profile)

    if not prediction.available:
        return {
            "tool": "simulate_what_if",
            "status": "INSUFFICIENT_DATA",
            "reason": prediction.reason or "Insufficient historical data for simulation.",
            "currency": profile.home_currency,
        }

    # Case 1: Income Shock or Unexpected Expense simulation using Constrained Action Planner / Forecaster
    if args.income_shock_percentage != 0.0 or args.unexpected_expense > 0.0:
        fc_req = ProbabilisticForecastRequest(
            horizon_months=6,
            confidence_level=0.90,
            income_shock_percentage=args.income_shock_percentage,
            unexpected_expense=args.unexpected_expense,
            unexpected_expense_period=1
        )
        prob_resp: ProbabilisticForecastResponse = pred_engine.run_probabilistic_forecast(
            transactions=transactions,
            profile=profile,
            request=fc_req
        )

        baseline_fc_req = ProbabilisticForecastRequest(horizon_months=6, confidence_level=0.90)
        baseline_resp: ProbabilisticForecastResponse = pred_engine.run_probabilistic_forecast(
            transactions=transactions,
            profile=profile,
            request=baseline_fc_req
        )

        p1 = prob_resp.periods[0] if prob_resp.periods else None
        b1 = baseline_resp.periods[0] if baseline_resp.periods else None

        base_cf = b1.projected_cash_flow.mean if b1 else 0.0
        shock_cf = p1.projected_cash_flow.mean if p1 else 0.0
        base_bal = b1.projected_cumulative_balance.mean if b1 else profile.current_available_balance
        shock_bal = p1.projected_cumulative_balance.mean if p1 else profile.current_available_balance
        shortfall_prob = p1.shortfall_probability if p1 else 0.0

        buffer_status = "breached" if shock_bal < profile.minimum_balance_to_keep else "maintained"

        return {
            "tool": "simulate_what_if",
            "scenario_type": "income_or_expense_shock",
            "currency": profile.home_currency,
            "income_shock_percentage": args.income_shock_percentage,
            "unexpected_expense": round(args.unexpected_expense, 2),
            "baseline_cash_flow": round(base_cf, 2),
            "scenario_cash_flow": round(shock_cf, 2),
            "baseline_balance": round(base_bal, 2),
            "scenario_balance": round(shock_bal, 2),
            "projected_balance": round(shock_bal, 2),
            "cash_flow_change": round(shock_cf - base_cf, 2),
            "balance_change": round(shock_bal - base_bal, 2),
            "buffer_status_change": buffer_status,
            "shortfall_probability": round(shortfall_prob, 4),
            "minimum_buffer": round(profile.minimum_balance_to_keep, 2),
        }

    # Case 2: Discretionary Spending Adjustment
    sim = WhatIfSimulator(profile, prediction)
    baseline = sim.baseline_scenario()
    change = args.change_amount

    if change is None or change == 0.0:
        return {
            "tool": "simulate_what_if",
            "scenario_type": "no_change",
            "currency": profile.home_currency,
            "projected_balance": round(baseline.projected_balance, 2),
            "baseline_cash_flow": round(baseline.projected_cash_flow, 2),
            "scenario_cash_flow": round(baseline.projected_cash_flow, 2),
            "buffer_status_change": "maintained" if not baseline.buffer_breached else "breached",
            "buffer_breached": baseline.buffer_breached,
            "minimum_buffer": round(profile.minimum_balance_to_keep, 2),
            "change_amount": 0.0,
            "note": "Baseline projection under no adjustments.",
        }

    if change < 0:
        # Reduction in spending
        reduction = abs(change)
        scenario = sim.simulate_reduce_discretionary_spending(reduction)
        impact = ImpactEngine.calculate_impact(baseline, scenario)
        summary = sim.compute_what_if_summary(baseline, scenario)
        return {
            "tool": "simulate_what_if",
            "scenario_type": "spending_reduction",
            "currency": profile.home_currency,
            "change_amount": round(reduction, 2),
            "baseline_balance": round(baseline.projected_balance, 2),
            "scenario_balance": round(scenario.projected_balance, 2),
            "projected_balance": round(scenario.projected_balance, 2),
            "baseline_cash_flow": round(baseline.projected_cash_flow, 2),
            "scenario_cash_flow": round(scenario.projected_cash_flow, 2),
            "cash_flow_change": round(impact.cash_flow_difference, 2),
            "balance_change": round(impact.balance_difference, 2),
            "buffer_status_change": impact.buffer_status_change,
            "buffer_breached": scenario.buffer_breached,
            "minimum_buffer": round(profile.minimum_balance_to_keep, 2),
            "monthly_summary": summary.model_dump(),
        }
    else:
        # Increase in spending
        scenario = sim.simulate_increase_spending(change)
        impact = ImpactEngine.calculate_impact(baseline, scenario)
        summary = sim.compute_what_if_summary(baseline, scenario)
        return {
            "tool": "simulate_what_if",
            "scenario_type": "spending_increase",
            "currency": profile.home_currency,
            "change_amount": round(change, 2),
            "baseline_balance": round(baseline.projected_balance, 2),
            "scenario_balance": round(scenario.projected_balance, 2),
            "projected_balance": round(scenario.projected_balance, 2),
            "baseline_cash_flow": round(baseline.projected_cash_flow, 2),
            "scenario_cash_flow": round(scenario.projected_cash_flow, 2),
            "cash_flow_change": round(impact.cash_flow_difference, 2),
            "balance_change": round(impact.balance_difference, 2),
            "buffer_status_change": impact.buffer_status_change,
            "buffer_breached": scenario.buffer_breached,
            "minimum_buffer": round(profile.minimum_balance_to_keep, 2),
            "monthly_summary": summary.model_dump(),
        }


def execute_cash_flow_forecast(
    args: CashFlowForecastArgs,
    profile: FinancialProfile,
    transactions: List[Transaction]
) -> Dict[str, Any]:
    pred_engine = PredictionEngine()
    fc_req = ProbabilisticForecastRequest(
        horizon_months=args.horizon_months,
        confidence_level=0.90,
        income_shock_percentage=args.income_shock_percentage
    )
    result: ProbabilisticForecastResponse = pred_engine.run_probabilistic_forecast(transactions, profile, fc_req)

    if not result.available or not result.periods:
        # Fall back to single-period prediction
        single_pred = pred_engine.run_prediction(transactions, profile)
        if not single_pred.available:
            return {
                "tool": "forecast_cash_flow",
                "status": "INSUFFICIENT_DATA",
                "reason": single_pred.reason or "Insufficient transaction history.",
                "currency": profile.home_currency,
            }
        pcf = single_pred.projected_cash_flow
        return {
            "tool": "forecast_cash_flow",
            "currency": profile.home_currency,
            "horizon_months": 1,
            "projected_income": round(pcf.projected_income, 2) if pcf else 0.0,
            "projected_expenses": round(pcf.projected_expenses, 2) if pcf else 0.0,
            "known_obligations": round(pcf.known_obligations, 2) if pcf else 0.0,
            "projected_cash_flow": round(pcf.projected_cash_flow, 2) if pcf else 0.0,
            "projected_balance": round(profile.current_available_balance + (pcf.projected_cash_flow if pcf else 0.0), 2),
            "minimum_buffer": round(profile.minimum_balance_to_keep, 2),
            "shortfall_probability": 0.0,
            "evaluation_metrics": None,
        }

    period_summaries = []
    max_shortfall_prob = 0.0
    for p in result.periods:
        max_shortfall_prob = max(max_shortfall_prob, p.shortfall_probability)
        period_summaries.append({
            "period": p.period,
            "period_index": p.period_index,
            "projected_income": round(p.projected_income.mean, 2),
            "essential_expenses": round(p.essential_expenses.mean, 2),
            "discretionary_expenses": round(p.discretionary_expenses.mean, 2),
            "known_obligations": round(p.known_obligations, 2),
            "net_cash_flow": round(p.projected_cash_flow.mean, 2),
            "cumulative_balance": round(p.projected_cumulative_balance.mean, 2),
            "uncertainty_std": round(p.projected_cumulative_balance.std_dev, 2),
            "shortfall_probability": round(p.shortfall_probability, 4),
            "buffer_breached": p.shortfall_probability > 0.05,
        })

    eval_dict = None
    if result.evaluation_metrics:
        eval_dict = {
            "income_mae": round(result.evaluation_metrics.income_mae, 2),
            "expense_mae": round(result.evaluation_metrics.expense_mae, 2),
            "expense_rmse": round(result.evaluation_metrics.expense_rmse, 2),
            "interval_coverage": round(result.evaluation_metrics.interval_coverage_ratio, 3),
        }

    first_p = period_summaries[0]
    return {
        "tool": "forecast_cash_flow",
        "currency": profile.home_currency,
        "horizon_months": len(period_summaries),
        "projected_income": first_p["projected_income"],
        "projected_expenses": round(first_p["essential_expenses"] + first_p["discretionary_expenses"], 2),
        "known_obligations": first_p["known_obligations"],
        "projected_cash_flow": first_p["net_cash_flow"],
        "projected_balance": first_p["cumulative_balance"],
        "minimum_buffer": round(profile.minimum_balance_to_keep, 2),
        "periods": period_summaries,
        "peak_shortfall_probability": round(max_shortfall_prob, 4),
        "uncertainty_method": result.uncertainty_method,
        "confidence_level": result.confidence_level,
        "evaluation_metrics": eval_dict,
    }


def execute_plan_evaluation(
    args: ActionPlanArgs,
    profile: FinancialProfile,
    transactions: List[Transaction]
) -> Dict[str, Any]:
    planner = ConstrainedPlannerEngine()
    req = PlanEvaluationRequest(
        horizon_months=args.horizon_months,
        goals=args.goals,
        income_shock_percentage=args.income_shock_percentage,
        unexpected_essential_expense=args.unexpected_expense
    )
    result: PlanEvaluationResponse = planner.evaluate_plans(transactions, profile, req)

    evaluated_plans = []
    for p in result.evaluated_plans:
        evaluated_plans.append({
            "plan_id": p.plan_id,
            "name": p.name,
            "strategy": p.strategy_description,
            "is_feasible": p.is_feasible,
            "shortfall_probability": round(p.shortfall_probability, 4),
            "max_shortfall": round(p.max_shortfall, 2),
            "ending_balance": round(p.cumulative_ending_balance, 2),
            "total_discretionary_trimmed": round(p.total_discretionary_reduction, 2),
            "constraint_violations": p.constraint_violations,
            "infeasible_goals": [g.model_dump() for g in p.infeasible_goals],
        })

    return {
        "tool": "evaluate_action_plans",
        "currency": profile.home_currency,
        "horizon_months": result.horizon_months,
        "declared_minimum_reserve": round(result.declared_minimum_reserve, 2),
        "current_balance": round(result.current_available_balance, 2),
        "recommended_plan_id": result.recommended_plan_id,
        "recommendation_rationale": result.recommendation_rationale,
        "uncertainty_changed_preference": result.uncertainty_changed_preference,
        "replanning_trigger_event": result.replanning_trigger_event,
        "plans": evaluated_plans,
    }


def execute_recommendation(
    args: RecommendationArgs,
    profile: FinancialProfile,
    transactions: List[Transaction]
) -> Dict[str, Any]:
    state_engine = FinancialStateEngine(profile.user_id)
    state = state_engine.calculate_state(transactions)
    pred_engine = PredictionEngine()
    prediction = pred_engine.run_prediction(transactions, profile)

    decision_engine = DecisionEngine(profile, state, prediction)
    trace = decision_engine.generate_recommendation_for_gap()

    if trace:
        return {
            "tool": "explain_recommendation",
            "currency": profile.home_currency,
            "recommendation_text": trace.recommendation.actionable_text,
            "recommendation_type": trace.recommendation.recommendation_type,
            "confidence_level": trace.recommendation.confidence_level,
            "confidence_reason": trace.recommendation.confidence_reason,
            "cash_flow_difference": trace.recommendation.expected_impact.cash_flow_difference,
            "balance_difference": trace.recommendation.expected_impact.balance_difference,
            "buffer_status_change": trace.recommendation.expected_impact.buffer_status_change,
            "observed_fact": trace.observed_fact,
            "calculation": trace.calculation,
            "prediction": trace.prediction,
            "simulation": trace.simulation,
        }

    return {
        "tool": "explain_recommendation",
        "currency": profile.home_currency,
        "recommendation_text": "Your projected cash flow and buffer are within acceptable ranges. No critical action required.",
        "confidence_level": "HIGH",
        "observed_fact": f"Current balance {profile.current_available_balance:.2f} is above minimum buffer {profile.minimum_balance_to_keep:.2f}.",
    }


# ============================================================================
# Allowlisted Tool Registry Map
# ============================================================================

FINANCIAL_TOOLS: Dict[str, Dict[str, Any]] = {
    "analyze_spending": {
        "schema": SpendingAnalysisArgs,
        "executor": execute_spending_analysis,
        "description": "Analyze user spending across categories, identifying essential vs discretionary spending and anomalies."
    },
    "get_financial_summary": {
        "schema": FinancialSummaryArgs,
        "executor": execute_financial_summary,
        "description": "Retrieve current balance, buffer, net cash flow, income, and total expenses summary."
    },
    "check_affordability": {
        "schema": AffordabilityCheckArgs,
        "executor": execute_affordability_check,
        "description": "Evaluate if a specific purchase amount is affordable upfront or via installment plans without breaching reserve."
    },
    "simulate_what_if": {
        "schema": WhatIfSimulationArgs,
        "executor": execute_what_if_simulation,
        "description": "Simulate what happens if spending changes, salary drops, or unexpected expenses occur."
    },
    "forecast_cash_flow": {
        "schema": CashFlowForecastArgs,
        "executor": execute_cash_flow_forecast,
        "description": "Forecast multi-period cash flow distributions, reserve breach probabilities, and uncertainty over 6-24 months."
    },
    "evaluate_action_plans": {
        "schema": ActionPlanArgs,
        "executor": execute_plan_evaluation,
        "description": "Compare candidate multi-period financial plans (Balanced Reserve vs Acceleration), evaluate goal feasibility and relaxations."
    },
    "explain_recommendation": {
        "schema": RecommendationArgs,
        "executor": execute_recommendation,
        "description": "Generate grounded recommendations with auditable decision traces and rationale for why an action is suggested."
    },
}
