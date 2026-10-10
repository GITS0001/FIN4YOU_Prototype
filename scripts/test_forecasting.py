import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

df = pd.read_csv('data/prototype/financial_events.csv')
df = df.dropna(subset=['amount']).copy()
df['event_date'] = pd.to_datetime(df['event_date'])
df['year_month'] = df['event_date'].dt.to_period('M')

# Calculate monthly expenses per user
monthly_exp = df[df['direction'] == 'debit'].groupby(['user_id', 'year_month'])['amount'].sum().reset_index()
monthly_exp = monthly_exp.sort_values(['user_id', 'year_month'])

print("Sample monthly expenses:")
print(monthly_exp.head(15))

# Chronological evaluation: predict the last month for each user using previous months
users = monthly_exp['user_id'].unique()
naive_maes = []
mean_maes = []
trend_maes = []

results = []
for u in users:
    u_data = monthly_exp[monthly_exp['user_id'] == u].copy()
    if len(u_data) < 3:
        continue
    # Held-out last month
    train_vals = u_data.iloc[:-1]['amount'].values
    actual = u_data.iloc[-1]['amount']
    
    # Baseline 1: Naive (last month's expense)
    pred_naive = train_vals[-1]
    
    # Baseline 2: Historical Mean (formula sheet MVP)
    pred_mean = np.mean(train_vals)
    
    # Model 3: 3-month Moving Average
    pred_ma3 = np.mean(train_vals[-3:]) if len(train_vals) >= 3 else np.mean(train_vals)
    
    results.append({
        'user_id': u,
        'actual': actual,
        'pred_naive': pred_naive,
        'err_naive': abs(actual - pred_naive),
        'pred_mean': pred_mean,
        'err_mean': abs(actual - pred_mean),
        'pred_ma3': pred_ma3,
        'err_ma3': abs(actual - pred_ma3),
    })

res_df = pd.DataFrame(results)
print("\n=== EXPENSE FORECASTING BENCHMARK (HELD-OUT FINAL MONTH) ===")
print(res_df.to_string())

print("\nAggregate Normalized Metrics (MAPE):")
print(f"Naive MAPE: {np.mean(res_df['err_naive'] / res_df['actual']) * 100:.2f}%")
print(f"Historical Mean MAPE: {np.mean(res_df['err_mean'] / res_df['actual']) * 100:.2f}%")
print(f"3-Month MA MAPE: {np.mean(res_df['err_ma3'] / res_df['actual']) * 100:.2f}%")
