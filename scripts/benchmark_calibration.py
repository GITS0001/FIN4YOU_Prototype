"""
Reproducible Benchmark Script for ML Probability Calibration (Member 2).

Compares:
  1. Original uncalibrated classifier (T = 1.0)
  2. Report hypothesis configuration (T = 0.6)
  3. Validation-optimized temperature scaling (T* fit via out-of-fold cross-validation)
  4. Platt Scaling (CalibratedClassifierCV via sigmoid mapping)

Evaluates on held-out chronological test set (n=221, Oct 2025 - Jul 2026).
Outputs results to console and reports/calibration_benchmark_results.json.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fin4you.data.loader import load_events
from fin4you.models.categorizer import TransactionCategorizer
from fin4you.models.calibration import (
    TemperatureScaler,
    evaluate_calibration_metrics,
    compare_calibration_methods,
    compute_ece
)


def run_calibration_benchmark():
    print("=" * 80)
    print("MEMBER 2: ML PROBABILITY CALIBRATION BENCHMARK & EVALUATION")
    print("=" * 80)

    # 1. Load dataset & prepare chronological split
    events = load_events().sort_values('event_date').reset_index(drop=True)
    n_total = len(events)
    split_idx = int(n_total * 0.75)

    train_df = events.iloc[:split_idx].copy().reset_index(drop=True)
    test_df = events.iloc[split_idx:].copy().reset_index(drop=True)

    print(f"Total dataset: {n_total} events")
    print(f"Training split: {len(train_df)} events ({train_df['event_date'].min().date()} to {train_df['event_date'].max().date()})")
    print(f"Held-out test split: {len(test_df)} events ({test_df['event_date'].min().date()} to {test_df['event_date'].max().date()})")
    print("-" * 80)

    # 2. Run multi-method comparison
    print("Fitting models and calibrators exclusively on training/cross-validation partitions...")
    results = compare_calibration_methods(
        train_df=train_df,
        test_df=test_df,
        n_bins=10,
        n_cv_splits=5,
        random_state=42
    )

    summary_table = results["summary_table"]
    print("\n" + "=" * 80)
    print("TEST-SET CALIBRATION METRICS COMPARISON TABLE (Held-out n=221)")
    print("=" * 80)
    print(f"{'Method / Configuration':<36} | {'Accuracy':<9} | {'NLL':<8} | {'Brier':<8} | {'ECE':<8} | {'Mean Conf':<10}")
    print("-" * 86)

    for method, metrics in summary_table.items():
        print(f"{method:<36} | {metrics['Accuracy']:<9.4f} | {metrics['NLL']:<8.4f} | {metrics['Brier Score']:<8.4f} | {metrics['ECE']:<8.4f} | {metrics['Mean Confidence']:<10.4f}")

    print("-" * 86)
    sel = results["selected_calibrator"]
    print(f"\nWinning Calibrator: {sel['name']} (T={sel['temperature']:.4f})")
    print(f"Target ECE < 0.05 Achieved: {'YES [PASSED]' if sel['achieved_ece_target'] else 'NO [FAILED]'}")
    print(f"Final Test ECE: {sel['metrics']['ece']:.4f}")

    # 3. Print Reliability Table for Winning Calibrator
    print("\n" + "=" * 80)
    print(f"RELIABILITY DIAGRAM BINS FOR SELECTED CALIBRATOR ({sel['name']})")
    print("=" * 80)
    print(f"{'Bin Range':<14} | {'Samples':<8} | {'Mean Conf':<11} | {'Accuracy':<10} | {'Gap (Acc - Conf)':<18} | {'Status':<16}")
    print("-" * 86)
    for b in sel['metrics']['reliability_bins']:
        if b['n_samples'] > 0:
            print(f"{b['bin_range']:<14} | {b['n_samples']:<8} | {b['mean_confidence']:<11.4f} | {b['accuracy']:<10.4f} | {b['gap']:<+18.4f} | {b['calibration_direction']:<16}")
        else:
            print(f"{b['bin_range']:<14} | {'0':<8} | {'-':<11} | {'-':<10} | {'-':<18} | {'no_data':<16}")

    # 4. Save results to reports/calibration_benchmark_results.json
    out_dir = Path("reports")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "calibration_benchmark_results.json"

    # Make JSON serializable
    def clean_obj(obj):
        if isinstance(obj, (np.floating, float)):
            return round(float(obj), 6)
        elif isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: clean_obj(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_obj(v) for v in obj]
        return obj

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(clean_obj(results), f, indent=2)

    print(f"\nPersisted complete calibration benchmarks to: {out_path}")
    return results


if __name__ == '__main__':
    run_calibration_benchmark()
