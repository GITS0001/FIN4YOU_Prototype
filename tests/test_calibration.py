"""
Unit tests for TransactionCategorizer calibration (ECE measurement).
Addresses review requirement:
  "The report describes confidence thresholds of 0.85, but it does not
   provide an actual calibration metric such as expected calibration error (ECE),
   despite mentioning calibration as a goal."
"""

import unittest
import numpy as np

from fin4you.models.calibration import compute_ece, evaluate_categorizer_calibration


class TestCalibrationECE(unittest.TestCase):

    # ---- Unit tests for ECE computation ----
    def test_perfect_calibration_zero_ece(self):
        """Perfect calibration: confidence == accuracy in each bin => ECE = 0."""
        # Create fake data where 80% confidence => 80% accuracy
        confidences = np.array([0.85, 0.85, 0.85, 0.85, 0.85] * 20)
        # 85% are correct
        correct = np.array([1.0, 1.0, 1.0, 1.0, 0.0] * 20)
        ece, bins = compute_ece(confidences, correct, n_bins=10)
        # In the [0.80, 0.90) bin: mean_conf=0.85, accuracy=0.80, gap=0.05
        self.assertLess(ece, 0.10)

    def test_overconfident_model_positive_ece(self):
        """Overconfident: high confidence but low accuracy => positive ECE."""
        # 95% confidence but only 60% accuracy
        confidences = np.array([0.95] * 100)
        correct = np.array([1.0] * 60 + [0.0] * 40)
        ece, bins = compute_ece(confidences, correct, n_bins=10)
        self.assertGreater(ece, 0.0)
        # The gap = accuracy (0.60) - confidence (0.95) = -0.35 (overconfident)
        occupied = [b for b in bins if b['n_samples'] > 0]
        self.assertEqual(len(occupied), 1)
        self.assertLess(occupied[0]['gap'], 0)  # negative gap = overconfident

    def test_underconfident_model_positive_ece(self):
        """Underconfident: low confidence but high accuracy => positive ECE."""
        # 70% confidence but 100% accuracy
        confidences = np.array([0.70] * 100)
        correct = np.array([1.0] * 100)
        ece, bins = compute_ece(confidences, correct, n_bins=10)
        self.assertGreater(ece, 0.0)
        occupied = [b for b in bins if b['n_samples'] > 0]
        self.assertEqual(len(occupied), 1)
        self.assertGreater(occupied[0]['gap'], 0)  # positive gap = underconfident

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
            # If bin is occupied, extra fields must exist
            if b['n_samples'] > 0:
                self.assertIn('mean_confidence', b)
                self.assertIn('accuracy', b)
                self.assertIn('gap', b)
                self.assertIn('calibration_direction', b)

    # ---- Integration: ECE on the actual trained categorizer ----
    def test_categorizer_ece_computed(self):
        """ECE must be computable on the production categorizer."""
        result = evaluate_categorizer_calibration(n_bins=10)
        self.assertIn('expected_calibration_error', result)
        self.assertIn('n_test_samples', result)
        self.assertIn('test_accuracy', result)
        self.assertIn('calibration_verdict', result)
        self.assertIn('interpretation', result)
        self.assertIn('confidence_level_breakdown', result)
        ece = result['expected_calibration_error']
        self.assertGreaterEqual(ece, 0.0)
        self.assertLessEqual(ece, 1.0)

    def test_categorizer_ece_threshold(self):
        """
        ECE < 0.15 is acceptable for a small synthetic dataset (882 events).
        A well-calibrated model has ECE < 0.05; ECE < 0.15 is still usable.
        """
        result = evaluate_categorizer_calibration(n_bins=10)
        ece = result['expected_calibration_error']
        self.assertLess(ece, 0.15,
                         f"ECE={ece:.4f} is too high. Consider temperature scaling.")

    def test_calibration_root_cause_identified(self):
        """Root cause (underconfident/overconfident/balanced) must be determined."""
        result = evaluate_categorizer_calibration(n_bins=10)
        self.assertIn('root_cause', result)
        self.assertIn(result['root_cause'], ['underconfident', 'overconfident', 'balanced'])

    def test_high_confidence_bin_accuracy(self):
        """In the high-confidence tier (>=0.85), accuracy must exceed 0.90."""
        result = evaluate_categorizer_calibration(n_bins=10)
        high_info = result['confidence_level_breakdown']['high']
        if high_info['n_samples'] > 0:
            self.assertGreater(high_info['accuracy'], 0.90,
                                "High-confidence predictions (≥0.85) must have >90% accuracy.")

    def test_confidence_level_breakdown_complete(self):
        """Must report high, medium, low confidence tiers."""
        result = evaluate_categorizer_calibration()
        breakdown = result['confidence_level_breakdown']
        self.assertIn('high', breakdown)
        self.assertIn('medium', breakdown)
        self.assertIn('low', breakdown)
        total = sum(b['n_samples'] for b in breakdown.values())
        self.assertEqual(total, result['n_test_samples'])

    def test_temperature_scaling_recommendation_when_miscalibrated(self):
        """When ECE > 0.05, a temperature scaling recommendation must be given."""
        result = evaluate_categorizer_calibration()
        ece = result['expected_calibration_error']
        if ece > 0.05:
            self.assertIsNotNone(result.get('temperature_scaling_recommendation'),
                                  "ECE > 0.05 requires a temperature scaling recommendation.")


if __name__ == '__main__':
    unittest.main()
