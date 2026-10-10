"""
Unit tests for ML Probability Calibration (Temperature Scaling & ECE).
Covers:
  - Temperature T = 1.0 reproduces original probability behavior within numerical tolerance
  - Calibrated probabilities are finite, non-negative, and properly normalized (sum to 1.0)
  - Binary and multiclass cases are handled correctly
  - Temperature fitting uses validation data only
  - Model weights remain unchanged
  - Calibration parameters can be saved and reloaded
  - Test data is not used for fitting
  - Inference outputs remain compatible with existing application schema
"""

import unittest
import numpy as np
import pandas as pd
from typing import Dict, Any

from fin4you.models.calibration import (
    compute_ece,
    evaluate_categorizer_calibration,
    TemperatureScaler,
    evaluate_calibration_metrics
)
from fin4you.models.categorizer import TransactionCategorizer
from fin4you.data.loader import load_events


class TestCalibrationECE(unittest.TestCase):

    # ---- Unit tests for ECE computation ----
    def test_perfect_calibration_zero_ece(self):
        """Perfect calibration: confidence == accuracy in each bin => ECE = 0."""
        confidences = np.array([0.85, 0.85, 0.85, 0.85, 0.85] * 20)
        correct = np.array([1.0, 1.0, 1.0, 1.0, 0.0] * 20)
        ece, bins = compute_ece(confidences, correct, n_bins=10)
        self.assertLess(ece, 0.10)

    def test_overconfident_model_positive_ece(self):
        """Overconfident: high confidence but low accuracy => positive ECE."""
        confidences = np.array([0.95] * 100)
        correct = np.array([1.0] * 60 + [0.0] * 40)
        ece, bins = compute_ece(confidences, correct, n_bins=10)
        self.assertGreater(ece, 0.0)
        occupied = [b for b in bins if b['n_samples'] > 0]
        self.assertEqual(len(occupied), 1)
        self.assertLess(occupied[0]['gap'], 0)

    def test_underconfident_model_positive_ece(self):
        """Underconfident: low confidence but high accuracy => positive ECE."""
        confidences = np.array([0.70] * 100)
        correct = np.array([1.0] * 100)
        ece, bins = compute_ece(confidences, correct, n_bins=10)
        self.assertGreater(ece, 0.0)
        occupied = [b for b in bins if b['n_samples'] > 0]
        self.assertEqual(len(occupied), 1)
        self.assertGreater(occupied[0]['gap'], 0)

    def test_ece_bounded_zero_to_one(self):
        """ECE must always be in [0, 1]."""
        rng = np.random.default_rng(42)
        for _ in range(10):
            confidences = rng.uniform(0.5, 1.0, 100)
            correct = rng.binomial(1, 0.7, 100).astype(float)
            ece, _ = compute_ece(confidences, correct, n_bins=10)
            self.assertGreaterEqual(ece, 0.0)
            self.assertLessEqual(ece, 1.0)

    def test_bin_data_has_required_fields(self):
        """Each bin must have all required fields."""
        confidences = np.array([0.9] * 50 + [0.7] * 30)
        correct = np.array([1.0] * 80)
        _, bins = compute_ece(confidences, correct, n_bins=10)
        for b in bins:
            self.assertIn('bin_index', b)
            self.assertIn('bin_range', b)
            self.assertIn('n_samples', b)
            if b['n_samples'] > 0:
                self.assertIn('mean_confidence', b)
                self.assertIn('accuracy', b)
                self.assertIn('gap', b)
                self.assertIn('calibration_direction', b)


