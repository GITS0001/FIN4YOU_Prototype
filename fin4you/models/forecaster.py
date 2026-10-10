"""
Next-Month Expense and Cash-Flow Forecasting Pipeline.
Implements Section 9 (Month-End Forecast) from formula_sheet.docx.
Provides baseline models, decomposed run-rate forecasts, and chronological holdout evaluation.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

class ExpenseForecaster:
    """
    Forecasting engine for next-month expenses, discretionary spend, and cash-flow trajectories.
    """
    
    def __init__(self, days_in_month: int = 30):
        self.days_in_month = days_in_month

    def forecast_user_next_month(
        self,
        df_events: pd.DataFrame,
        user_id: str,
        as_of_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Produce next-month total expense and cash-flow forecasts for a user.
        Combines deterministic recurring contractual obligations with rolling daily variable run-rate.
        """
        user_events = df_events[df_events['user_id'] == user_id].copy()
        user_events['event_date'] = pd.to_datetime(user_events['event_date'])
        
        if as_of_date is not None:
            user_events = user_events[user_events['event_date'] <= as_of_date]
            ref_date = as_of_date
        else:
            ref_date = user_events['event_date'].max()

        debit_events = user_events[user_events['direction'] == 'debit'].copy()
        credit_events = user_events[user_events['direction'] == 'credit'].copy()
        
        # 1. Fixed recurring monthly obligations
        fixed_events = debit_events[debit_events['flexibility'] == 'fixed']
        fixed_monthly = 0.0
        if not fixed_events.empty:
            for cat, grp in fixed_events.groupby('category'):
                fixed_monthly += float(grp.tail(2)['amount'].mean())
                
        # 2. Variable spending run rate (groceries, transport, dining, shopping)
        variable_events = debit_events[debit_events['flexibility'] != 'fixed']
        total_hist_days = max(30, (ref_date - debit_events['event_date'].min()).days)
        daily_variable_spend = float(variable_events['amount'].sum()) / total_hist_days if total_hist_days > 0 else 0.0
        projected_variable = daily_variable_spend * self.days_in_month
        
        # 3. Income projection
        if not credit_events.empty:
            salary_events = credit_events[credit_events['category'] == 'salary']
            if not salary_events.empty:
                monthly_income = float(salary_events.tail(2)['amount'].mean())
            else:
                monthly_income = float(credit_events['amount'].sum()) / (total_hist_days / 30.4375)
        else:
            monthly_income = 0.0
            
        # Total forecast
        projected_total_expense = fixed_monthly + projected_variable
        projected_surplus = monthly_income - projected_total_expense
        projected_savings_rate = (projected_surplus / monthly_income * 100.0) if monthly_income > 0 else 0.0
        
        # Historical monthly averages for comparison
        monthly_series = debit_events.groupby(debit_events['event_date'].dt.to_period('M'))['amount'].sum()
        hist_mean_expense = float(monthly_series.mean()) if not monthly_series.empty else projected_total_expense
        
        # Uncertainty bounds (based on historical standard deviation of completed months)
        if len(monthly_series) >= 3:
            std_err = float(monthly_series.std())
        else:
            std_err = projected_total_expense * 0.05
            
        return {
            "user_id": user_id,
            "as_of_date": ref_date.strftime('%Y-%m-%d'),
            "forecast_period_days": self.days_in_month,
            "projected_total_expenses": round(projected_total_expense, 2),
            "projected_fixed_obligations": round(fixed_monthly, 2),
            "projected_variable_spend": round(projected_variable, 2),
            "daily_variable_burn_rate": round(daily_variable_spend, 2),
            "projected_income": round(monthly_income, 2),
            "projected_net_surplus": round(projected_surplus, 2),
            "projected_savings_rate_pct": round(projected_savings_rate, 2),
            "baseline_historical_mean": round(hist_mean_expense, 2),
            "confidence_interval_95": {
                "lower_bound": round(max(0.0, projected_total_expense - 1.96 * std_err), 2),
                "upper_bound": round(projected_total_expense + 1.96 * std_err, 2)
            }
        }

    def evaluate_chronological_holdout(self, df_events: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluates forecasting models on held-out completed calendar months across all users.
        Compares:
        1. Naive (Previous Month Spend)
        2. Historical Mean (Formula Sheet MVP)
        3. 3-Month Moving Average
        4. Decomposed Schedule + Run-Rate Engine
        """
        df = df_events.dropna(subset=['amount']).copy()
        df['event_date'] = pd.to_datetime(df['event_date'])
        
        user_results = []
        for u, grp in df[df['direction'] == 'debit'].groupby('user_id'):
            m_exp = grp.groupby(grp['event_date'].dt.to_period('M'))['amount'].sum()
            # Select middle completed months (exclude first and last boundary-truncated months)
            completed_months = m_exp.iloc[1:-1]
            if len(completed_months) < 3:
                continue
                
            train_vals = completed_months.iloc[:-1].values
            actual = float(completed_months.iloc[-1])
            
            pred_naive = float(train_vals[-1])
            pred_mean = float(np.mean(train_vals))
            pred_ma3 = float(np.mean(train_vals[-3:])) if len(train_vals) >= 3 else pred_mean
            
            # Decomposed forecast using events prior to the test month
            test_month_start = completed_months.index[-1].start_time
            decomposed = self.forecast_user_next_month(df, u, as_of_date=test_month_start)
            pred_decomp = decomposed["projected_total_expenses"]
            
            user_results.append({
                "user_id": u,
                "actual": actual,
                "pred_naive": pred_naive,
                "pred_mean": pred_mean,
                "pred_ma3": pred_ma3,
                "pred_decomposed": pred_decomp,
                "err_naive": abs(actual - pred_naive),
                "err_mean": abs(actual - pred_mean),
                "err_ma3": abs(actual - pred_ma3),
                "err_decomposed": abs(actual - pred_decomp),
                "ape_naive": abs(actual - pred_naive) / actual,
                "ape_mean": abs(actual - pred_mean) / actual,
                "ape_ma3": abs(actual - pred_ma3) / actual,
                "ape_decomposed": abs(actual - pred_decomp) / actual
            })
            
        res_df = pd.DataFrame(user_results)
        
        summary = {
            "n_evaluated_users": len(res_df),
            "naive_mae": float(res_df['err_naive'].mean()),
            "naive_mape_pct": float(res_df['ape_naive'].mean() * 100.0),
            "historical_mean_mae": float(res_df['err_mean'].mean()),
            "historical_mean_mape_pct": float(res_df['ape_mean'].mean() * 100.0),
            "ma3_mae": float(res_df['err_ma3'].mean()),
            "ma3_mape_pct": float(res_df['ape_ma3'].mean() * 100.0),
            "decomposed_runrate_mae": float(res_df['err_decomposed'].mean()),
            "decomposed_runrate_mape_pct": float(res_df['ape_decomposed'].mean() * 100.0),
            "user_breakdown": user_results
        }
        return summary
