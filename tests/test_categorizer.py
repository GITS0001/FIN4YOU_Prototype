"""
Unit tests for TransactionCategorizer.
"""

import unittest
import pandas as pd
from fin4you.models.categorizer import TransactionCategorizer

class TestTransactionCategorizer(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.categorizer = TransactionCategorizer.load()

    def test_load_model_artifacts(self):
        self.assertIsNotNone(self.categorizer.pipeline)
        self.assertGreater(len(self.categorizer.classes_), 10)
        self.assertIn("rent", self.categorizer.classes_)
        self.assertIn("groceries", self.categorizer.classes_)
        self.assertIn("salary", self.categorizer.classes_)

    def test_predict_single_rent(self):
        res = self.categorizer.predict_single(
            description="Apartment rent transfer",
            direction="debit",
            event_type="expense"
        )
        self.assertEqual(res["predicted_category"], "rent")
        self.assertGreaterEqual(res["ml_confidence"], 0.85)
        self.assertEqual(res["ml_status"], "confirmed")
        self.assertEqual(res["ml_confidence_level"], "high")

    def test_predict_single_salary(self):
        res = self.categorizer.predict_single(
            description="Monthly payroll credit net salary",
            direction="credit",
            event_type="income"
        )
        self.assertEqual(res["predicted_category"], "salary")
        self.assertGreaterEqual(res["ml_confidence"], 0.80)

    def test_predict_batch_schema(self):
        test_df = pd.DataFrame([
            {"description": "Grocery delivery", "direction": "debit", "event_type": "expense"},
            {"description": "Metro and bus fares", "direction": "debit", "event_type": "expense"},
            {"description": "Unknown merchant debit", "direction": "debit", "event_type": "expense"}
        ])
        preds = self.categorizer.predict_records(test_df)
        self.assertEqual(len(preds), 3)
        self.assertIn("predicted_category", preds.columns)
        self.assertIn("ml_confidence", preds.columns)
        self.assertIn("ml_status", preds.columns)
        self.assertIn("ml_confidence_level", preds.columns)

if __name__ == '__main__':
    unittest.main()
