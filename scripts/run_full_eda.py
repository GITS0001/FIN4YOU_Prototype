import pandas as pd
import numpy as np
import json
import os

events = pd.read_csv('data/prototype/financial_events.csv')
profiles = pd.read_csv('data/prototype/financial_profiles.csv')
samples = pd.read_csv('data/prototype/sample_requests.csv')
requests = pd.read_csv('data/prototype/requests.csv')
outputs = pd.read_csv('data/prototype/output.csv')
rates = pd.read_csv('data/prototype/exchange_rates.csv')
messages = pd.read_csv('data/prototype/messages.csv')
images = pd.read_csv('data/prototype/images.csv')

print("=== DATA SUMMARY STATS ===")
print(f"Total events: {len(events)}")
print(f"Total users in profiles: {len(profiles)}")
print(f"Total sample requests: {len(samples)}")
print(f"Total test requests: {len(requests)}")
print(f"Total rates: {len(rates)}")
print(f"Total messages: {len(messages)}")
print(f"Total images in csv: {len(images)}")

# Missing amounts
print("Missing amounts in events:", events['amount'].isnull().sum())
print("Missing settlement dates in events:", events['settlement_date'].isnull().sum())
print("Missing flexibility:", events['flexibility'].isnull().sum())

# Date stats
events['event_date'] = pd.to_datetime(events['event_date'])
print(f"Global event date range: {events['event_date'].min().date()} to {events['event_date'].max().date()}")

# Per-user spending and income metrics
user_metrics = []
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
print("\n=== USER FINANCIAL METRICS ===")
print(df_metrics.to_string())

# Category breakdown
cat_stats = events.groupby('category').agg(
    count=('event_id', 'count'),
    total_debit=('amount', lambda s: s[events.loc[s.index, 'direction'] == 'debit'].sum()),
    mean_amount=('amount', 'mean'),
    median_amount=('amount', 'median'),
    std_amount=('amount', 'std'),
    min_amount=('amount', 'min'),
    max_amount=('amount', 'max')
).reset_index()
print("\n=== CATEGORY STATS ===")
print(cat_stats.to_string())

# Check AgamiAI dataset breakdown
import glob
agami_train = glob.glob('Indian-Bank-Statements/train/*/*.json')
print(f"\nAgamiAI total JSONs: {len(agami_train)}")
agami_tx_types = {}
agami_total_txns = 0
for f in agami_train[:20]: # sample 20 files
    with open(f, 'r', encoding='utf-8') as jf:
        d = json.load(jf)
        for tx in d.get('transactions', []):
            agami_total_txns += 1
            desc = tx.get('description', '')
            t_type = desc.split()[0].split('-')[0] if desc else 'UNKNOWN'
            agami_tx_types[t_type] = agami_tx_types.get(t_type, 0) + 1
print(f"Sample Agami transaction types (from 20 files, {agami_total_txns} txns):")
print(agami_tx_types)
