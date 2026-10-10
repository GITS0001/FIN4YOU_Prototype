from typing import List
from pathlib import Path
import joblib
import pandas as pd
from app.schemas.financial import Transaction, CategoryPrediction

class TransactionCategorizer:
    """
    ML categorizer using TF-IDF and Logistic Regression.
    Supports multi-feature pipeline (description + direction + event_type) with graceful
    fallback to legacy text-only pipeline or rule-based defaults if model is unavailable.
    """
    def __init__(self):
        self.default_confidence = 0.95
        self.unknown_confidence = 0.20
        self.unknown_category = "unknown"
        self.is_multi_feature = False
        self.model = None

        multi_feature_path = Path(__file__).resolve().parent / "trained_models" / "multi_feature" / "multi_feature_categorizer.joblib"
        legacy_path = Path(__file__).resolve().parent / "trained_models" / "categorization_model.pkl"

        # Prefer multi-feature pipeline if present, fall back to legacy artifact
        if multi_feature_path.exists():
            try:
                self.model = joblib.load(multi_feature_path)
                self.is_multi_feature = True
            except Exception as e:
                print(f"Failed to load multi-feature categorization model: {e}")

        if not self.model and legacy_path.exists():
            try:
                self.model = joblib.load(legacy_path)
                self.is_multi_feature = False
            except Exception as e:
                print(f"Failed to load legacy categorization model: {e}")

    def predict(self, transaction: Transaction) -> CategoryPrediction:
        cat = transaction.category
        conf = self.default_confidence
        status = "needs_review"
        confidence_level = "low"

        # If we have a trained model, use it to predict
        if self.model:
            try:
                desc = (transaction.description or "").strip()
                if desc:
                    if self.is_multi_feature:
                        df_in = pd.DataFrame([{
                            "description": desc,
                            "direction": (transaction.direction or "debit").strip().lower(),
                            "event_type": (transaction.event_type or "expense").strip().lower()
                        }])
                        probas = self.model.predict_proba(df_in)[0]
                    else:
                        probas = self.model.predict_proba([desc])[0]

                    max_prob = float(max(probas))
                    pred_idx = probas.argmax()
                    pred = self.model.classes_[pred_idx]

                    conf = max_prob
                    if conf >= 0.8:
                        cat = pred
                        status = "classified"
                        confidence_level = "high"
                    elif conf >= 0.5:
                        cat = pred
                        status = "classified"
                        confidence_level = "medium"
                    else:
                        cat = self.unknown_category
                        status = "needs_review"
                        confidence_level = "low"
            except Exception:
                # Fallback gracefully if predict_proba fails
                pass

        if not cat or cat.strip() == "":
            cat = self.unknown_category
            conf = self.unknown_confidence
            status = "needs_review"
            confidence_level = "low"

        return CategoryPrediction(
            transaction_id=transaction.transaction_id,
            category=cat,
            confidence=conf,
            status=status,
            confidence_level=confidence_level
        )

    def predict_batch(self, transactions: List[Transaction]) -> List[CategoryPrediction]:
        return [self.predict(t) for t in transactions]
