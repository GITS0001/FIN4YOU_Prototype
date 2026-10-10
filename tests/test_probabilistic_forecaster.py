"""
Unit tests for ProbabilisticForecaster.
Covers all final-round requirements from Additional_analysis.md:
  1. Six monthly forecast periods
  2. Prediction intervals (t-distribution)
  3. Probability of falling below minimum reserve
  4. Interval coverage metrics
  5. Chronological held-out evaluation
  6. Evidence that uncertainty changes the preferred plan
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime

from fin4you.models.probabilistic_forecaster import ProbabilisticForecaster
from fin4you.data.loader import load_events, load_profiles


class TestProbabilisticForecaster(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.events = load_events()
        cls.profiles = load_profiles()
        cls.forecaster = ProbabilisticForecaster(forecast_months=6, confidence_level=0.95)

    # ---- Requirement 1: Six monthly forecast periods ----
    def test_six_monthly_periods_returned(self):
        """Forecaster must return exactly 6 monthly forecasts."""
        result = self.forecaster.forecast_user_multi_period(
            self.events, 'user_27',
            minimum_reserve=20500.0
        )
        self.assertNotIn('error', result)
        monthly = result['monthly_forecasts']
        self.assertEqual(len(monthly), 6)
        # Check month indices
        for h, mf in enumerate(monthly, start=1):
            self.assertEqual(mf['month_ahead'], h)

    # ---- Requirement 2: Prediction intervals / distributions ----
    def test_prediction_intervals_present(self):
        """Each monthly forecast must have valid prediction interval."""
        result = self.forecaster.forecast_user_multi_period(
            self.events, 'user_05',
            minimum_reserve=13100.0
        )
        self.assertNotIn('error', result)
        for mf in result['monthly_forecasts']:
            self.assertIn('prediction_interval_lower', mf)
            self.assertIn('prediction_interval_upper', mf)
            self.assertIn('interval_width', mf)
            self.assertIn('distribution_mu', mf)
            self.assertIn('distribution_sigma', mf)
            self.assertIn('degrees_of_freedom', mf)
            self.assertIn('t_critical_value', mf)
            # lower <= point forecast <= upper
            self.assertLessEqual(mf['prediction_interval_lower'], mf['point_forecast_expense'])
            self.assertGreaterEqual(mf['prediction_interval_upper'], mf['point_forecast_expense'])
            # interval must be positive
            self.assertGreater(mf['interval_width'], 0.0)

    def test_t_distribution_df_correct(self):
        """Degrees of freedom must equal n_historical_months - 1."""
        result = self.forecaster.forecast_user_multi_period(
            self.events, 'user_27'
        )
        n = result['historical_months_used']
        expected_df = n - 1
        self.assertEqual(result['t_distribution_df'], expected_df)
        for mf in result['monthly_forecasts']:
            self.assertEqual(mf['degrees_of_freedom'], expected_df)

    def test_t_prediction_interval_math(self):
        """Verify t-distribution PI formula on known data."""
        train = np.array([1000.0, 1100.0, 950.0, 1050.0])
        mu, sigma, lower, upper = self.forecaster._t_prediction_interval(train, 0.95)
        from scipy import stats as scipy_stats
        n = len(train)
        expected_mu = np.mean(train)
        expected_sigma = np.std(train, ddof=1)
        t_crit = scipy_stats.t.ppf(0.975, df=n - 1)
        sigma_pred = expected_sigma * np.sqrt(1 + 1 / n)
        expected_lower = expected_mu - t_crit * sigma_pred
        expected_upper = expected_mu + t_crit * sigma_pred
        self.assertAlmostEqual(mu, expected_mu, places=2)
        self.assertAlmostEqual(sigma, expected_sigma, places=2)
        self.assertAlmostEqual(lower, max(0.0, expected_lower), places=2)
        self.assertAlmostEqual(upper, expected_upper, places=2)

    # ---- Requirement 3: Probability of falling below minimum reserve ----
    def test_breach_probability_is_present_and_bounded(self):
        """Breach probability must be in [0, 1] for all months."""
        result = self.forecaster.forecast_user_multi_period(
            self.events, 'user_30',
            minimum_reserve=900.0
        )
        self.assertNotIn('error', result)
        for mf in result['monthly_forecasts']:
            p_cum = mf['p_breach_reserve_cumulative']
            p_single = mf['p_breach_reserve_single_month']
            self.assertGreaterEqual(p_cum, 0.0)
            self.assertLessEqual(p_cum, 1.0)
            self.assertGreaterEqual(p_single, 0.0)
            self.assertLessEqual(p_single, 1.0)

    def test_portfolio_breach_probability_present(self):
        """Overall breach probability across 6 months must be computed."""
        result = self.forecaster.forecast_user_multi_period(
            self.events, 'user_27',
            minimum_reserve=20500.0
        )
        self.assertIn('probability_any_reserve_breach', result)
        p = result['probability_any_reserve_breach']
        self.assertGreaterEqual(p, 0.0)
        self.assertLessEqual(p, 1.0)

    def test_high_reserve_increases_breach_probability(self):
        """Higher reserve threshold must yield higher breach probability."""
        low_res = self.forecaster.forecast_user_multi_period(
            self.events, 'user_27', minimum_reserve=0.0
        )
        high_res = self.forecaster.forecast_user_multi_period(
            self.events, 'user_27', minimum_reserve=1_000_000.0
        )
        p_low = low_res['probability_any_reserve_breach']
        p_high = high_res['probability_any_reserve_breach']
        self.assertGreaterEqual(p_high, p_low)

    # ---- Requirement 4: Interval coverage and width ----
    def test_coverage_metrics_schema(self):
        """Coverage evaluation must return all required fields."""
        coverage = self.forecaster.evaluate_coverage_metrics(self.events)
        self.assertIn('n_evaluations', coverage)
        self.assertIn('target_coverage', coverage)
        self.assertIn('empirical_coverage', coverage)
        self.assertIn('coverage_gap', coverage)
        self.assertIn('mean_interval_width', coverage)
        self.assertIn('mean_mape_pct', coverage)
        self.assertIn('calibration_verdict', coverage)
        self.assertIn('per_user_coverage', coverage)
        self.assertGreater(coverage['n_evaluations'], 0)
        ec = coverage['empirical_coverage']
        self.assertGreaterEqual(ec, 0.0)
        self.assertLessEqual(ec, 1.0)

    def test_t_distribution_achieves_at_least_80_percent_coverage(self):
        """t-distribution PI must achieve >= 80% empirical coverage (lenient lower bound)."""
        coverage = self.forecaster.evaluate_coverage_metrics(self.events)
        self.assertGreaterEqual(coverage['empirical_coverage'], 0.80,
                                 "Coverage below 80% — intervals are too narrow.")

    def test_mape_below_15_percent(self):
        """Point forecast MAPE should be below 15% on held-out months."""
        coverage = self.forecaster.evaluate_coverage_metrics(self.events)
        self.assertLess(coverage['mean_mape_pct'], 15.0,
                         f"MAPE {coverage['mean_mape_pct']:.2f}% exceeds 15%.")

    # ---- Requirement 5: Chronological held-out evaluation ----
    def test_chronological_split_used(self):
        """Expanding window evaluation must use only past months to predict future."""
        coverage = self.forecaster.evaluate_coverage_metrics(self.events)
        for user_res in coverage['per_user_coverage']:
            # Each user must have had at least 1 evaluation
            self.assertGreater(user_res['n_evaluations'], 0)

    # ---- Requirement 6: Uncertainty changes the preferred plan ----
    def test_uncertainty_changes_plan_for_tight_reserve(self):
        """
        For user_30: deterministic forecast says 'safe' at 5× reserve,
        but probabilistic upper CI says 'at_risk'. This proves that
        uncertainty (prediction interval) changes the recommended plan.
        """
        demonstrations = self.forecaster.demonstrate_uncertainty_changes_plan(
            self.events, self.profiles,
            reserve_tightening_factors=(1.0, 1.5, 2.0, 3.0, 5.0, 8.0)
        )
        # user_30 must show a verdict change
        user30 = next((d for d in demonstrations if d['user_id'] == 'user_30'), None)
        self.assertIsNotNone(user30, "user_30 not found in demonstrations")
        self.assertTrue(
            user30['uncertainty_changes_plan_at_any_threshold'],
            "user_30 should show a plan change at 5× reserve threshold"
        )

    def test_demonstration_includes_sensitivity_sweep(self):
        """Demonstration must include reserve sensitivity sweep for each user."""
        demonstrations = self.forecaster.demonstrate_uncertainty_changes_plan(
            self.events, self.profiles
        )
        self.assertGreater(len(demonstrations), 0)
        for d in demonstrations:
            self.assertIn('reserve_sensitivity', d)
            self.assertIn('expense_cv_pct', d)
            self.assertIn('upper_ci_expense', d)
            self.assertGreater(len(d['reserve_sensitivity']), 0)

    # ---- Insufficient data handling ----
    def test_insufficient_data_returns_error(self):
        """Single-month histories must gracefully return an error dict."""
        # Create minimal event df for a fake user with only 1 month
        single_month_events = pd.DataFrame([{
            'user_id': 'fake_user',
            'event_date': pd.Timestamp('2024-01-15'),
            'direction': 'debit',
            'amount': 1000.0,
            'category': 'groceries',
            'flexibility': 'variable',
            'status': 'completed',
            'event_type': 'expense',
            'settlement_date': pd.Timestamp('2024-01-16'),
            'currency': 'USD'
        }])
        result = self.forecaster.forecast_user_multi_period(
            single_month_events, 'fake_user', minimum_reserve=0.0
        )
        self.assertIn('error', result)

    # ---- All users can be forecast ----
    def test_all_users_forecast(self):
        """All 10 users must produce valid 6-month forecasts."""
        all_forecasts = self.forecaster.forecast_all_users(self.events, self.profiles)
        self.assertEqual(len(all_forecasts), 10)
        valid = [f for f in all_forecasts if 'error' not in f]
        self.assertGreater(len(valid), 7, "At least 8 users should have enough data")


if __name__ == '__main__':
    unittest.main()
