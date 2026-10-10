import math
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from copy import deepcopy

from app.schemas.financial import FinancialProfile, Transaction
from app.schemas.planner import (
    ActionType, PeriodAction, FinancialGoal, GoalFeasibilityStatus,
    PeriodPlanProjection, CandidateActionPlan, EvaluatedPlanResult,
    PlanEvaluationRequest, PlanEvaluationResponse, ProbabilisticForecastRequest,
    ProbabilisticForecastResponse
)
from app.ml.forecasting import PredictionEngine


class ConstrainedPlannerEngine:
    """
    Addition 1 — Constrained Financial Action Planning Engine.
    Plans across at least six monthly periods.
    Accounts for income, essential expenses, discretionary expenses, debt obligations,
    and a declared minimum cash reserve.
    Evaluates candidate action sequences under probabilistic cash-flow forecasts.
    Identifies infeasible goals and proposes explicit relaxations.
    Selects recommendations taking shortfall risk and forecast uncertainty into account.
    """

    def __init__(self, prediction_engine: Optional[PredictionEngine] = None):
        self.prediction_engine = prediction_engine or PredictionEngine()

    def generate_default_candidate_plans(
        self,
        horizon_months: int,
        base_discretionary: float,
        goals: List[FinancialGoal]
    ) -> List[CandidateActionPlan]:
        """
        Generates standard candidate action sequences to compare when client
        does not specify custom candidate sequences.
        Ensures at least two distinct strategies are always evaluated.
        """
        # Plan 1: Balanced Reserve & Sustainable Discipline
        # Reduces discretionary spending moderately (20%) each month to protect reserve
        mod_reduction = round(max(50.0, base_discretionary * 0.20), 2)
        plan1_actions = [
            PeriodAction(
                period_index=p,
                action_type=ActionType.REDUCE_DISCRETIONARY,
                category="discretionary_general",
                amount=mod_reduction,
                description=f"Trim discretionary spending by ${mod_reduction:,.2f} to protect cash buffer"
            )
            for p in range(1, horizon_months + 1)
        ]

        plan1 = CandidateActionPlan(
            plan_id="plan_balanced_reserve",
            name="Balanced Reserve & Discipline",
            strategy_description="Moderate 20% discretionary spending reduction to build and maintain a protective cash reserve buffer.",
            actions=plan1_actions
        )

        # Plan 2: Aggressive Acceleration (Growth / Fast Goal Payoff)
        # Allocates heavily towards savings/debt in early months without trimming variable spend
        early_alloc = round(max(100.0, base_discretionary * 0.40), 2)
        plan2_actions = [
            PeriodAction(
                period_index=p,
                action_type=ActionType.ACCELERATE_DEBT if p <= 2 else ActionType.NO_ACTION,
                amount=early_alloc if p <= 2 else 0.0,
                description=f"Aggressively allocate ${early_alloc:,.2f} towards goal/debt paydown" if p <= 2 else "Standard flow"
            )
            for p in range(1, horizon_months + 1)
        ]

        plan2 = CandidateActionPlan(
            plan_id="plan_aggressive_acceleration",
            name="Aggressive Acceleration",
            strategy_description="Prioritizes rapid early-month debt payoff or goal acceleration, accepting lower cash buffer margins.",
            actions=plan2_actions
        )

        # Plan 3: Liquidity Preservation (Conservative)
        # Pauses 40% discretionary spend throughout the horizon
        heavy_reduction = round(max(80.0, base_discretionary * 0.40), 2)
        plan3_actions = [
            PeriodAction(
                period_index=p,
                action_type=ActionType.REDUCE_DISCRETIONARY,
                category="discretionary_general",
                amount=heavy_reduction,
                description=f"Strictly reduce discretionary spending by ${heavy_reduction:,.2f}"
            )
            for p in range(1, horizon_months + 1)
        ]

        plan3 = CandidateActionPlan(
            plan_id="plan_conservative_liquidity",
            name="Conservative Liquidity Preservation",
            strategy_description="Maximum spending pause to eliminate shortfall risk under adverse scenarios.",
            actions=plan3_actions
        )

        return [plan1, plan2, plan3]

    def evaluate_plans(
        self,
        transactions: List[Transaction],
        profile: FinancialProfile,
        request: PlanEvaluationRequest
    ) -> PlanEvaluationResponse:
        """
        Executes full constrained action plan evaluation:
        1. Runs probabilistic cash-flow forecast across horizon.
        2. Applies candidate action sequences period by period.
        3. Computes projected balances, shortfall probabilities, and constraint violations.
        4. Identifies infeasible goals and details relaxations.
        5. Formulates recommendation considering forecast uncertainty.
        """
        horizon = max(6, request.horizon_months)
        declared_reserve = (
            request.declared_minimum_reserve
            if request.declared_minimum_reserve is not None
            else profile.minimum_balance_to_keep
        )
        current_balance = profile.current_available_balance

        # 1. Run baseline probabilistic forecast with any requested shocks
        fc_req = ProbabilisticForecastRequest(
            horizon_months=horizon,
            confidence_level=0.90,
            income_shock_percentage=request.income_shock_percentage,
            unexpected_expense=request.unexpected_essential_expense,
            unexpected_expense_period=1
        )
        forecast_response: ProbabilisticForecastResponse = self.prediction_engine.run_probabilistic_forecast(
            transactions=transactions,
            profile=profile,
            request=fc_req
        )

        if not forecast_response.available:
            return PlanEvaluationResponse(
                user_id=profile.user_id,
                horizon_months=horizon,
                declared_minimum_reserve=declared_reserve,
                current_available_balance=current_balance,
                evaluated_plans=[],
                recommended_plan_id="",
                recommendation_rationale=f"Cannot evaluate plans: {forecast_response.reason}",
                uncertainty_changed_preference=False
            )

        # Baseline discretionary expense benchmark for generating default plans
        base_disc = (
            forecast_response.periods[0].discretionary_expenses.mean
            if forecast_response.periods
            else 500.0
        )

        candidate_plans = (
            request.candidate_plans
            if (request.candidate_plans and len(request.candidate_plans) >= 2)
            else self.generate_default_candidate_plans(horizon, base_disc, request.goals)
        )

        evaluated_plans: List[EvaluatedPlanResult] = []

        # 2. Evaluate each candidate plan
        for plan in candidate_plans:
            plan_result = self._evaluate_single_plan(
                plan=plan,
                forecast=forecast_response,
                starting_balance=current_balance,
                declared_reserve=declared_reserve,
                goals=request.goals
            )
            evaluated_plans.append(plan_result)

        # 3. Recommendation decision engine (considering shortfall risk & uncertainty)
        recommended_plan, rationale, uncertainty_changed = self._select_recommended_plan(
            evaluated_plans=evaluated_plans,
            declared_reserve=declared_reserve
        )

        replan_notice = None
        if request.income_shock_percentage != 0.0 or request.unexpected_essential_expense > 0.0:
            replan_notice = (
                f"Replanned active action sequence under updated conditions: "
                f"Income change={request.income_shock_percentage:+.1%}, "
                f"Unexpected essential expense=${request.unexpected_essential_expense:,.2f}."
            )

        return PlanEvaluationResponse(
            user_id=profile.user_id,
            horizon_months=horizon,
            declared_minimum_reserve=declared_reserve,
            current_available_balance=current_balance,
            evaluated_plans=evaluated_plans,
            recommended_plan_id=recommended_plan.plan_id,
            recommendation_rationale=rationale,
            uncertainty_changed_preference=uncertainty_changed,
            replan_notice=replan_notice
        )

    def _evaluate_single_plan(
        self,
        plan: CandidateActionPlan,
        forecast: ProbabilisticForecastResponse,
        starting_balance: float,
        declared_reserve: float,
        goals: List[FinancialGoal]
    ) -> EvaluatedPlanResult:
        """
        Simulates cash balance evolution period-by-period under the specific candidate plan.
        """
        # Index actions by period_index
        actions_by_period: Dict[int, List[PeriodAction]] = defaultdict(list)
        for act in plan.actions:
            actions_by_period[act.period_index].append(act)

        projections: List[PeriodPlanProjection] = []
        running_mean_balance = starting_balance
        running_variance_balance = 0.0

        reserve_breach_count = 0
        all_shortfall_probs = []
        trade_offs_collected = []

        for p_idx, fc_period in enumerate(forecast.periods, start=1):
            p_actions = actions_by_period.get(p_idx, [])

            # Compute modification to net cash flow from actions in this period
            # Reducing discretionary expenditure increases surplus (+ net cash flow)
            # Accelerating debt or savings allocation decreases liquid cash (- net cash flow)
            action_mod = 0.0
            p_trade_offs = []

            for act in p_actions:
                if act.action_type in [ActionType.REDUCE_DISCRETIONARY, ActionType.PAUSE_CATEGORY]:
                    # Cannot reduce more than discretionary spending in that period
                    effective_reduction = min(act.amount, fc_period.discretionary_expenses.mean)
                    action_mod += effective_reduction
                    p_trade_offs.append(f"Reduced discretionary spend by ${effective_reduction:,.2f} ({act.description})")
                elif act.action_type in [ActionType.ACCELERATE_DEBT, ActionType.ALLOCATE_SAVINGS]:
                    action_mod -= act.amount
                    p_trade_offs.append(f"Outflow of ${act.amount:,.2f} for {act.description}")

            trade_offs_collected.extend(p_trade_offs)

            # Planned period cash flow
            planned_net_cf = fc_period.projected_cash_flow.mean + action_mod
            plan_unc_mult = getattr(plan, "uncertainty_multiplier", 1.0) or 1.0
            period_cf_std = fc_period.projected_cash_flow.std_dev * plan_unc_mult

            # Update cumulative balance
            start_bal = running_mean_balance
            running_mean_balance += planned_net_cf
            running_variance_balance += (period_cf_std ** 2)
            cum_bal_std = math.sqrt(running_variance_balance)

            # Bounds at 90% confidence
            bal_lower_p10 = running_mean_balance - 1.645 * cum_bal_std
            bal_upper_p90 = running_mean_balance + 1.645 * cum_bal_std

            # Probability of falling below reserve in period p
            if cum_bal_std > 0:
                z = (declared_reserve - running_mean_balance) / cum_bal_std
                prob_below_res = max(0.0, min(1.0, 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))))
            else:
                prob_below_res = 1.0 if running_mean_balance < declared_reserve else 0.0

            all_shortfall_probs.append(prob_below_res)
            reserve_breached = running_mean_balance < declared_reserve or prob_below_res > 0.35
            if reserve_breached:
                reserve_breach_count += 1

            projections.append(
                PeriodPlanProjection(
                    period_index=p_idx,
                    period=fc_period.period,
                    starting_balance=round(start_bal, 2),
                    projected_income=fc_period.projected_income.mean,
                    essential_expenses=fc_period.essential_expenses.mean,
                    discretionary_expenses=fc_period.discretionary_expenses.mean,
                    known_obligations=fc_period.known_obligations,
                    action_modifications=round(action_mod, 2),
                    net_cash_flow=round(planned_net_cf, 2),
                    ending_balance_mean=round(running_mean_balance, 2),
                    ending_balance_lower_p10=round(bal_lower_p10, 2),
                    ending_balance_upper_p90=round(bal_upper_p90, 2),
                    declared_minimum_reserve=round(declared_reserve, 2),
                    probability_below_reserve=round(prob_below_res, 4),
                    reserve_breached=reserve_breached,
                    actions_taken=p_actions,
                    trade_offs_identified=p_trade_offs
                )
            )

        # 3. Infeasible Goal Analysis & Proposed Relaxations
        goals_feasibility: List[GoalFeasibilityStatus] = []
        all_goals_feasible = True

        for g in goals:
            t_idx = min(len(projections), max(1, g.target_period_index))
            proj_at_target = projections[t_idx - 1]

            # Available buffer above reserve at target month
            available_surplus = proj_at_target.ending_balance_mean - declared_reserve
            is_feasible = available_surplus >= g.target_amount and proj_at_target.probability_below_reserve < 0.20

            conflict_reason = None
            relaxations = []
            shortfall = 0.0

            if not is_feasible:
                all_goals_feasible = False
                shortfall = max(0.0, g.target_amount - max(0.0, available_surplus))
                conflict_reason = (
                    f"Goal '{g.name}' requires ${g.target_amount:,.2f} by month {g.target_period_index}, "
                    f"but expected surplus above minimum reserve (${declared_reserve:,.2f}) is only "
                    f"${max(0.0, available_surplus):,.2f} (shortfall of ${shortfall:,.2f}) "
                    f"with a {proj_at_target.probability_below_reserve:.1%} probability of reserve breach."
                )

                # Generate explicit proposed relaxations
                alt_month = min(len(projections), g.target_period_index + 3)
                relaxations.append(
                    f"Timeline relaxation: Extend target completion date from month {g.target_period_index} to month {alt_month}."
                )
                scaled_target = max(100.0, g.target_amount - shortfall)
                relaxations.append(
                    f"Amount relaxation: Scale target contribution down to ${scaled_target:,.2f}."
                )
                needed_monthly_cut = round(shortfall / max(1, g.target_period_index), 2)
                relaxations.append(
                    f"Discretionary adjustment: Cut discretionary spending by an additional ${needed_monthly_cut:,.2f}/month."
                )

            goals_feasibility.append(
                GoalFeasibilityStatus(
                    goal_id=g.goal_id,
                    name=g.name,
                    target_amount=g.target_amount,
                    target_period_index=g.target_period_index,
                    is_feasible=is_feasible,
                    conflict_reason=conflict_reason,
                    accumulated_towards_goal=round(max(0.0, available_surplus), 2),
                    shortfall=round(shortfall, 2),
                    proposed_relaxations=relaxations
                )
            )

        avg_shortfall_prob = sum(all_shortfall_probs) / len(all_shortfall_probs) if all_shortfall_probs else 0.0
        max_shortfall_prob = max(all_shortfall_probs) if all_shortfall_probs else 0.0

        # Composite risk score: weighted combination of max shortfall prob and breach count
        risk_score = round(max_shortfall_prob * 70.0 + reserve_breach_count * 15.0, 2)

        return EvaluatedPlanResult(
            plan_id=plan.plan_id,
            name=plan.name,
            strategy_description=plan.strategy_description,
            projections=projections,
            final_projected_balance_mean=round(running_mean_balance, 2),
            final_projected_balance_lower_p10=round(bal_lower_p10, 2),
            final_projected_balance_upper_p90=round(bal_upper_p90, 2),
            average_shortfall_probability=round(avg_shortfall_prob, 4),
            max_shortfall_probability=round(max_shortfall_prob, 4),
            reserve_breach_count=reserve_breach_count,
            goals_feasibility=goals_feasibility,
            all_goals_feasible=all_goals_feasible,
            trade_off_summary=list(set(trade_offs_collected)),
            risk_score=risk_score
        )

    def _select_recommended_plan(
        self,
        evaluated_plans: List[EvaluatedPlanResult],
        declared_reserve: float
    ) -> Tuple[EvaluatedPlanResult, str, bool]:
        """
        Risk-aware decision selection:
        Evaluates trade-offs between expected ending balance and forecast uncertainty / shortfall probability.
        Demonstrates cases where uncertainty alters plan preference:
        A plan with a higher expected balance is rejected if its shortfall risk is unacceptable.
        """
        if not evaluated_plans:
            raise ValueError("No plans evaluated.")

        # Sort by expected balance (highest first) - what a naive risk-neutral planner would pick
        plans_by_expected_balance = sorted(
            evaluated_plans,
            key=lambda p: p.final_projected_balance_mean,
            reverse=True
        )

        naive_choice = plans_by_expected_balance[0]

        # Filter safe plans: max shortfall probability <= 15% and 0 reserve breaches
        safe_plans = [
            p for p in evaluated_plans
            if p.max_shortfall_probability <= 0.15 and p.reserve_breach_count == 0
        ]

        uncertainty_changed = False

        if safe_plans:
            # Among safe plans, select the one with highest expected ending balance
            best_safe = max(safe_plans, key=lambda p: p.final_projected_balance_mean)

            if best_safe.plan_id != naive_choice.plan_id:
                # Key Requirement: Uncertainty changed the preferred plan!
                uncertainty_changed = True
                rationale = (
                    f"Plan '{best_safe.name}' is strongly recommended over '{naive_choice.name}' "
                    f"due to forecast uncertainty. While '{naive_choice.name}' offers a higher expected balance "
                    f"(${naive_choice.final_projected_balance_mean:,.2f} vs ${best_safe.final_projected_balance_mean:,.2f}), "
                    f"it incurs an unacceptable {naive_choice.max_shortfall_probability:.1%} probability of breaching "
                    f"your minimum cash reserve (${declared_reserve:,.2f}). '{best_safe.name}' limits maximum reserve "
                    f"shortfall probability to {best_safe.max_shortfall_probability:.1%}, providing resilient liquidity."
                )
                return best_safe, rationale, uncertainty_changed
            else:
                rationale = (
                    f"Plan '{best_safe.name}' is recommended. It delivers the highest expected ending balance "
                    f"(${best_safe.final_projected_balance_mean:,.2f}) while comfortably maintaining your declared "
                    f"minimum cash reserve (${declared_reserve:,.2f}) with a safe shortfall risk of "
                    f"{best_safe.max_shortfall_probability:.1%}."
                )
                return best_safe, rationale, False
        else:
            # If no plan is strictly under 15% shortfall risk, pick the one with lowest risk score
            safest_plan = min(evaluated_plans, key=lambda p: p.risk_score)
            if safest_plan.plan_id != naive_choice.plan_id:
                uncertainty_changed = True
                rationale = (
                    f"Plan '{safest_plan.name}' is recommended under constrained risk management. "
                    f"Under current market uncertainty, '{naive_choice.name}' presents an extreme "
                    f"{naive_choice.max_shortfall_probability:.1%} shortfall probability. "
                    f"'{safest_plan.name}' minimizes downside volatility."
                )
            else:
                rationale = (
                    f"Plan '{safest_plan.name}' is selected as the best available option under tight cash flow constraints."
                )
            return safest_plan, rationale, uncertainty_changed
