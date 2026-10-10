"""
Run all review-required evaluations:
  1. Categorizer ECE calibration
  2. Probabilistic 6-month forecasting with coverage metrics
  3. Uncertainty impact demonstration (sensitivity sweep)
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fin4you.models.calibration import evaluate_categorizer_calibration
from fin4you.models.probabilistic_forecaster import ProbabilisticForecaster
from fin4you.data.loader import load_events, load_profiles


def main():
    print("=" * 70)
    print("REVIEW VERIFICATION: Full Evaluation Suite")
    print("=" * 70)

    # ---- 1. CATEGORIZER CALIBRATION ----
    print("\n[1/3] Measuring Expected Calibration Error (ECE)...")
    try:
        cal = evaluate_categorizer_calibration(n_bins=10)
        print(f"  Test samples: {cal['n_test_samples']}")
        print(f"  Test accuracy: {cal['test_accuracy']:.4f}")
        print(f"  ECE: {cal['expected_calibration_error']:.6f}")
        print(f"  Root cause: {cal['root_cause']}")
        print(f"  Verdict: {cal['calibration_verdict']}")
        print(f"  Interpretation: {cal['interpretation']}")
        if cal.get('temperature_scaling_recommendation'):
            tr = cal['temperature_scaling_recommendation']
            print(f"  Temperature scaling: {tr['action']} (T in {tr['suggested_T_range']})")
        print("\n  Confidence Level Breakdown:")
        for level, data in cal['confidence_level_breakdown'].items():
            print(f"    {level}: n={data['n_samples']}, "
                  f"acc={data['accuracy']:.4f}, "
                  f"conf={data['mean_confidence']:.4f}, "
                  f"direction={data['calibration_direction']}")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        cal = {"error": str(e)}

    # ---- 2. PROBABILISTIC FORECASTING ----
    print("\n[2/3] Running 6-month probabilistic forecaster...")
    events = load_events()
    profiles = load_profiles()
    forecaster = ProbabilisticForecaster(forecast_months=6, confidence_level=0.95)

    # Coverage metrics on held-out months
    print("  Evaluating t-distribution interval coverage...")
    try:
        coverage = forecaster.evaluate_coverage_metrics(events)
        print(f"  Evaluations: {coverage['n_evaluations']}")
        print(f"  Target coverage: {coverage['target_coverage']:.2%}")
        print(f"  Empirical coverage: {coverage['empirical_coverage']:.2%}")
        print(f"  Coverage gap: {coverage['coverage_gap']:+.4f}")
        print(f"  Mean interval width: {coverage['mean_interval_width']:,.2f}")
        print(f"  Mean MAPE: {coverage['mean_mape_pct']:.2f}%")
        print(f"  Verdict: {coverage['calibration_verdict']}")
        print(f"  Note: {coverage.get('note', '')}")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        coverage = {"error": str(e)}

    # Sample 6-month forecast for user_27 (has full income)
    print("\n  Sample 6-month probabilistic forecast for user_27:")
    try:
        prof27 = profiles[profiles['user_id'] == 'user_27'].iloc[0]
        f27 = forecaster.forecast_user_multi_period(
            events, 'user_27',
            minimum_reserve=float(prof27['minimum_balance_to_keep']),
        )
        print(f"    Historical months used: {f27['historical_months_used']}")
        print(f"    t-distribution df: {f27['t_distribution_df']}")
        print(f"    Expense mean: {f27['historical_expense_mean']:,.2f}")
        print(f"    Expense std: {f27['historical_expense_std']:,.2f}")
        print(f"    Monthly income: {f27['estimated_monthly_income']:,.2f}")
        print(f"    P(any breach): {f27['probability_any_reserve_breach']:.4f}")
        print(f"    Uncertainty changes plan: {f27['uncertainty_changes_plan']}")
        print(f"    Recommendation: {f27['recommendation']}")
        print("    Monthly forecasts:")
        for mf in f27['monthly_forecasts']:
            print(f"      Month +{mf['month_ahead']}: "
                  f"exp={mf['point_forecast_expense']:,.2f}, "
                  f"CI=[{mf['prediction_interval_lower']:,.2f}, "
                  f"{mf['prediction_interval_upper']:,.2f}] (width={mf['interval_width']:,.2f}), "
                  f"P(breach)={mf['p_breach_reserve_cumulative']:.4f}")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        f27 = {"error": str(e)}

    # ---- 3. UNCERTAINTY IMPACT DEMONSTRATION ----
    print("\n[3/3] Demonstrating uncertainty impact on financial plans...")
    try:
        demonstrations = forecaster.demonstrate_uncertainty_changes_plan(
            events, profiles,
            reserve_tightening_factors=(1.0, 1.5, 2.0, 3.0, 5.0, 8.0)
        )
        changed_any = sum(1 for d in demonstrations if d['uncertainty_changes_plan_at_any_threshold'])
        print(f"  Users evaluated: {len(demonstrations)}")
        print(f"  Users where uncertainty changes plan: {changed_any}/{len(demonstrations)}")
        for d in demonstrations:
            changed_factors = [
                s['reserve_factor']
                for s in d['reserve_sensitivity']
                if s['uncertainty_changed_verdict']
            ]
            flag = f"  *** VERDICT CHANGED at reserve x{changed_factors} ***" if changed_factors else ""
            print(f"  {d['user_id']}: CV={d['expense_cv_pct']:.2f}%, "
                  f"upper_CI={d['upper_ci_expense']:,.2f}, "
                  f"income={d['estimated_monthly_income']:,.2f}"
                  f"{flag}")
            for s in d['reserve_sensitivity']:
                if s['uncertainty_changed_verdict']:
                    print(f"    reserve×{s['reserve_factor']}: "
                          f"det={s['deterministic_verdict']}, "
                          f"prob={s['probabilistic_verdict']}")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        demonstrations = []

    # ---- Save all results ----
    all_results = {
        "calibration": cal,
        "coverage_metrics": coverage,
        "sample_forecast_user27": f27 if isinstance(f27, dict) else {},
        "uncertainty_demonstrations": demonstrations
    }

    output_path = "reports/review_verification_results.json"
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nAll results saved to {output_path}")
    print("\nSUMMARY:")
    print(f"  ECE = {cal.get('expected_calibration_error', 'N/A')} ({cal.get('calibration_verdict', 'N/A')})")
    print(f"  Coverage = {coverage.get('empirical_coverage', 'N/A')} (target {coverage.get('target_coverage', 'N/A')})")
    print(f"  Users with uncertainty-driven plan change: {changed_any if demonstrations else 'N/A'}/{len(demonstrations) if demonstrations else 'N/A'}")


if __name__ == "__main__":
    main()
