import math
from typing import List, Dict, Tuple, Optional, Any
from datetime import date
from collections import defaultdict

from app.schemas.financial import (
    Transaction, FinancialProfile, ForecastResult, ForecastEvaluation,
    FutureObligation, ProjectedCashFlow, CashFlowGap, PredictionEngineResult
)

class PredictionEngine:
    """
    Phase 3 Prediction Engine.
    Uses historical monthly averages to forecast variable income and expenses.
    Evaluates via chronological train/test split.
    Carries forward deterministic known future obligations.
    Calculates projected cash flow and cash flow gap detection.
    """

    def __init__(self, min_months_required: int = 3):
        self.min_months_required = min_months_required

    def _get_month_key(self, d: date) -> str:
        return f"{d.year}-{d.month:02d}"

    def run_prediction(self, transactions: List[Transaction], profile: FinancialProfile) -> PredictionEngineResult:
        if not transactions:
            return PredictionEngineResult(available=False, reason="No transactions found")

        # Group by month
        monthly_income: Dict[str, float] = defaultdict(float)
        monthly_variable_expenses: Dict[str, float] = defaultdict(float)

        # Track latest month's obligations
        latest_month_obligations = []

        for t in transactions:
            month_key = self._get_month_key(t.event_date)
            if t.event_type == "income":
                monthly_income[month_key] += t.amount
            elif t.event_type == "refund":
                if t.flexibility != "fixed" and t.event_type not in ["subscription", "debt_payment"]:
                    monthly_variable_expenses[month_key] -= t.amount
            elif t.direction == "debit":
                if t.flexibility == "fixed" or t.event_type in ["subscription", "debt_payment"]:
                    # Will collect obligations later from the latest month
                    pass
                else:
                    monthly_variable_expenses[month_key] += t.amount

        sorted_months = sorted(list(set(monthly_income.keys()).union(monthly_variable_expenses.keys())))

        if len(sorted_months) < self.min_months_required:
            return PredictionEngineResult(
                available=False,
                reason=f"Insufficient historical observations. Found {len(sorted_months)} months, require {self.min_months_required}."
            )

        # Train/Test Split (Chronological)
        # Test = last month, Train = all previous months
        test_month = sorted_months[-1]
        train_months = sorted_months[:-1]

        # Evaluate Income Forecast (Historical Mean vs 2-Month Moving Average)
        train_incomes = [monthly_income[m] for m in train_months]
        test_income = monthly_income[test_month]

        avg_train_income = sum(train_incomes) / len(train_incomes) if train_incomes else 0.0
        income_mae_hm = abs(avg_train_income - test_income)

        ma2_train_income = sum(train_incomes[-2:]) / min(2, len(train_incomes)) if train_incomes else 0.0
        income_mae_ma = abs(ma2_train_income - test_income)

        # Select Best Model for Income
        all_incomes = [monthly_income[m] for m in sorted_months]
        if income_mae_ma < income_mae_hm and len(all_incomes) >= 2:
            final_forecast_income = sum(all_incomes[-2:]) / 2.0
            best_income_model = "moving_average_2m"
            income_mae = income_mae_ma
        else:
            final_forecast_income = sum(all_incomes) / len(all_incomes) if all_incomes else 0.0
            best_income_model = "historical_mean"
            income_mae = income_mae_hm

        income_std = self._calc_std(all_incomes)

        # Evaluate Variable Expense Forecast
        train_var_exp = [monthly_variable_expenses[m] for m in train_months]
        test_var_exp = monthly_variable_expenses[test_month]

        avg_train_var_exp = sum(train_var_exp) / len(train_var_exp) if train_var_exp else 0.0
        exp_mae_hm = abs(avg_train_var_exp - test_var_exp)

        ma2_train_var_exp = sum(train_var_exp[-2:]) / min(2, len(train_var_exp)) if train_var_exp else 0.0
        exp_mae_ma = abs(ma2_train_var_exp - test_var_exp)

        # Select Best Model for Expenses
        all_var_exp = [monthly_variable_expenses[m] for m in sorted_months]
        if exp_mae_ma < exp_mae_hm and len(all_var_exp) >= 2:
            final_forecast_var_exp = sum(all_var_exp[-2:]) / 2.0
            best_exp_model = "moving_average_2m"
            exp_mae = exp_mae_ma
        else:
            final_forecast_var_exp = sum(all_var_exp) / len(all_var_exp) if all_var_exp else 0.0
            best_exp_model = "historical_mean"
            exp_mae = exp_mae_hm

        var_exp_std = self._calc_std(all_var_exp)

        # Future Obligations (from the most recent month)
        obligations = []
        total_obligations = 0.0
        for t in transactions:
            if self._get_month_key(t.event_date) == test_month and t.direction == "debit":
                if t.flexibility == "fixed" or t.event_type in ["subscription", "debt_payment"]:
                    obligations.append(
                        FutureObligation(
                            description=t.description,
                            category=t.category if t.category else "unknown",
                            expected_amount=t.amount,
                            expected_period="next_month"
                        )
                    )
                    total_obligations += t.amount

        # Results packaging
        forecasts = [
            ForecastResult(
                metric="total_income",
                horizon="next_month",
                prediction=final_forecast_income,
                confidence=0.85 if len(sorted_months) >= 3 else 0.50,
                model=best_income_model,
                uncertainty=income_std,
                evidence=[f"Based on {len(sorted_months)} months of historical data.", f"Prediction using {best_income_model}."],
                evaluation=ForecastEvaluation(mae=income_mae, rmse=income_mae) # For 1 test point, MAE == RMSE
            ),
            ForecastResult(
                metric="variable_expenses",
                horizon="next_month",
                prediction=final_forecast_var_exp,
                confidence=0.80 if len(sorted_months) >= 3 else 0.45,
                model=best_exp_model,
                uncertainty=var_exp_std,
                evidence=[f"Based on {len(sorted_months)} months of variable expense history.", f"Prediction using {best_exp_model}."],
                evaluation=ForecastEvaluation(mae=exp_mae, rmse=exp_mae)
            )
        ]

        projected_cash_flow = None
        gap_detection = None

        projected_cash_flows = []
        gap_detections = []

        current_balance = profile.current_available_balance

        # Determine the test month (last observed month)
        parts = test_month.split("-")
        test_yr, test_mo = int(parts[0]), int(parts[1])

        for m in range(1, 7):
            mo_val = test_mo + m
            yr_val = test_yr + (mo_val - 1) // 12
            mo_val = (mo_val - 1) % 12 + 1
            period_name = f"{yr_val}-{mo_val:02d}"

            pcf = ProjectedCashFlow(
                period=period_name,
                projected_income=final_forecast_income,
                projected_expenses=final_forecast_var_exp,
                known_obligations=total_obligations,
                projected_cash_flow=final_forecast_income - final_forecast_var_exp - total_obligations
            )
            projected_cash_flows.append(pcf)

            current_balance += pcf.projected_cash_flow
            shortfall = profile.minimum_balance_to_keep - current_balance

            gap = CashFlowGap(
                detected=shortfall > 0,
                period=period_name,
                projected_balance=current_balance,
                required_buffer=profile.minimum_balance_to_keep,
                shortfall=shortfall if shortfall > 0 else 0.0
            )
            gap_detections.append(gap)

            if m == 1:
                projected_cash_flow = pcf
                gap_detection = gap

        return PredictionEngineResult(
            available=True,
            forecasts=forecasts,
            obligations=obligations,
            projected_cash_flow=projected_cash_flow,
            gap_detection=gap_detection,
            projected_cash_flows=projected_cash_flows,
            gap_detections=gap_detections
        )

    def _calc_std(self, values: List[float]) -> float:
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    @staticmethod
    def _normal_cdf(x: float) -> float:
        """Standard Normal Cumulative Distribution Function using error function erf."""
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    @staticmethod
    def _get_t_critical(confidence_level: float, df: int) -> float:
        """
        Approximate two-tailed Student-t critical values.
        Supports df >= 1 with convergence to standard normal z for larger df.
        """
        # Exact lookup table for small degrees of freedom
        t_table_90 = {1: 6.314, 2: 2.920, 3: 2.353, 4: 2.132, 5: 2.015, 6: 1.943, 8: 1.860, 10: 1.812, 20: 1.725}
        t_table_95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 8: 2.306, 10: 2.228, 20: 2.086}
        t_table_80 = {1: 3.078, 2: 1.886, 3: 1.638, 4: 1.533, 5: 1.476, 6: 1.440, 8: 1.397, 10: 1.372, 20: 1.325}

        if confidence_level >= 0.94:
            table = t_table_95
            normal_val = 1.960
        elif confidence_level >= 0.88:
            table = t_table_90
            normal_val = 1.645
        else:
            table = t_table_80
            normal_val = 1.282

        if df in table:
            return table[df]
        for k in sorted(table.keys()):
            if df <= k:
                return table[k]
        return normal_val

    def run_probabilistic_forecast(
        self,
        transactions: List[Transaction],
        profile: FinancialProfile,
        request: Optional[Any] = None
    ) -> Any:
        """
        Addition 2 — Probabilistic Cash-Flow Forecasting across >= 6 monthly periods.
        Produces prediction distributions for income, essential expenses, discretionary expenses,
        net cash flow, and cumulative balance.
        Estimates the probability of falling below the declared minimum cash reserve.
        Evaluates on held-out periods and reports MAE, RMSE, interval coverage and width.
        """
        from app.schemas.planner import (
            DistributionSummary, ProbabilisticForecastPeriod, ForecastEvaluationMetrics,
            ProbabilisticForecastRequest, ProbabilisticForecastResponse
        )

        req = request or ProbabilisticForecastRequest()
        horizon = max(6, req.horizon_months)
        conf_level = req.confidence_level

        declared_reserve = profile.minimum_balance_to_keep
        current_balance = profile.current_available_balance

        if not transactions:
            return ProbabilisticForecastResponse(
                user_id=profile.user_id,
                available=False,
                reason="No transactions available for forecasting.",
                horizon_months=horizon,
                uncertainty_method=req.uncertainty_method,
                confidence_level=conf_level,
                declared_minimum_reserve=declared_reserve,
                current_available_balance=current_balance,
            )

        # 1. Group transactions chronologically into monthly buckets
        monthly_income: Dict[str, float] = defaultdict(float)
        monthly_essential: Dict[str, float] = defaultdict(float)
        monthly_discretionary: Dict[str, float] = defaultdict(float)
        all_months_set = set()

        for t in transactions:
            mk = self._get_month_key(t.event_date)
            all_months_set.add(mk)
            if t.event_type == "income":
                monthly_income[mk] += t.amount
            elif t.event_type == "refund":
                if t.flexibility == "fixed":
                    monthly_essential[mk] -= t.amount
                else:
                    monthly_discretionary[mk] -= t.amount
            elif t.direction == "debit":
                if t.flexibility == "fixed" or t.event_type in ["subscription", "debt_payment"]:
                    monthly_essential[mk] += t.amount
                else:
                    monthly_discretionary[mk] += t.amount

        sorted_months = sorted(list(all_months_set))
        num_months = len(sorted_months)

        if num_months < self.min_months_required:
            return ProbabilisticForecastResponse(
                user_id=profile.user_id,
                available=False,
                reason=f"Insufficient historical observations. Found {num_months} months, minimum {self.min_months_required} required.",
                horizon_months=horizon,
                uncertainty_method=req.uncertainty_method,
                confidence_level=conf_level,
                declared_minimum_reserve=declared_reserve,
                current_available_balance=current_balance,
            )

        # 2. Chronological Expanding-Window Rolling-Origin Evaluation
        # When num_months >= 4, evaluate multi-origin backtesting over the later historical months.
        # Strict temporal order: models at origin t are trained exclusively on data prior to t.
        if num_months >= 4:
            eval_origins = list(range(max(2, num_months - 3), num_months))
        else:
            eval_origins = [num_months - 1]

        eval_inc_maes: List[float] = []
        eval_exp_maes: List[float] = []
        eval_bl_inc_maes: List[float] = []
        eval_bl_exp_maes: List[float] = []
        eval_coverages: List[float] = []
        eval_widths: List[float] = []

        for o_idx in eval_origins:
            origin_train_months = sorted_months[:o_idx]
            origin_test_month = sorted_months[o_idx]
            o_train_df = max(1, len(origin_train_months) - 1)
            t_crit_origin = self._get_t_critical(conf_level, o_train_df)

            o_tr_incomes = [monthly_income[m] for m in origin_train_months]
            o_tr_essentials = [monthly_essential[m] for m in origin_train_months]
            o_tr_discretionary = [monthly_discretionary[m] for m in origin_train_months]
            o_tr_total_exp = [o_tr_essentials[i] + o_tr_discretionary[i] for i in range(len(origin_train_months))]

            act_o_inc = monthly_income[origin_test_month]
            act_o_ess = monthly_essential[origin_test_month]
            act_o_disc = monthly_discretionary[origin_test_month]
            act_o_exp = act_o_ess + act_o_disc

            # Baseline model: Historical mean of strictly prior window
            o_bl_inc = sum(o_tr_incomes) / len(o_tr_incomes) if o_tr_incomes else 0.0
            o_bl_exp = sum(o_tr_total_exp) / len(o_tr_total_exp) if o_tr_total_exp else 0.0
            eval_bl_inc_maes.append(abs(act_o_inc - o_bl_inc))
            eval_bl_exp_maes.append(abs(act_o_exp - o_bl_exp))

            # Candidate model: 2-month moving average of strictly prior window
            o_ma_inc = sum(o_tr_incomes[-2:]) / min(2, len(o_tr_incomes)) if o_tr_incomes else o_bl_inc
            o_ma_ess = sum(o_tr_essentials[-2:]) / min(2, len(o_tr_essentials)) if o_tr_essentials else 0.0
            o_ma_disc = sum(o_tr_discretionary[-2:]) / min(2, len(o_tr_discretionary)) if o_tr_discretionary else 0.0
            o_ma_exp = o_ma_ess + o_ma_disc
            eval_inc_maes.append(abs(act_o_inc - o_ma_inc))
            eval_exp_maes.append(abs(act_o_exp - o_ma_exp))

            # Prediction interval evaluation on total expense
            o_exp_std = self._calc_std(o_tr_total_exp)
            o_exp_lower = max(0.0, o_ma_exp - t_crit_origin * o_exp_std)
            o_exp_upper = o_ma_exp + t_crit_origin * o_exp_std
            is_covered = 1.0 if (o_exp_lower <= act_o_exp <= o_exp_upper) else 0.0
            eval_coverages.append(is_covered)
            eval_widths.append(o_exp_upper - o_exp_lower)

        n_eval = len(eval_origins)
        agg_inc_mae = sum(eval_inc_maes) / n_eval
        agg_inc_rmse = math.sqrt(sum(e ** 2 for e in eval_inc_maes) / n_eval)
        agg_exp_mae = sum(eval_exp_maes) / n_eval
        agg_exp_rmse = math.sqrt(sum(e ** 2 for e in eval_exp_maes) / n_eval)
        agg_coverage = sum(eval_coverages) / n_eval
        agg_width = sum(eval_widths) / n_eval
        agg_bl_inc_mae = sum(eval_bl_inc_maes) / n_eval
        agg_bl_exp_mae = sum(eval_bl_exp_maes) / n_eval

        evaluation_metrics = ForecastEvaluationMetrics(
            evaluation_periods_evaluated=n_eval,
            income_mae=round(agg_inc_mae, 2),
            income_rmse=round(agg_inc_rmse, 2),
            expense_mae=round(agg_exp_mae, 2),
            expense_rmse=round(agg_exp_rmse, 2),
            interval_coverage=round(agg_coverage, 2),
            mean_interval_width=round(agg_width, 2),
            baseline_model="historical_average",
            baseline_income_mae=round(agg_bl_inc_mae, 2),
            baseline_expense_mae=round(agg_bl_exp_mae, 2)
        )

        # 3. Model parameterization carrying forward the evaluated winning model family (P3)
        all_incomes = [monthly_income[m] for m in sorted_months]
        all_essentials = [monthly_essential[m] for m in sorted_months]
        all_discretionary = [monthly_discretionary[m] for m in sorted_months]

        # Select forward income point forecast based on rolling-origin evaluation
        if agg_inc_mae <= agg_bl_inc_mae and len(all_incomes) >= 2:
            base_mean_income = sum(all_incomes[-2:]) / 2.0
            selected_income_model = "moving_average_2m"
        else:
            base_mean_income = sum(all_incomes) / num_months
            selected_income_model = "historical_mean"
        base_std_income = max(1.0, self._calc_std(all_incomes))

        # Select forward expense point forecast based on rolling-origin evaluation
        if agg_exp_mae <= agg_bl_exp_mae and len(all_essentials) >= 2:
            base_mean_essential = sum(all_essentials[-2:]) / 2.0
            base_mean_discretionary = sum(all_discretionary[-2:]) / 2.0
            selected_exp_model = "moving_average_2m"
        else:
            base_mean_essential = sum(all_essentials) / num_months
            base_mean_discretionary = sum(all_discretionary) / num_months
            selected_exp_model = "historical_mean"
        base_std_essential = max(1.0, self._calc_std(all_essentials))
        base_std_discretionary = max(1.0, self._calc_std(all_discretionary))

        # Carry forward deterministic recurring obligations from most recent month
        total_obligations = 0.0
        test_month = sorted_months[-1]
        for t in transactions:
            if self._get_month_key(t.event_date) == test_month and t.direction == "debit":
                if t.flexibility == "fixed" or t.event_type in ["subscription", "debt_payment"]:
                    total_obligations += t.amount

        # 4. Generate multi-period projections across horizon
        parts = test_month.split("-")
        test_yr, test_mo = int(parts[0]), int(parts[1])

        df_full = max(1, num_months - 1)
        t_crit = self._get_t_critical(conf_level, df_full)

        forecast_periods = []
        cum_mean_balance = current_balance
        cum_variance_balance = 0.0

        for h in range(1, horizon + 1):
            mo_val = test_mo + h
            yr_val = test_yr + (mo_val - 1) // 12
            mo_val = (mo_val - 1) % 12 + 1
            period_name = f"{yr_val}-{mo_val:02d}"

            # Uncertainty growth factor across multi-step horizon h (P4):
            # Statistically defensible sample-size scaling:
            # w_h = sqrt(1 + 1/N + (h - 1)/N)
            # where 1 represents single-period forecast innovation, 1/N represents parameter estimation
            # variance with sample size N, and (h - 1)/N represents multi-step drift uncertainty.
            w_h = math.sqrt(1.0 + (1.0 / num_months) + ((h - 1) / num_months))

            # Apply income shock if requested
            mean_inc_h = base_mean_income * (1.0 + (req.income_shock_percentage or 0.0))
            std_inc_h = base_std_income * w_h
            inc_lower = max(0.0, mean_inc_h - t_crit * std_inc_h)
            inc_upper = mean_inc_h + t_crit * std_inc_h

            income_dist = DistributionSummary(
                mean=round(mean_inc_h, 2),
                median=round(mean_inc_h, 2),
                lower_bound=round(inc_lower, 2),
                upper_bound=round(inc_upper, 2),
                std_dev=round(std_inc_h, 2),
                confidence_level=conf_level
            )

            # Essential expenses (with optional unexpected expense shock)
            shock_amount = req.unexpected_expense if (req.unexpected_expense and h == req.unexpected_expense_period) else 0.0
            mean_ess_h = base_mean_essential + shock_amount
            std_ess_h = base_std_essential * w_h
            ess_lower = max(0.0, mean_ess_h - t_crit * std_ess_h)
            ess_upper = mean_ess_h + t_crit * std_ess_h

            essential_dist = DistributionSummary(
                mean=round(mean_ess_h, 2),
                median=round(mean_ess_h, 2),
                lower_bound=round(ess_lower, 2),
                upper_bound=round(ess_upper, 2),
                std_dev=round(std_ess_h, 2),
                confidence_level=conf_level
            )

            # Discretionary expenses
            mean_disc_h = base_mean_discretionary
            std_disc_h = base_std_discretionary * w_h
            disc_lower = max(0.0, mean_disc_h - t_crit * std_disc_h)
            disc_upper = mean_disc_h + t_crit * std_disc_h

            discretionary_dist = DistributionSummary(
                mean=round(mean_disc_h, 2),
                median=round(mean_disc_h, 2),
                lower_bound=round(disc_lower, 2),
                upper_bound=round(disc_upper, 2),
                std_dev=round(std_disc_h, 2),
                confidence_level=conf_level
            )

            # Net Cash Flow for period h (obligations are already captured within essential expenses)
            mean_cf_h = mean_inc_h - mean_ess_h - mean_disc_h
            var_cf_h = (std_inc_h ** 2) + (std_ess_h ** 2) + (std_disc_h ** 2)
            std_cf_h = math.sqrt(var_cf_h)
            cf_lower = mean_cf_h - t_crit * std_cf_h
            cf_upper = mean_cf_h + t_crit * std_cf_h

            cash_flow_dist = DistributionSummary(
                mean=round(mean_cf_h, 2),
                median=round(mean_cf_h, 2),
                lower_bound=round(cf_lower, 2),
                upper_bound=round(cf_upper, 2),
                std_dev=round(std_cf_h, 2),
                confidence_level=conf_level
            )

            # Cumulative Balance update
            cum_mean_balance += mean_cf_h
            cum_variance_balance += var_cf_h
            cum_std_balance = math.sqrt(cum_variance_balance)
            bal_lower = cum_mean_balance - t_crit * cum_std_balance
            bal_upper = cum_mean_balance + t_crit * cum_std_balance

            cumulative_bal_dist = DistributionSummary(
                mean=round(cum_mean_balance, 2),
                median=round(cum_mean_balance, 2),
                lower_bound=round(bal_lower, 2),
                upper_bound=round(bal_upper, 2),
                std_dev=round(cum_std_balance, 2),
                confidence_level=conf_level
            )

            # Probability of falling below declared minimum reserve: P(Balance < Reserve)
            if cum_std_balance > 0:
                z_score = (declared_reserve - cum_mean_balance) / cum_std_balance
                prob_below_reserve = max(0.0, min(1.0, self._normal_cdf(z_score)))
            else:
                prob_below_reserve = 1.0 if cum_mean_balance < declared_reserve else 0.0

            forecast_periods.append(
                ProbabilisticForecastPeriod(
                    period_index=h,
                    period=period_name,
                    projected_income=income_dist,
                    essential_expenses=essential_dist,
                    discretionary_expenses=discretionary_dist,
                    known_obligations=round(total_obligations, 2),
                    projected_cash_flow=cash_flow_dist,
                    projected_cumulative_balance=cumulative_bal_dist,
                    probability_below_reserve=round(prob_below_reserve, 4)
                )
            )

        baseline_summary = {
            "historical_mean_income": round(base_mean_income, 2),
            "historical_mean_expenses": round(base_mean_essential + base_mean_discretionary, 2),
            "historical_mean_cash_flow": round(base_mean_income - base_mean_essential - base_mean_discretionary, 2),
            "held_out_period_tested": test_month,
            "evaluation_origins_tested": [sorted_months[i] for i in eval_origins],
            "selected_income_model": selected_income_model,
            "selected_expense_model": selected_exp_model,
            "observations_count": num_months
        }

        return ProbabilisticForecastResponse(
            user_id=profile.user_id,
            available=True,
            horizon_months=horizon,
            uncertainty_method=req.uncertainty_method,
            confidence_level=conf_level,
            declared_minimum_reserve=declared_reserve,
            current_available_balance=current_balance,
            periods=forecast_periods,
            evaluation_metrics=evaluation_metrics,
            baseline_comparison=baseline_summary
        )
