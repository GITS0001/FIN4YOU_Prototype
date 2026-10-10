import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_data():
    events = pd.read_csv('data/prototype/financial_events.csv')
    profiles = pd.read_csv('data/prototype/financial_profiles.csv')
    samples = pd.read_csv('data/prototype/sample_requests.csv')
    options = pd.read_csv('data/prototype/request_payment_options.csv')
    outputs = pd.read_csv('data/prototype/output.csv')
    rates = pd.read_csv('data/prototype/exchange_rates.csv')
    
    events['event_date'] = pd.to_datetime(events['event_date'])
    events['settlement_date'] = pd.to_datetime(events['settlement_date'])
    return events, profiles, samples, options, outputs, rates

events, profiles, samples, options, outputs, rates = load_data()

print("User 01 request:")
r1 = samples[samples['request_id'] == 'request_01'].iloc[0]
p1 = profiles[profiles['user_id'] == 'user_01'].iloc[0]
opts1 = options[options['request_id'] == 'request_01']

print("Req 01:", r1['request_date'], r1['requested_amount'], r1['affordability_status'], r1['recommended_payment_method'])
print("Prof 01:", p1['current_available_balance'], p1['minimum_balance_to_keep'])
print("Options 01:\n", opts1[['payment_option_id', 'payment_method', 'payment_amount', 'number_of_payments', 'first_payment_date']])

# Let's inspect user_01 recurring obligations:
u1_ev = events[events['user_id'] == 'user_01']
print("\nUser 01 salary events:")
print(u1_ev[u1_ev['category'] == 'salary'][['event_id', 'amount', 'event_date', 'status']])
print("\nUser 01 fixed obligations in a typical month:")
u1_fixed = u1_ev[u1_ev['flexibility'] == 'fixed'].groupby('category')['amount'].mean()
print(u1_fixed)
