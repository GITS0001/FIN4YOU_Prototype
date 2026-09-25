import pandas as pd
import json
from app.ingestion.loader import DataLoader
from app.financial.state import FinancialStateEngine
from app.ml.forecasting import PredictionEngine
from app.decision.engine import DecisionEngine
from app.decision.affordability import AffordabilityEngine
from app.schemas.financial import PaymentOption

loader = DataLoader("data/prototype")
profiles = loader.load_profiles()
events = loader.load_events()

print('--- Gap Recommendation ---')
for p in profiles:
    user_events = [e for e in events if e.user_id == p.user_id]
    state = FinancialStateEngine(p.user_id).calculate_state(user_events)
    pred = PredictionEngine().run_prediction(user_events, p)
    engine = DecisionEngine(p, state, pred)
    trace = engine.generate_recommendation_for_gap()
    if trace:
        print(f'User: {p.user_id}')
        print(json.dumps(trace.dict(), indent=2))
        break

print('\n--- Affordability ---')
requests_df = pd.read_csv('data/prototype/requests.csv')
payment_opts_df = pd.read_csv('data/prototype/request_payment_options.csv')

for idx, row in requests_df.iterrows():
    p = next((pf for pf in profiles if pf.user_id == row['user_id']), None)
    if not p: continue
    user_events = [e for e in events if e.user_id == p.user_id]
    state = FinancialStateEngine(p.user_id).calculate_state(user_events)
    pred = PredictionEngine().run_prediction(user_events, p)
    
    opts = payment_opts_df[payment_opts_df['request_id'] == row['request_id']]
    po_list = []
    for _, o in opts.iterrows():
        pfq = o['payment_frequency_days']
        if pd.isna(pfq): pfq = None
        po_list.append(PaymentOption(
            payment_option_id=o['payment_option_id'],
            request_id=o['request_id'],
            payment_method=o['payment_method'],
            payment_amount=o['payment_amount'],
            number_of_payments=o['number_of_payments'],
            first_payment_date=o['first_payment_date'],
            payment_frequency_days=pfq,
            financing_fee=o['financing_fee'],
            total_payable_amount=o['total_payable_amount']
        ))
    
    aff_eng = AffordabilityEngine(p, pred)
    res = aff_eng.evaluate_purchase(row['requested_amount'], po_list)
    print(f'User {p.user_id}, Request {row["request_type"]} {row["requested_amount"]}')
    print(res.model_dump_json(indent=2))
    break
