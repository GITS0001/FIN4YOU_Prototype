import math
from typing import List, Dict, Tuple
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
            if t.direction == "credit" or t.event_type == "income":
                monthly_income[month_key] += t.amount
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

        # Evaluate Income Forecast
        train_incomes = [monthly_income[m] for m in train_months]
        test_income = monthly_income[test_month]
        avg_train_income = sum(train_incomes) / len(train_incomes)
        income_mae = abs(avg_train_income - test_income)
        
        # Final forecast uses all available months
        all_incomes = [monthly_income[m] for m in sorted_months]
        final_forecast_income = sum(all_incomes) / len(all_incomes)
        income_std = self._calc_std(all_incomes)

        # Evaluate Variable Expense Forecast
        train_var_exp = [monthly_variable_expenses[m] for m in train_months]
        test_var_exp = monthly_variable_expenses[test_month]
        avg_train_var_exp = sum(train_var_exp) / len(train_var_exp) if train_var_exp else 0.0
        exp_mae = abs(avg_train_var_exp - test_var_exp)
        
        all_var_exp = [monthly_variable_expenses[m] for m in sorted_months]
        final_forecast_var_exp = sum(all_var_exp) / len(all_var_exp) if all_var_exp else 0.0
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
                target="total_income",
                period="next_month",
                predicted_value=final_forecast_income,
                model="historical_mean",
                uncertainty=income_std,
                evaluation=ForecastEvaluation(mae=income_mae, rmse=income_mae) # For 1 test point, MAE == RMSE
            ),
            ForecastResult(
                target="variable_expenses",
                period="next_month",
                predicted_value=final_forecast_var_exp,
                model="historical_mean",
                uncertainty=var_exp_std,
                evaluation=ForecastEvaluation(mae=exp_mae, rmse=exp_mae)
            )
        ]

        projected_cash_flow = ProjectedCashFlow(
            period="next_month",
            projected_income=final_forecast_income,
            projected_expenses=final_forecast_var_exp,
            known_obligations=total_obligations,
            projected_cash_flow=final_forecast_income - final_forecast_var_exp - total_obligations
        )

        projected_balance = profile.current_available_balance + projected_cash_flow.projected_cash_flow
        shortfall = profile.minimum_balance_to_keep - projected_balance
        
        gap_detection = CashFlowGap(
            detected=shortfall > 0,
            period="next_month",
            projected_balance=projected_balance,
            required_buffer=profile.minimum_balance_to_keep,
            shortfall=shortfall if shortfall > 0 else 0.0
        )

        return PredictionEngineResult(
            available=True,
            forecasts=forecasts,
            obligations=obligations,
            projected_cash_flow=projected_cash_flow,
            gap_detection=gap_detection
        )

    def _calc_std(self, values: List[float]) -> float:
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)
