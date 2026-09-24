import os
import json
import time
import pandas as pd
from typing import Dict, Any

from app.ingestion.loader import DataLoader
from app.financial.state import FinancialStateEngine
from app.ml.forecasting import PredictionEngine
from app.decision.engine import DecisionEngine
from app.decision.affordability import AffordabilityEngine
from app.decision.simulation import WhatIfSimulator
from app.decision.impact import ImpactEngine
from app.copilot.orchestrator import CopilotOrchestrator
from app.schemas.copilot import CopilotRequest, IntentType
from fastapi.testclient import TestClient
from app.main import app

def run_audit():
    report = {}
    
    # 2. INVENTORY
    report['inventory'] = {
        'modules': [d for d in os.listdir("backend/app") if os.path.isdir(os.path.join("backend/app", d))],
        'schemas': os.listdir("backend/app/schemas") if os.path.exists("backend/app/schemas") else []
    }
    
    # 3. DATA INTEGRITY
    loader = DataLoader("data/prototype")
    profiles = loader.load_profiles()
    events = loader.load_events()
    try:
        po_df = pd.read_csv("data/prototype/request_payment_options.csv")
    except:
        po_df = pd.DataFrame()
        
    try:
        req_df = pd.read_csv("data/prototype/requests.csv")
    except:
        req_df = pd.DataFrame()

    report['data_integrity'] = {
        'events_count': len(events),
        'unique_users': len(set([e.user_id for e in events])),
        'profiles_count': len(profiles),
        'requests_count': len(req_df),
        'payment_options_count': len(po_df)
    }

    # 4-11. USER LEVEL VALIDATION (Financial, Temporal, Refund, Leakage, Decision)
    user_reports = {}
    for profile in profiles:
        uid = profile.user_id
        u_events = [e for e in events if e.user_id == uid]
        
        # Financial State
        fse = FinancialStateEngine(uid)
        state = fse.calculate_state(u_events)
        
        # Check refund handling
        refunds = [e for e in u_events if e.amount < 0 and e.category != "Income"] # simplified check
        
        # Prediction
        pe = PredictionEngine()
        pred = pe.run_prediction(u_events, profile)
        
        # Decision / Affordability
        if pred.available:
            ae = AffordabilityEngine(profile, pred)
            aff_res = ae.evaluate_purchase(1500)
            
            sim = WhatIfSimulator(profile, pred)
            base = sim.baseline_scenario()
            scen = sim.simulate_reduce_discretionary_spending(100)
            imp = ImpactEngine.calculate_impact(base, scen)
        else:
            aff_res = None
            imp = None
            
        user_reports[uid] = {
            'events_count': len(u_events),
            'has_refunds': len(refunds) > 0,
            'state_cash_flow': state.cash_flow,
            'prediction_available': pred.available,
            'affordability_1500': aff_res.status if aff_res else None,
            'whatif_buffer_change': imp.buffer_status_change if imp else None
        }
        
    report['user_validation'] = user_reports
    
    # 13-16. COPILOT API TESTS
    client = TestClient(app)
    api_tests = []
    
    # Simple query
    t1 = time.time()
    r1 = client.post("/api/copilot/query", json={"user_id": "user_28", "message": "Can I afford to spend 1302.4 in installments?"})
    t2 = time.time()
    
    api_tests.append({
        'query': "Can I afford to spend 1302.4 in installments?",
        'user': "user_28",
        'status': r1.status_code,
        'intent': r1.json().get('intent') if r1.status_code==200 else None,
        'latency': t2 - t1
    })

    # Cross user isolation
    r2 = client.post("/api/copilot/query", json={"user_id": "user_1", "message": "Can I afford to spend 1302.4 in installments?"})
    r2_data = r2.json() if r2.status_code == 200 else {}
    structured_res = r2_data.get('structured_result') or {}
    api_tests.append({
        'query': "Cross user same query",
        'user': "user_1",
        'status': r2.status_code,
        'intent': r2_data.get('intent'),
        'affordability': structured_res.get('affordability_status')
    })
    
    report['api_tests'] = api_tests
    
    with open("audit_results.json", "w") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    run_audit()
