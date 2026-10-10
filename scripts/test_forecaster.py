import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from fin4you.data.loader import load_events
from fin4you.models.forecaster import ExpenseForecaster

print("Loading events...")
df_events = load_events()

forecaster = ExpenseForecaster()

print("\n--- 1. Testing Next-Month Forecast for user_01 ---")
f1 = forecaster.forecast_user_next_month(df_events, "user_01")
print(f"User: {f1['user_id']}")
print(f"Projected Total Expenses: {f1['projected_total_expenses']}")
print(f"  Fixed Obligations: {f1['projected_fixed_obligations']}")
print(f"  Variable Spend: {f1['projected_variable_spend']} (daily burn: {f1['daily_variable_burn_rate']})")
print(f"Projected Income: {f1['projected_income']}")
print(f"Projected Net Surplus: {f1['projected_net_surplus']} (savings rate: {f1['projected_savings_rate_pct']}%)")
print(f"95% Confidence Interval: {f1['confidence_interval_95']}")

print("\n--- 2. Chronological Holdout Evaluation Across Users ---")
eval_res = forecaster.evaluate_chronological_holdout(df_events)
print(f"Evaluated Users Count: {eval_res['n_evaluated_users']}")
print(f"Naive Baseline MAPE: {eval_res['naive_mape_pct']:.2f}%")
print(f"Historical Mean (MVP) MAPE: {eval_res['historical_mean_mape_pct']:.2f}%")
print(f"3-Month Moving Average MAPE: {eval_res['ma3_mape_pct']:.2f}%")
print(f"Decomposed Schedule + Run-Rate MAPE: {eval_res['decomposed_runrate_mape_pct']:.2f}%")
