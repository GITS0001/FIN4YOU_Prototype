import pandas as pd
import numpy as np

events = pd.read_csv('data/prototype/financial_events.csv')
events['event_date'] = pd.to_datetime(events['event_date'])

for u in ['user_01', 'user_02', 'user_26', 'user_27']:
    print(f"\n================ USER: {u} ================")
    u_ev = events[events['user_id'] == u]
    for cat in u_ev['category'].unique():
        cat_ev = u_ev[u_ev['category'] == cat].sort_values('event_date')
        if len(cat_ev) > 1:
            diffs = cat_ev['event_date'].diff().dt.days.dropna().tolist()
            days_of_month = cat_ev['event_date'].dt.day.tolist()
            amts = cat_ev['amount'].tolist()
            print(f"  {cat} ({len(cat_ev)}): DOMs={days_of_month[:6]}, Diffs={diffs[:5]}, Amounts={amts[:3]}")
