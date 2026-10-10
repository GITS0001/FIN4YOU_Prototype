import pandas as pd
import numpy as np
import json
import glob
import os

print("=== 1. AUDITING FINANCIAL EVENTS ===")
df_events = pd.read_csv('data/prototype/financial_events.csv')
print(f"Shape: {df_events.shape}")
print("Columns & Types:")
print(df_events.dtypes)
print("\nMissing values:")
print(df_events.isnull().sum())
print("\nUnique Users:", df_events['user_id'].unique())
print("Event Types:", df_events['event_type'].value_counts().to_dict())
print("Directions:", df_events['direction'].value_counts().to_dict())
print("Categories:", df_events['category'].value_counts().to_dict())
print("Flexibility:", df_events['flexibility'].value_counts().to_dict())
print("Currencies per user:")
print(df_events.groupby('user_id')['currency'].unique().to_dict())
df_events['event_date'] = pd.to_datetime(df_events['event_date'])
print("Date ranges per user:")
for u, grp in df_events.groupby('user_id'):
    print(f"  {u}: {grp['event_date'].min().date()} to {grp['event_date'].max().date()} ({len(grp)} txns, {grp['event_date'].dt.to_period('M').nunique()} months)")

print("\n=== 2. AUDITING FINANCIAL PROFILES ===")
df_profiles = pd.read_csv('data/prototype/financial_profiles.csv')
print(f"Shape: {df_profiles.shape}")
print(df_profiles.to_string())

print("\n=== 3. AUDITING REQUESTS & SAMPLES ===")
df_samples = pd.read_csv('data/prototype/sample_requests.csv')
print(f"Sample Requests Shape: {df_samples.shape}")
print(df_samples[['request_id', 'user_id', 'request_type', 'requested_amount', 'affordability_status', 'recommended_payment_method']])

df_reqs = pd.read_csv('data/prototype/requests.csv')
print(f"\nTest Requests Shape: {df_reqs.shape}")
print(df_reqs)

df_out = pd.read_csv('data/prototype/output.csv')
print(f"\nGround Truth Output Shape: {df_out.shape}")
print(df_out[['request_id', 'amount_safe_to_pay', 'affordability_status', 'recommended_payment_method', 'earliest_date_for_full_payment']])

print("\n=== 4. AUDITING PAYMENT OPTIONS ===")
df_opts = pd.read_csv('data/prototype/request_payment_options.csv')
print(f"Payment Options Shape: {df_opts.shape}")
print(df_opts.groupby('request_id')['payment_method'].value_counts())

print("\n=== 5. AUDITING AGAMIAI DATASET ===")
agami_files = glob.glob('Indian-Bank-Statements/train/*/*.json')
print(f"Total AgamiAI JSON files: {len(agami_files)}")
if agami_files:
    with open(agami_files[0], 'r', encoding='utf-8') as f:
        sample_json = json.load(f)
    print("Agami keys:", list(sample_json.keys()))
    txns = sample_json.get('transactions', [])
    print(f"Sample statement transaction count: {len(txns)}")
    if txns:
        print("Sample txn keys:", list(txns[0].keys()))
        print("Sample txn:", txns[0])

print("\n=== 6. AUDITING MESSAGES & IMAGES ===")
df_msg = pd.read_csv('data/prototype/messages.csv')
print("Messages:")
print(df_msg[['message_id', 'user_id', 'request_id', 'source_type', 'message_text']])
