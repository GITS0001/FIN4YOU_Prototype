import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
from datetime import datetime

def train_and_evaluate():
    # 1. Paths
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    data_path = root_dir / "data" / "prototype" / "financial_events.csv"
    model_dir = Path(__file__).resolve().parent / "trained_models"
    model_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading data from {data_path}")
    if not data_path.exists():
        print("Data file not found. Please ensure data/prototype/financial_events.csv exists.")
        return

    # 2. Load Data
    df = pd.read_csv(data_path)

    # 3. Preprocessing for ML (Deterministic)
    # Ensure description and category exist
    df = df.dropna(subset=['description', 'category'])
    X = df['description'].astype(str)
    y = df['category'].astype(str)

    # 4. Train-Test Split (Fixed Seed for Reproducibility)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # 5. Build Pipeline
    print("Training TF-IDF + Logistic Regression model...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
        ('clf', LogisticRegression(class_weight='balanced', random_state=42, max_iter=1000))
    ])

    # Train
    pipeline.fit(X_train, y_train)

    # 6. Evaluate
    print("Evaluating model...")
    y_pred = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average='macro')

    # Convert confusion matrix to list for JSON serialization
    conf_matrix = confusion_matrix(y_test, y_pred).tolist()
    labels = sorted(y.unique().tolist())

    # Generate Classification Report dict
    class_report = classification_report(y_test, y_pred, output_dict=True)

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Macro F1: {macro_f1:.4f}")

    # 7. Save Evaluation Report
    evaluation_report = {
        "metrics": {
            "accuracy": float(accuracy),
            "macro_f1": float(macro_f1)
        },
        "per_class_metrics": class_report,
        "confusion_matrix": {
            "labels": labels,
            "matrix": conf_matrix
        },
        "evaluation_date": datetime.utcnow().isoformat()
    }

    eval_path = model_dir / "evaluation_report.json"
    with open(eval_path, "w") as f:
        json.dump(evaluation_report, f, indent=4)

    print(f"Evaluation report saved to {eval_path}")

    # 8. Save Model
    model_path = model_dir / "categorization_model.pkl"
    joblib.dump(pipeline, model_path)
    print(f"Model saved to {model_path}")

    # 9. Save Metadata Registry
    model_metadata = {
        "model_name": "transaction_categorizer",
        "model_type": "TF-IDF + LogisticRegression",
        "version": "1.0.0",
        "training_date": datetime.utcnow().isoformat(),
        "training_data_identifier": "financial_events.csv",
        "features": ["description_tfidf"],
        "classes": labels,
        "confidence_threshold": 0.5,
        "model_parameters": {
            "tfidf_max_features": 5000,
            "tfidf_ngram_range": [1, 2],
            "lr_class_weight": "balanced",
            "lr_max_iter": 1000,
            "random_state": 42
        },
        "evaluation_metrics": {
            "accuracy": float(accuracy),
            "macro_f1": float(macro_f1)
        },
        "limitations": "WARNING: Prototype dataset is highly repetitive/synthetic. The 1.0 metrics DO NOT represent real-world accuracy. May not generalize to novel merchant names."
    }

    metadata_path = model_dir / "model_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(model_metadata, f, indent=4)

    print(f"Model metadata saved to {metadata_path}")

if __name__ == "__main__":
    train_and_evaluate()