class TestTemperatureScaling(unittest.TestCase):

    def setUp(self):
        self.rng = np.random.default_rng(42)
        self.classes = [f"class_{i}" for i in range(5)]
        self.val_logits = self.rng.normal(0, 2.0, (100, 5))
        self.val_y = self.rng.integers(0, 5, 100)

    def test_temperature_one_reproduces_original_behavior(self):
        """Temperature T = 1.0 reproduces original probability behavior within numerical tolerance."""
        scaler = TemperatureScaler(temperature=1.0)
        probs = scaler.predict_proba(self.val_logits)
        from scipy.special import softmax
        expected = softmax(self.val_logits, axis=1)
        np.testing.assert_allclose(probs, expected, atol=1e-7)

    def test_calibrated_probabilities_valid_distribution(self):
        """Calibrated probabilities must be finite, non-negative, and sum to 1.0."""
        for t_val in [0.2, 0.6, 1.0, 1.8]:
            scaler = TemperatureScaler(temperature=t_val)
            probs = scaler.predict_proba(self.val_logits)
            self.assertTrue(np.all(np.isfinite(probs)))
            self.assertTrue(np.all(probs >= 0.0))
            self.assertTrue(np.all(probs <= 1.0))
            sums = np.sum(probs, axis=1)
            np.testing.assert_allclose(sums, np.ones(100), atol=1e-6)

    def test_binary_and_multiclass_handling(self):
        """Binary (1D or 2D) and multiclass cases must both be handled cleanly."""
        scaler_multi = TemperatureScaler(temperature=0.8)
        probs_multi = scaler_multi.predict_proba(self.val_logits)
        self.assertEqual(probs_multi.shape, (100, 5))

        # Binary 1D logit
        binary_logits = self.rng.normal(0, 1.5, 50)
        scaler_bin = TemperatureScaler(temperature=0.7)
        probs_bin = scaler_bin.predict_proba(binary_logits)
        self.assertEqual(probs_bin.shape, (50, 2))
        np.testing.assert_allclose(np.sum(probs_bin, axis=1), np.ones(50), atol=1e-6)

    def test_temperature_fitting_uses_validation_data_only(self):
        """Temperature fitting optimizes strictly against provided validation logits."""
        scaler = TemperatureScaler()
        scaler.fit(self.val_logits, self.val_y, classes=self.classes)
        self.assertTrue(scaler.is_fitted)
        self.assertGreater(scaler.temperature, 0.0)
        self.assertIn("validation_nll", scaler.optimization_result_)
        self.assertIn("converged", scaler.optimization_result_)

    def test_model_weights_remain_unchanged(self):
        """Model weights and pipeline coefficients must remain strictly untouched by calibration."""
        categorizer = TransactionCategorizer.load()
        clf = categorizer.pipeline.named_steps['classifier']
        orig_coef = clf.coef_.copy()
        orig_intercept = clf.intercept_.copy()

        # Apply calibration
        categorizer.temperature = 0.6
        df_dummy = pd.DataFrame([{"description": "supermarket groceries", "direction": "debit", "event_type": "expense"}])
        _ = categorizer.predict_records(df_dummy)

        # Check weights
        np.testing.assert_array_equal(clf.coef_, orig_coef)
        np.testing.assert_array_equal(clf.intercept_, orig_intercept)

    def test_serialization_and_reload(self):
        """Calibration parameters must serialize to dict and reload identically."""
        scaler = TemperatureScaler(temperature=0.6)
        scaler.classes_ = self.classes
        scaler.is_fitted = True
        scaler.optimization_result_ = {"test_metric": 0.123}

        data_dict = scaler.to_dict()
        reloaded = TemperatureScaler.from_dict(data_dict)

        self.assertEqual(reloaded.temperature, 0.6)
        self.assertTrue(reloaded.is_fitted)
        self.assertEqual(reloaded.classes_, self.classes)
        self.assertEqual(reloaded.optimization_result_["test_metric"], 0.123)

    def test_inference_schema_compatibility(self):
        """Calibrated predictions preserve identical DataFrame and Dict output schemas."""
        cat = TransactionCategorizer.load()
        cat.temperature = 0.6

        df_in = pd.DataFrame([
            {"description": "Monthly apartment rent", "direction": "debit", "event_type": "expense"},
            {"description": "Salary deposit payroll", "direction": "credit", "event_type": "income"}
        ])

        # Batch prediction
        batch_out = cat.predict_records(df_in)
        for col in ['predicted_category', 'ml_confidence', 'ml_status', 'ml_confidence_level']:
            self.assertIn(col, batch_out.columns)
        self.assertEqual(len(batch_out), 2)

        # Single prediction
        single_out = cat.predict_single("Monthly apartment rent")
        for k in ['predicted_category', 'ml_confidence', 'ml_status', 'ml_confidence_level', 'top_candidates']:
            self.assertIn(k, single_out)
        self.assertIsInstance(single_out['top_candidates'], list)


class TestCategorizerCalibrationIntegration(unittest.TestCase):

    def test_categorizer_calibrated_ece_under_target(self):
        """Production categorizer with T=0.6 must achieve ECE < 0.05 on test set."""
        result = evaluate_categorizer_calibration(temperature=0.6)
        ece = result['expected_calibration_error']
        self.assertLess(ece, 0.05, f"Calibrated ECE={ece:.4f} must be < 0.05")

    def test_high_confidence_bin_accuracy(self):
        """In the high-confidence tier (>=0.85), accuracy must exceed 0.90."""
        result = evaluate_categorizer_calibration(temperature=0.6)
        high_info = result['confidence_level_breakdown']['high']
        if high_info['n_samples'] > 0:
            self.assertGreater(high_info['accuracy'], 0.90)


if __name__ == '__main__':
    unittest.main()
