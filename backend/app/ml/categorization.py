from typing import List
from pathlib import Path
import joblib
import pandas as pd
from app.schemas.financial import Transaction, CategoryPrediction
from app.financial.merchants import detect_merchant_info

_CACHED_MODEL = None
_CACHED_IS_MULTI = False
_MODEL_LOAD_ATTEMPTED = False

class TransactionCategorizer:
    """
    ML categorizer using TF-IDF and Logistic Regression.
    Supports multi-feature pipeline (description + direction + event_type) with graceful
    fallback to legacy text-only pipeline or rule-based defaults if model is unavailable.
    """
    def __init__(self):
        global _CACHED_MODEL, _CACHED_IS_MULTI, _MODEL_LOAD_ATTEMPTED
        self.default_confidence = 0.95
        self.unknown_confidence = 0.20
        self.unknown_category = "unknown"

        if not _MODEL_LOAD_ATTEMPTED:
            _MODEL_LOAD_ATTEMPTED = True
            multi_feature_path = Path(__file__).resolve().parent / "trained_models" / "multi_feature" / "multi_feature_categorizer.joblib"
            legacy_path = Path(__file__).resolve().parent / "trained_models" / "categorization_model.pkl"

            if multi_feature_path.exists():
                try:
                    _CACHED_MODEL = joblib.load(multi_feature_path)
                    _CACHED_IS_MULTI = True
                except Exception as e:
                    print(f"Failed to load multi-feature categorization model: {e}")

            if not _CACHED_MODEL and legacy_path.exists():
                try:
                    _CACHED_MODEL = joblib.load(legacy_path)
                    _CACHED_IS_MULTI = False
                except Exception as e:
                    print(f"Failed to load legacy categorization model: {e}")

        self.model = _CACHED_MODEL
        self.is_multi_feature = _CACHED_IS_MULTI

    def predict(self, transaction: Transaction) -> CategoryPrediction:
        desc = (transaction.description or "").strip()
        merchant_info = detect_merchant_info(desc)
        if merchant_info:
            return CategoryPrediction(
                transaction_id=transaction.transaction_id,
                category=merchant_info["category"],
                confidence=0.98,
                status="classified",
                confidence_level="high"
            )

        cat = transaction.category
        conf = self.default_confidence
        status = "needs_review"
        confidence_level = "low"

        # If we have a trained model, use it to predict
        if self.model:
            try:
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

        # If model is available but confidence is low, apply domain keyword heuristics
        if self.model is not None and (not cat or cat == self.unknown_category or conf < 0.5):
            desc_upper = (transaction.description or "").upper()
            dir_str = (transaction.direction or "").lower()
            
            if "SALARY" in desc_upper or "PAYROLL" in desc_upper or "STIPEND" in desc_upper:
                cat = "salary"
                conf = 0.95
                status = "classified"
                confidence_level = "high"
            elif any(u in desc_upper for u in ["ELECTRICITY", "TORRENT POWER", "BESCOM", "WATER", "BROADBAND", "ACT FIBERNET", "AIRTEL", "JIO", "VODAFONE", "BILLPAY", "MOBILE BILL", "GAS"]):
                cat = "utilities"
                conf = 0.95
                status = "classified"
                confidence_level = "high"
            elif any(r in desc_upper for r in ["RENT", "SKYLINE PROPERTIES", "LANDLORD", "MAINTENANCE"]):
                cat = "rent"
                conf = 0.95
                status = "classified"
                confidence_level = "high"
            elif any(f in desc_upper for f in ["SWIGGY", "ZOMATO", "BLINKIT", "ZEPTO", "GROCERY", "SUPERMARKET", "DMART", "BIGBASKET", "RESTAURANT", "DINING"]):
                cat = "food"
                conf = 0.95
                status = "classified"
                confidence_level = "high"
            elif any(t_kw in desc_upper for t_kw in ["UBER", "OLA", "METRO", "PETROL", "FUEL", "HPCL", "BPCL", "IOCL", "FASTAG"]):
                cat = "transport"
                conf = 0.95
                status = "classified"
                confidence_level = "high"
            elif any(tx in desc_upper for tx in ["TDS", "ITNS", "INCOME TAX", "GST"]):
                cat = "taxes"
                conf = 0.95
                status = "classified"
                confidence_level = "high"
            elif any(s in desc_upper for s in ["HARDWARE", "PURCHASE", "SUPPLIES"]):
                cat = "office_supplies"
                conf = 0.90
                status = "classified"
                confidence_level = "high"
            elif any(rev in desc_upper for rev in ["MERIDIAN RETAIL", "NORTHSTAR LOGISTICS", "BLUEPEAK CONSULTING", "ORION HEALTHCARE"]):
                cat = "sales_revenue" if dir_str == "credit" else "business_expense"
                conf = 0.90
                status = "classified"
                confidence_level = "high"
            elif any(h in desc_upper for h in ["PHARMACY", "APOLLO", "HOSPITAL", "CLINIC", "MEDPLUS"]):
                cat = "healthcare"
                conf = 0.95
                status = "classified"
                confidence_level = "high"
            elif any(ent in desc_upper for ent in ["NETFLIX", "SPOTIFY", "PRIME", "HOTSTAR", "PVR", "CINEMA"]):
                cat = "entertainment"
                conf = 0.95
                status = "classified"
                confidence_level = "high"

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
