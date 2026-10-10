import pandas as pd
import numpy as np

profiles = pd.read_csv('data/prototype/financial_profiles.csv')
events = pd.read_csv('data/prototype/financial_events.csv')
samples = pd.read_csv('data/prototype/sample_requests.csv')
options = pd.read_csv('data/prototype/request_payment_options.csv')
outputs = pd.read_csv('data/prototype/output.csv')

print("=== SAMPLES DATA ===")
for idx, row in samples.iterrows():
    print(f"\nRequest: {row['request_id']}, User: {row['user_id']}, Date: {row['request_date']}, Req Amount: {row['requested_amount']}")
    print(f"  Affordability: {row['affordability_status']}, Method: {row['recommended_payment_method']}")
    print(f"  Safe amount: {row['amount_safe_to_pay']}, Earliest date: {row['earliest_date_for_full_payment']}")
    print(f"  Explanation: {row['decision_explanation']}")
    
    # User profile
    u_prof = profiles[profiles['user_id'] == row['user_id']].iloc[0]
    print(f"  Profile Balance: {u_prof['current_available_balance']}, Min Balance: {u_prof['minimum_balance_to_keep']}")
    
    # Available payment options
    req_opts = options[options['request_id'] == row['request_id']]
    print(f"  Options: {req_opts[['payment_option_id', 'payment_method', 'payment_amount', 'number_of_payments', 'first_payment_date', 'total_payable_amount']].to_dict(orient='records')}")

print("\n=== BENCHMARK OUTPUTS (TEST REQUESTS) ===")
for idx, row in outputs.iterrows():
    print(f"\nRequest: {row['request_id']}, Status: {row['affordability_status']}, Method: {row['recommended_payment_method']}")
    print(f"  Safe amount: {row['amount_safe_to_pay']}, Earliest date: {row['earliest_date_for_full_payment']}")
    print(f"  Explanation: {row['decision_explanation']}")
