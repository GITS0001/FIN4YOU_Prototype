"""
Unit tests for deterministic financial metrics engine.
"""

import unittest
import pandas as pd
from fin4you.engine.metrics import (
    calculate_basic_financial_state,
    calculate_category_spending,
    calculate_loan_emi,
    calculate_financial_health_metrics,
    detect_transaction_anomalies
)

class TestFinancialMetrics(unittest.TestCase):
    
    def setUp(self):
        self.sample_events = pd.DataFrame([
            {"event_id": "e1", "category": "salary", "direction": "credit", "amount": 10000.0, "event_date": "2024-01-15", "flexibility": "fixed"},
            {"event_id": "e2", "category": "rent", "direction": "debit", "amount": 3000.0, "event_date": "2024-01-02", "flexibility": "fixed"},
            {"event_id": "e3", "category": "utilities", "direction": "debit", "amount": 500.0, "event_date": "2024-01-06", "flexibility": "fixed"},
            {"event_id": "e4", "category": "groceries", "direction": "debit", "amount": 1500.0, "event_date": "2024-01-10", "flexibility": "flexible"},
            {"event_id": "e5", "category": "dining", "direction": "debit", "amount": 800.0, "event_date": "2024-01-12", "flexibility": "flexible"},
            {"event_id": "e6", "category": "debt_repayment", "direction": "debit", "amount": 700.0, "event_date": "2024-01-11", "flexibility": "fixed"}
        ])

    def test_basic_financial_state(self):
        res = calculate_basic_financial_state(self.sample_events, days_elapsed=30)
        self.assertEqual(res["total_income"], 10000.0)
        self.assertEqual(res["total_expenses"], 6500.0)
        self.assertEqual(res["net_cash_flow"], 3500.0)
        self.assertAlmostEqual(res["savings_rate_pct"], 35.0, places=1)
        self.assertAlmostEqual(res["expense_ratio_pct"], 65.0, places=1)
        # Essential: rent (3000) + utilities (500) + groceries (1500) + debt (700) = 5700
        self.assertEqual(res["essential_expenses"], 5700.0)
        # Discretionary: dining (800)
        self.assertEqual(res["discretionary_expenses"], 800.0)

    def test_loan_emi_formula(self):
        # Principal = 100,000, Rate = 12% p.a. (1% monthly), Tenure = 1 year (12 months)
        # Standard EMI = 100000 * 0.01 * (1.01)^12 / ((1.01)^12 - 1) = 8,884.88
        emi_res = calculate_loan_emi(principal=100000, annual_interest_rate_pct=12.0, tenure_years=1.0)
        self.assertAlmostEqual(emi_res["monthly_emi"], 8884.88, places=1)
        self.assertAlmostEqual(emi_res["total_loan_payment"], 8884.88 * 12, places=0)
        self.assertGreater(emi_res["total_interest"], 0.0)

    def test_category_spending_breakdown(self):
        cats = calculate_category_spending(self.sample_events)
        self.assertEqual(len(cats), 5)
        total_pct = sum(c["percentage_of_total"] for c in cats)
        self.assertAlmostEqual(total_pct, 100.0, places=1)

    def test_anomaly_detection_zscore(self):
        events = pd.DataFrame([
            {"event_id": f"g_{i}", "category": "groceries", "direction": "debit", "amount": 100.0, "event_date": "2024-01-01"}
            for i in range(10)
        ] + [
            {"event_id": "spike_1", "category": "groceries", "direction": "debit", "amount": 1000.0, "event_date": "2024-01-11"}
        ])
        anomalies = detect_transaction_anomalies(events, z_threshold=2.0)
        self.assertGreaterEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["event_id"], "spike_1")
        self.assertGreater(anomalies[0]["z_score"], 2.0)

if __name__ == '__main__':
    unittest.main()
