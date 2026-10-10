"""
Reproducible Multi-Feature Transaction Categorizer Training Pipeline.

Integrates TF-IDF text features on transaction descriptions with one-hot encoded
direction and event_type metadata, evaluated under strict chronological out-of-time splits.

Security Notice:
Model artifacts serialized via joblib/pickle must only be loaded from trusted local sources,
as unpickling untrusted binary data can result in arbitrary code execution.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple

import pandas as pd
import numpy as np
import joblib
import sklearn

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train_categorizer")

# Root directory resolution
BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent
DATA_PATH = REPO_ROOT / "data" / "prototype" / "financial_events.csv"
MODEL_DIR = BACKEND_DIR / "app" / "ml" / "trained_models" / "multi_feature"


def load_and_validate_dataset(csv_path: Path) -> pd.DataFrame:
    """
    Loads raw transaction events and safely validates columns and labels.
    Handles missing descriptions, directions, event_types, and amounts.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Training data not found at {csv_path}")

    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(df)} total raw records from {csv_path.name}")

    # Validate essential target
    df = df.dropna(subset=['category']).copy()
    df['category'] = df['category'].astype(str).str.strip()
    df = df[df['category'] != ""]

    # Impute and clean feature columns safely
    df['description'] = df['description'].fillna("").astype(str).str.strip()
    df['direction'] = df['direction'].fillna("debit").astype(str).str.strip().str.lower()
    df['event_type'] = df['event_type'].fillna("expense").astype(str).str.strip().str.lower()

    # Amount validation: note that amount is NOT used as an ML feature because currency
    # scales differ across users (ZAR vs USD vs IDR) and amounts can overfit to synthetic constants.
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)

    # Date parsing for chronological sorting
    if 'event_date' in df.columns:
        df['event_date'] = pd.to_datetime(df['event_date'], errors='coerce')
        df = df.sort_values('event_date').reset_index(drop=True)
    else:
        logger.warning("No event_date column found; maintaining original ordering.")

    classes = sorted(df['category'].unique())
    logger.info(f"Validated {len(df)} clean records across {len(classes)} distinct categories.")
    logger.info(f"Target classes: {classes}")

    return df


def build_pipeline(c_param: float = 5.0, random_state: int = 42) -> Pipeline:
    """
    Constructs multi-feature ColumnTransformer + LogisticRegression pipeline.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            (
                'text',
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    max_features=1500,
                    sublinear_tf=True,
                    lowercase=True
                ),
                'description'
            ),
            (
                'meta',
                OneHotEncoder(handle_unknown='ignore'),
                ['direction', 'event_type']
            )
        ],
        remainder='drop'
    )

    classifier = LogisticRegression(
        C=c_param,
        max_iter=1000,
        class_weight='balanced',
        random_state=random_state,
        solver='lbfgs'
    )

    return Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', classifier)
    ])


def train_and_evaluate(
    data_path: Path = DATA_PATH,
    model_dir: Path = MODEL_DIR,
    train_split_ratio: float = 0.75
) -> Dict[str, Any]:
    """
    Executes chronological held-out evaluation, fits the final model, and persists artifacts safely.
    """
    df = load_and_validate_dataset(data_path)

    # Chronological out-of-time evaluation split
    split_idx = int(len(df) * train_split_ratio)
    train_df = df.iloc[:split_idx].copy()
    test_df = df.iloc[split_idx:].copy()

    logger.info(
        f"Chronological split: Train={len(train_df)} ({train_df['event_date'].min().date()} to {train_df['event_date'].max().date()}), "
        f"Test={len(test_df)} ({test_df['event_date'].min().date()} to {test_df['event_date'].max().date()})"
    )

    feature_cols = ['description', 'direction', 'event_type']

    # 1. Out-of-Time Held-Out Evaluation
    eval_pipeline = build_pipeline()
    eval_pipeline.fit(train_df[feature_cols], train_df['category'])
    test_preds = eval_pipeline.predict(test_df[feature_cols])

    test_acc = float(accuracy_score(test_df['category'], test_preds))
    p, r, f1, _ = precision_recall_fscore_support(test_df['category'], test_preds, average='macro', zero_division=0)
    per_class_report = classification_report(test_df['category'], test_preds, output_dict=True, zero_division=0)

    logger.info(f"Chronological Held-Out Results -> Accuracy: {test_acc:.4f}, Macro F1: {f1:.4f}")

    # 2. Final Fit on All Validated Historical Data
    final_pipeline = build_pipeline()
    final_pipeline.fit(df[feature_cols], df['category'])
    classes = list(final_pipeline.named_steps['classifier'].classes_)

    # 3. Model Directory & Artifact Persistence
    model_dir.mkdir(parents=True, exist_ok=True)
    model_artifact_path = model_dir / "multi_feature_categorizer.joblib"
    meta_artifact_path = model_dir / "metadata.json"

    # Save pipeline safely
    joblib.dump(final_pipeline, model_artifact_path)
    logger.info(f"Saved model artifact to {model_artifact_path}")

    # Compile comprehensive metadata manifest
    class_counts = df['category'].value_counts().to_dict()
    metadata: Dict[str, Any] = {
        "model_name": "multi_feature_transaction_categorizer",
        "model_type": "ColumnTransformer(TF-IDF + OneHotEncoder) + LogisticRegression",
        "created_at": datetime.utcnow().isoformat(),
        "python_version": sys.version.split()[0],
        "scikit_learn_version": sklearn.__version__,
        "joblib_version": joblib.__version__,
        "training_data_file": data_path.name,
        "n_samples_total": len(df),
        "n_classes": len(classes),
        "classes": classes,
        "class_distribution": class_counts,
        "feature_columns": feature_cols,
        "chronological_evaluation": {
            "train_ratio": train_split_ratio,
            "train_samples": len(train_df),
            "test_samples": len(test_df),
            "test_accuracy": round(test_acc, 4),
            "macro_f1": round(float(f1), 4),
            "macro_precision": round(float(p), 4),
            "macro_recall": round(float(r), 4),
            "per_class_metrics": per_class_report
        },
        "calibration_notes": (
            "Confidence scores are raw maximum softmax posterior probabilities and have not undergone "
            "empirical Platt scaling or isotonic regression. They represent heuristic decision indicators."
        ),
        "security_notes": (
            "This artifact contains serialized python objects (joblib/pickle). Only load from local trusted storage."
        )
    }

    with open(meta_artifact_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved metadata manifest to {meta_artifact_path}")

    return metadata


if __name__ == "__main__":
    meta = train_and_evaluate()
    print("\nTraining and Evaluation Summary:")
    print(f"- Classes ({meta['n_classes']}): {meta['classes']}")
    print(f"- Chronological Test Accuracy: {meta['chronological_evaluation']['test_accuracy']:.2%}")
    print(f"- Chronological Test Macro F1: {meta['chronological_evaluation']['macro_f1']:.4f}")
