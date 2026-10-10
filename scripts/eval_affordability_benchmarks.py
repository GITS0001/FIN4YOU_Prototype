import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
from datetime import datetime
from fin4you.data.loader import (
    load_profiles, load_events, load_requests,
    load_sample_requests, load_payment_options, load_messages
)
from fin4you.engine.affordability import AffordabilitySimulator

profiles = load_profiles()
events = load_events()
options = load_payment_options()
messages = load_messages()
samples = load_sample_requests()
requests = load_requests()
outputs = pd.read_csv('data/prototype/output.csv')

simulator = AffordabilitySimulator(horizon_days=90)

print("=== EVALUATING SAMPLE REQUESTS (01-05) ===")
for _, req in samples.iterrows():
    req_id = req['request_id']
    u_id = req['user_id']
    r_date = pd.to_datetime(req['request_date'])
    amt = float(req['requested_amount'])
    comp_date = pd.to_datetime(req['desired_completion_date']) if pd.notnull(req.get('desired_completion_date')) else None
    
    res = simulator.evaluate_request(
        user_id=u_id,
        request_id=req_id,
        request_date=r_date,
        requested_amount=amt,
        profile=profiles,
        events=events,
        options=options,
        messages=messages,
        desired_completion_date=comp_date
    )
    
    print(f"\n{req_id} ({u_id}):")
    print(f"  Expected Status: {req['affordability_status']} | Predicted Status: {res['affordability_status']}")
    print(f"  Expected Method: {req['recommended_payment_method']} | Predicted Method: {res['recommended_payment_method']}")
    print(f"  Safe to Pay: {res['amount_safe_to_pay']} (Expected: {req['amount_safe_to_pay']})")
    print(f"  Earliest Date: {res['earliest_date_for_full_payment']} (Expected: {req['earliest_date_for_full_payment']})")

print("\n=== EVALUATING TEST REQUESTS (26-30) vs BENCHMARK OUTPUT.CSV ===")
for _, req in requests.iterrows():
    req_id = req['request_id']
    u_id = req['user_id']
    r_date = pd.to_datetime(req['request_date'])
    amt = float(req['requested_amount'])
    comp_date = pd.to_datetime(req['desired_completion_date']) if pd.notnull(req.get('desired_completion_date')) else None
    
    res = simulator.evaluate_request(
        user_id=u_id,
        request_id=req_id,
        request_date=r_date,
        requested_amount=amt,
        profile=profiles,
        events=events,
        options=options,
        messages=messages,
        desired_completion_date=comp_date
    )
    
    bench = outputs[outputs['request_id'] == req_id].iloc[0]
    print(f"\n{req_id} ({u_id}):")
    print(f"  Benchmark Status: {bench['affordability_status']} | Predicted Status: {res['affordability_status']}")
    print(f"  Benchmark Method: {bench['recommended_payment_method']} | Predicted Method: {res['recommended_payment_method']}")
    print(f"  Safe to Pay: {res['amount_safe_to_pay']} (Benchmark: {bench['amount_safe_to_pay']})")
    print(f"  Earliest Date: {res['earliest_date_for_full_payment']} (Benchmark: {bench['earliest_date_for_full_payment']})")
