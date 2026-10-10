"""Debug: Find conditions where uncertainty changes plan."""
import sys; sys.path.insert(0,'.')
from fin4you.data.loader import load_events, load_profiles
from fin4you.models.probabilistic_forecaster import ProbabilisticForecaster

events = load_events()
profiles = load_profiles()
forecaster = ProbabilisticForecaster(forecast_months=6, confidence_level=0.95)

for user_id in ['user_30', 'user_28', 'user_01', 'user_05']:
    prof = profiles[profiles['user_id'] == user_id].iloc[0]
    min_res = float(prof['minimum_balance_to_keep'])
    curr = float(prof['current_available_balance'])

    exp_s = forecaster._get_completed_monthly_series(events, user_id, 'debit')
    inc_s = forecaster._get_completed_monthly_series(events, user_id, 'credit')

    if len(exp_s) < 3:
        continue

    mu, sigma, lower, upper = forecaster._t_prediction_interval(exp_s.values, 0.95)
    inc_mu = float(inc_s.mean()) if len(inc_s) >= 1 else 0.0

    print(f"\n{user_id}: balance={curr:.2f}, min_reserve={min_res:.2f}")
    print(f"  expense: mu={mu:.2f}, sigma={sigma:.2f}, upper_CI={upper:.2f}")
    print(f"  income_mu={inc_mu:.2f}")

    found = False
    for f in [1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0, 50.0]:
        test_res = min_res * f
        det_6m = curr + (inc_mu - mu) * 6
        prob_6m = curr + inc_mu * 6 - upper * 6
        det_safe = det_6m >= test_res
        prob_safe = prob_6m >= test_res
        verdict = "CHANGED" if det_safe != prob_safe else "same"
        print(f"  x{f}: reserve={test_res:.2f}, det_end={det_6m:.2f}({'safe' if det_safe else 'risk'}), prob_end={prob_6m:.2f}({'safe' if prob_safe else 'risk'}) => {verdict}")
        if det_safe != prob_safe and not found:
            found = True
