import pandas as pd
import numpy as np
from datetime import datetime, timedelta

events = pd.read_csv('data/prototype/financial_events.csv')
profiles = pd.read_csv('data/prototype/financial_profiles.csv')
samples = pd.read_csv('data/prototype/sample_requests.csv')
options = pd.read_csv('data/prototype/request_payment_options.csv')
outputs = pd.read_csv('data/prototype/output.csv')
messages = pd.read_csv('data/prototype/messages.csv')

events['event_date'] = pd.to_datetime(events['event_date'])
events['settlement_date'] = pd.to_datetime(events['settlement_date'])

print("=== CHECKING USER_01 CASH FLOW SIMULATION ===")
# user_01 request_01: date=2024-03-03, amount=25256, profile balance=58481.1, min_bal=18000
u1_events = events[events['user_id'] == 'user_01'].sort_values('event_date')
print("User 01 events around March 2024:")
print(u1_events[u1_events['event_date'] >= '2024-02-15'][['event_id', 'event_type', 'category', 'description', 'direction', 'amount', 'event_date', 'settlement_date', 'status']])

print("\n=== CHECKING USER_02 CASH FLOW SIMULATION ===")
# user_02 request_02: date=2025-08-05, amount=46018000, profile balance=60383889.2, min_bal=29158400
u2_events = events[events['user_id'] == 'user_02'].sort_values('event_date')
print("User 02 events around August 2025:")
print(u2_events[u2_events['event_date'] >= '2025-07-15'][['event_id', 'event_type', 'category', 'description', 'direction', 'amount', 'event_date', 'settlement_date', 'status']])
