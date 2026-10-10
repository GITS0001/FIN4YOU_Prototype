"""
Unit tests for 90-day liquidity simulation and affordability engine.
"""

import unittest
import pandas as pd
from datetime import datetime
from fin4you.engine.affordability import AffordabilitySimulator
from fin4you.data.loader import load_profiles, load_events, load_payment_options, load_messages

class TestAffordabilitySimulator(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.simulator = AffordabilitySimulator(horizon_days=90)
        cls.profiles = load_profiles()
        cls.events = load_events()
        cls.options = load_payment_options()
        cls.messages = load_messages()

    def test_evaluate_request_26(self):
        # user_26 requested IDR 15,656,000. Balance = 100M, Min = 24.7M. Affordable now in full.
        res = self.simulator.evaluate_request(
            user_id="user_26",
            request_id="request_26",
            request_date=datetime(2025, 8, 3),
            requested_amount=15656000.0,
            profile=self.profiles,
            events=self.events,
            options=self.options,
            messages=self.messages
        )
        self.assertEqual(res["affordability_status"], "affordable_now")
        self.assertEqual(res["recommended_payment_method"], "full_payment")
        self.assertEqual(res["amount_safe_to_pay"], 15656000.0)

    def test_evaluate_request_27(self):
        # user_27 requested ZAR 6,670. Balance = 93.1K, Min = 20.5K. Affordable now in full.
        res = self.simulator.evaluate_request(
            user_id="user_27",
            request_id="request_27",
            request_date=datetime(2026, 7, 5),
            requested_amount=6670.0,
            profile=self.profiles,
            events=self.events,
            options=self.options,
            messages=self.messages
        )
        self.assertEqual(res["affordability_status"], "affordable_now")
        self.assertEqual(res["recommended_payment_method"], "full_payment")
        self.assertEqual(res["amount_safe_to_pay"], 6670.0)

    def test_evaluate_request_29_contract_ended(self):
        # user_29 seasonal contract ended per message_21. Not affordable.
        res = self.simulator.evaluate_request(
            user_id="user_29",
            request_id="request_29",
            request_date=datetime(2025, 11, 4),
            requested_amount=51524.0,
            profile=self.profiles,
            events=self.events,
            options=self.options,
            messages=self.messages
        )
        self.assertEqual(res["affordability_status"], "not_affordable")
        self.assertEqual(res["recommended_payment_method"], "not_recommended")

    def test_evaluate_request_30_installments(self):
        # user_30 prefers installments. Candidate payment_option_83 keeps minimum balance safe.
        res = self.simulator.evaluate_request(
            user_id="user_30",
            request_id="request_30",
            request_date=datetime(2026, 4, 6),
            requested_amount=775.2,
            profile=self.profiles,
            events=self.events,
            options=self.options,
            messages=self.messages
        )
        self.assertEqual(res["affordability_status"], "affordable_with_plan")
        self.assertEqual(res["recommended_payment_method"], "installments")

if __name__ == '__main__':
    unittest.main()
