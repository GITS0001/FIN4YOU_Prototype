"""Inspect data time spans per user for forecasting feasibility."""
import pandas as pd

df = pd.read_csv('data/prototype/financial_events.csv')
df['event_date'] = pd.to_datetime(df['event_date'])

print(f"Date range: {df['event_date'].min()} to {df['event_date'].max()}")
print(f"Users: {df['user_id'].nunique()}")
print(f"Categories: {df['category'].nunique()}")
print(f"\nPer user months:")
for u, g in df.groupby('user_id'):
    d = g['event_date']
    n_months = len(g.groupby(d.dt.to_period('M')))
    debit_months = g[g['direction'] == 'debit'].groupby(d[g['direction'] == 'debit'].dt.to_period('M'))['amount'].sum()
    print(f"  {u}: {d.min().date()} to {d.max().date()}, {len(g)} events, {n_months} months, {len(debit_months)} debit months")
    print(f"    Monthly debit sums: {[round(v, 0) for v in debit_months.values]}")
