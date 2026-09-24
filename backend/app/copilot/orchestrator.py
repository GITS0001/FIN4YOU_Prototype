from typing import Optional, List, Dict
from app.schemas.copilot import CopilotRequest, CopilotResponse, ParsedIntent, IntentType
from app.copilot.intent_parser import IntentParser
from app.copilot.response_generator import ResponseGenerator
from app.ingestion.loader import DataLoader
from app.financial.state import FinancialStateEngine
from app.ml.forecasting import PredictionEngine
from app.decision.engine import DecisionEngine
from app.decision.affordability import AffordabilityEngine
from app.decision.simulation import WhatIfSimulator
from app.decision.impact import ImpactEngine
from app.schemas.financial import PaymentOption

import pandas as pd

class CopilotOrchestrator:
    def __init__(self, data_dir: str = "data/prototype"):
        self.parser = IntentParser()
        self.generator = ResponseGenerator()
        self.loader = DataLoader(data_dir)
        self.profiles = self.loader.load_profiles()
        self.events = self.loader.load_events()
        
        # Load payment options globally for the prototype to avoid passing around df
        try:
            self.payment_opts_df = pd.read_csv(f"{data_dir}/request_payment_options.csv")
        except FileNotFoundError:
            self.payment_opts_df = pd.DataFrame()

    def process_query(self, request: CopilotRequest) -> CopilotResponse:
        # Find user
        profile = next((p for p in self.profiles if p.user_id == request.user_id), None)
        if not profile:
            return CopilotResponse(
                intent=IntentType.UNKNOWN,
                response="User context not found.",
                confidence="UNKNOWN",
                status="ERROR"
            )

        # Parse Intent
        parsed = self.parser.parse(request.message)
        
        if parsed.intent == IntentType.UNKNOWN:
            resp_text = self.generator.generate(parsed, {})
            return CopilotResponse(
                intent=parsed.intent,
                response=resp_text,
                confidence="UNKNOWN",
                status="UNSUPPORTED"
            )

        # Retrieve Financial Context
        user_events = [e for e in self.events if e.user_id == profile.user_id]
        state = FinancialStateEngine(profile.user_id).calculate_state(user_events)
        pred = PredictionEngine().run_prediction(user_events, profile)

        if not pred.available and parsed.intent not in [IntentType.FINANCIAL_SUMMARY, IntentType.SPENDING_ANALYSIS]:
            resp_text = self.generator.generate(parsed, {"status": "INSUFFICIENT_DATA"})
            return CopilotResponse(
                intent=parsed.intent,
                response=resp_text,
                confidence="UNKNOWN",
                status="INSUFFICIENT_DATA",
                data_sources=["financial_profiles", "financial_events"]
            )

        structured_res = {}
        trace = None
        status = "SUCCESS"

        if parsed.intent == IntentType.AFFORDABILITY_CHECK:
            if not parsed.amount or parsed.amount <= 0:
                return CopilotResponse(intent=parsed.intent, response="Please specify a valid amount.", confidence="UNKNOWN", status="ERROR")
            aff_eng = AffordabilityEngine(profile, pred)
            res = aff_eng.evaluate_purchase(parsed.amount)
            structured_res = {
                "affordability_status": res.status,
                "resulting_balance": res.resulting_balance,
                "trade_off": res.trade_off_required
            }

        elif parsed.intent == IntentType.PAYMENT_OPTION_ANALYSIS:
            if not parsed.amount or parsed.amount <= 0:
                return CopilotResponse(intent=parsed.intent, response="Please specify a valid amount.", confidence="UNKNOWN", status="ERROR")
            
            # Simple heuristic: find requests in DB that match the user and rough amount
            try:
                requests_df = pd.read_csv("data/prototype/requests.csv")
                req_id = None
                for _, r in requests_df.iterrows():
                    if r["user_id"] == profile.user_id and abs(r["requested_amount"] - parsed.amount) < 1.0:
                        req_id = r["request_id"]
                        break
                po_list = []
                if req_id and not self.payment_opts_df.empty:
                    opts = self.payment_opts_df[self.payment_opts_df["request_id"] == req_id]
                    for _, o in opts.iterrows():
                        pfq = o["payment_frequency_days"]
                        if pd.isna(pfq): pfq = None
                        po_list.append(PaymentOption(
                            payment_option_id=o["payment_option_id"],
                            request_id=o["request_id"],
                            payment_method=o["payment_method"],
                            payment_amount=o["payment_amount"],
                            number_of_payments=o["number_of_payments"],
                            first_payment_date=o["first_payment_date"],
                            payment_frequency_days=pfq,
                            financing_fee=o["financing_fee"],
                            total_payable_amount=o["total_payable_amount"]
                        ))
            except Exception:
                po_list = []

            aff_eng = AffordabilityEngine(profile, pred)
            res = aff_eng.evaluate_purchase(parsed.amount, po_list)
            structured_res = {
                "affordability_status": res.status,
                "viable_options": [o.model_dump() for o in res.viable_payment_options]
            }

        elif parsed.intent == IntentType.WHAT_IF:
            sim = WhatIfSimulator(profile, pred)
            baseline = sim.baseline_scenario()
            if parsed.change_amount and parsed.change_amount < 0:
                scenario = sim.simulate_reduce_discretionary_spending(abs(parsed.change_amount))
                impact = ImpactEngine.calculate_impact(baseline, scenario)
                structured_res = {
                    "projected_balance": scenario.projected_balance,
                    "buffer_status_change": impact.buffer_status_change
                }

        elif parsed.intent == IntentType.RECOMMENDATION:
            dec_eng = DecisionEngine(profile, state, pred)
            trace = dec_eng.generate_recommendation_for_gap()
            if trace:
                structured_res = {"recommendation_text": trace.recommendation.actionable_text}
            else:
                structured_res = {"recommendation_text": None}

        elif parsed.intent == IntentType.CASH_FLOW_FORECAST:
            sim = WhatIfSimulator(profile, pred)
            baseline = sim.baseline_scenario()
            structured_res = {
                "projected_cash_flow": pred.projected_cash_flow.projected_cash_flow,
                "projected_balance": baseline.projected_balance
            }

        elif parsed.intent == IntentType.FINANCIAL_SUMMARY:
            structured_res = {
                "balance": profile.current_available_balance,
                "cash_flow": state.cash_flow
            }

        elif parsed.intent == IntentType.SPENDING_ANALYSIS:
            structured_res = {
                "largest_categories": []
            }

        resp_text = self.generator.generate(parsed, structured_res)

        return CopilotResponse(
            intent=parsed.intent,
            response=resp_text,
            decision_trace=trace,
            structured_result=structured_res,
            confidence="HIGH" if pred.available else "MEDIUM",
            status=status,
            data_sources=["financial_profiles", "financial_events", "PredictionEngine", "DecisionEngine"]
        )
