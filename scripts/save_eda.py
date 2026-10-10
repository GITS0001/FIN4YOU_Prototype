import pandas as pd
import numpy as np

events = pd.read_csv('data/prototype/financial_events.csv')
profiles = pd.read_csv('data/prototype/financial_profiles.csv')

user_metrics = []
events['event_date'] = pd.to_datetime(events['event_date'])
for u, grp in events.groupby('user_id'):
    prof = profiles[profiles['user_id'] == u].iloc[0]
    curr = prof['home_currency']
    income = grp[grp['direction'] == 'credit']['amount'].sum()
    expenses = grp[grp['direction'] == 'debit']['amount'].sum()
    txns = len(grp)
    start_d = grp['event_date'].min().date()
    end_d = grp['event_date'].max().date()
    days = (grp['event_date'].max() - grp['event_date'].min()).days + 1
    months = days / 30.4375
    monthly_income = income / months if months > 0 else 0
    monthly_expenses = expenses / months if months > 0 else 0
    savings = income - expenses
    savings_rate = (savings / income * 100) if income > 0 else 0
    
    user_metrics.append({
        'user_id': u,
        'currency': curr,
        'current_balance': prof['current_available_balance'],
        'min_balance': prof['minimum_balance_to_keep'],
        'transactions': txns,
        'start_date': str(start_d),
        'end_date': str(end_d),
        'days': days,
        'total_income': round(income, 2),
        'total_expenses': round(expenses, 2),
        'monthly_income': round(monthly_income, 2),
        'monthly_expenses': round(monthly_expenses, 2),
        'net_savings': round(savings, 2),
        'savings_rate_pct': round(savings_rate, 2)
    })

df_metrics = pd.DataFrame(user_metrics)

cat_stats = events.groupby('category').agg(
    count=('event_id', 'count'),
    total_debit=('amount', lambda s: s[events.loc[s.index, 'direction'] == 'debit'].sum()),
    mean_amount=('amount', 'mean'),
    median_amount=('amount', 'median'),
    std_amount=('amount', 'std'),
    min_amount=('amount', 'min'),
    max_amount=('amount', 'max')
).reset_index()

with open('scratch/eda_summary.txt', 'w') as f:
    f.write("=== USER METRICS ===\n")
    f.write(df_metrics.to_string())
    f.write("\n\n=== CATEGORY STATS ===\n")
    f.write(cat_stats.to_string())

print("Wrote scratch/eda_summary.txt successfully")
