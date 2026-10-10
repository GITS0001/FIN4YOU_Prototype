from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Literal
from datetime import date
from enum import Enum


# -----------------------------------------------------------------------------
# Probabilistic Forecasting Schemas
# -----------------------------------------------------------------------------
class DistributionSummary(BaseModel):
    mean: float
    median: float
    lower_bound: float  # e.g., p05 or p10 depending on confidence interval
    upper_bound: float  # e.g., p95 or p90
    std_dev: float
    confidence_level: float = 0.90


class ProbabilisticForecastPeriod(BaseModel):
    period_index: int  # 1 to 6+
    period: str  # YYYY-MM
    projected_income: DistributionSummary
    essential_expenses: DistributionSummary
    discretionary_expenses: DistributionSummary
    known_obligations: float
    projected_cash_flow: DistributionSummary
    projected_cumulative_balance: DistributionSummary
    probability_below_reserve: float = Field(
        ...,
        description="Probability that cumulative cash balance falls below declared minimum reserve P(Balance < Reserve)"
    )


class ForecastEvaluationMetrics(BaseModel):
    evaluation_periods_evaluated: int
    income_mae: float
    income_rmse: float
    expense_mae: float
    expense_rmse: float
    interval_coverage: float = Field(
        ...,
        description="Empirical proportion of held-out actuals falling within the prediction interval"
    )
    mean_interval_width: float = Field(
        ...,
        description="Average width of prediction interval across evaluated held-out periods"
    )
    baseline_model: str = "historical_average"
    baseline_income_mae: float
    baseline_expense_mae: float


class ProbabilisticForecastRequest(BaseModel):
    horizon_months: int = Field(default=6, ge=6, description="Forecast horizon in months (at least 6)")
    confidence_level: float = Field(default=0.90, ge=0.50, le=0.99, description="Confidence level for prediction intervals")
    uncertainty_method: str = Field(
        default="student_t_residual_growth",
        description="Documented uncertainty method (e.g. student_t_residual_growth or historical_residual_bootstrap)"
    )
    income_shock_percentage: Optional[float] = Field(
        default=0.0,
        description="Simulated percentage change in income, e.g. -0.20 for 20% income reduction"
    )
    unexpected_expense: Optional[float] = Field(
        default=0.0,
        description="Simulated unexpected essential expense added to period 1"
    )
    unexpected_expense_period: Optional[int] = Field(
        default=1,
        description="Period index for unexpected expense (1-based)"
    )


class ProbabilisticForecastResponse(BaseModel):
    user_id: str
    available: bool
    reason: Optional[str] = None
    horizon_months: int
    uncertainty_method: str
    confidence_level: float
    declared_minimum_reserve: float
    current_available_balance: float
    periods: List[ProbabilisticForecastPeriod] = []
    evaluation_metrics: Optional[ForecastEvaluationMetrics] = None
    baseline_comparison: Optional[Dict[str, Any]] = None


# -----------------------------------------------------------------------------
# Constrained Financial Action Planning Schemas
# -----------------------------------------------------------------------------
class ActionType(str, Enum):
    REDUCE_DISCRETIONARY = "reduce_discretionary"
    PAUSE_CATEGORY = "pause_category"
    ALLOCATE_SAVINGS = "allocate_savings"
    ACCELERATE_DEBT = "accelerate_debt"
    RESTRUCTURE_EXPENSE = "restructure_expense"
    NO_ACTION = "no_action"


class PeriodAction(BaseModel):
    period_index: int = Field(..., ge=1, le=12, description="Period month index (1-based)")
    action_type: ActionType
    category: Optional[str] = None
    amount: float = Field(..., ge=0.0, description="Dollar/Currency amount of the planned action")
    description: str


class FinancialGoal(BaseModel):
    goal_id: str
    name: str
    target_amount: float = Field(..., gt=0.0)
    target_period_index: int = Field(..., ge=1, le=12, description="Target period index (1-based)")
    priority: Literal["critical", "high", "medium", "low"] = "high"
    is_mandatory: bool = False


class GoalFeasibilityStatus(BaseModel):
    goal_id: str
    name: str
    target_amount: float
    target_period_index: int
    is_feasible: bool
    conflict_reason: Optional[str] = None
    accumulated_towards_goal: float = 0.0
    shortfall: float = 0.0
    proposed_relaxations: List[str] = []


class PeriodPlanProjection(BaseModel):
    period_index: int
    period: str
    starting_balance: float
    projected_income: float
    essential_expenses: float
    discretionary_expenses: float
    known_obligations: float
    action_modifications: float  # Net effect of actions on cash flow (+savings or -debt payment)
    net_cash_flow: float
    ending_balance_mean: float
    ending_balance_lower_p10: float
    ending_balance_upper_p90: float
    declared_minimum_reserve: float
    probability_below_reserve: float = Field(
        ...,
        description="Estimated probability that ending balance falls below declared minimum reserve"
    )
    reserve_breached: bool
    actions_taken: List[PeriodAction] = []
    trade_offs_identified: List[str] = []


class CandidateActionPlan(BaseModel):
    plan_id: str
    name: str
    strategy_description: str
    actions: List[PeriodAction] = []
    uncertainty_multiplier: float = Field(
        default=1.0,
        ge=0.1,
        le=5.0,
        description="Multiplier on cash flow uncertainty representing strategy risk profile"
    )


class EvaluatedPlanResult(BaseModel):
    plan_id: str
    name: str
    strategy_description: str
    projections: List[PeriodPlanProjection] = []
    final_projected_balance_mean: float
    final_projected_balance_lower_p10: float
    final_projected_balance_upper_p90: float
    average_shortfall_probability: float
    max_shortfall_probability: float
    reserve_breach_count: int
    goals_feasibility: List[GoalFeasibilityStatus] = []
    all_goals_feasible: bool
    trade_off_summary: List[str] = []
    risk_score: float = Field(
        ...,
        description="Composite risk score considering shortfall probability and reserve proximity"
    )


class PlanEvaluationRequest(BaseModel):
    horizon_months: int = Field(default=6, ge=6, description="Planning horizon across at least six monthly periods")
    declared_minimum_reserve: Optional[float] = Field(
        default=None,
        description="Declared minimum cash reserve override (uses user profile buffer if omitted)"
    )
    goals: List[FinancialGoal] = Field(default_factory=list, description="Target financial goals")
    candidate_plans: Optional[List[CandidateActionPlan]] = Field(
        default=None,
        description="Candidate action sequences to compare. If omitted, engine generates standard candidate sequences."
    )
    income_shock_percentage: float = Field(
        default=0.0,
        description="Simulated income change (e.g., -0.20 for 20% reduction) for replanning"
    )
    unexpected_essential_expense: float = Field(
        default=0.0,
        description="Simulated unexpected essential expense in period 1"
    )


class PlanEvaluationResponse(BaseModel):
    user_id: str
    horizon_months: int
    declared_minimum_reserve: float
    current_available_balance: float
    evaluated_plans: List[EvaluatedPlanResult] = []
    recommended_plan_id: str
    recommendation_rationale: str
    uncertainty_changed_preference: bool = Field(
        ...,
        description="True if a plan with lower expected ending balance was preferred because its uncertainty/shortfall risk was significantly safer"
    )
    replan_notice: Optional[str] = None
