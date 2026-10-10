"""
Machine Learning Transaction Categorizer with Calibrated Confidence Scoring.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report

from fin4you.config import (
    CATEGORIZER_MODEL_PATH,
    CATEGORIZER_META_PATH,
    CONFIDENCE_HIGH_THRESHOLD,
    CONFIDENCE_MEDIUM_THRESHOLD
)

class TransactionCategorizer:
    """
    Supervised classifier that maps raw financial transaction text and metadata
    into standardized budget categories with calibrated confidence scores.
    """
    
    def __init__(self, C: float = 5.0, random_state: int = 42):
        self.C = C
        self.random_state = random_state
        self.classes_ = []
        self.pipeline: Optional[Pipeline] = None
        self.metadata: Dict[str, Any] = {}
        
    def _build_pipeline(self) -> Pipeline:
        preprocessor = ColumnTransformer(
            transformers=[
                ('text', TfidfVectorizer(ngram_range=(1, 2), max_features=1500, sublinear_tf=True, lowercase=True), 'description'),
                ('meta', OneHotEncoder(handle_unknown='ignore'), ['direction', 'event_type'])
            ],
            remainder='drop'
        )
        
        clf = LogisticRegression(
            C=self.C,
            max_iter=1000,
            class_weight='balanced',
            random_state=self.random_state,
            solver='lbfgs'
        )
        
        return Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', clf)
        ])
        
    def fit(self, df: pd.DataFrame) -> "TransactionCategorizer":
        """
        Train the pipeline on labeled transactions.
        Requires columns: 'description', 'direction', 'event_type', 'category'.
        """
        data = df.dropna(subset=['description', 'category']).copy()
        data['direction'] = data['direction'].fillna('debit')
        data['event_type'] = data['event_type'].fillna('expense')
        
        self.pipeline = self._build_pipeline()
        self.pipeline.fit(data[['description', 'direction', 'event_type']], data['category'])
        self.classes_ = list(self.pipeline.named_steps['classifier'].classes_)
        
        train_preds = self.pipeline.predict(data[['description', 'direction', 'event_type']])
        acc = accuracy_score(data['category'], train_preds)
        p, r, f1, _ = precision_recall_fscore_support(data['category'], train_preds, average='macro', zero_division=0)
        
        self.metadata = {
            "n_samples": len(data),
            "n_classes": len(self.classes_),
            "classes": self.classes_,
            "train_accuracy": float(acc),
            "train_macro_f1": float(f1),
            "train_macro_precision": float(p),
            "train_macro_recall": float(r)
        }
        return self

    def predict_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Predict categories and calibrated confidence scores for a batch dataframe.
        Returns a DataFrame with columns: predicted_category, ml_confidence, ml_status, ml_confidence_level.
        """
        if self.pipeline is None:
            raise RuntimeError("Model is not fitted or loaded yet.")
            
        data = df.copy()
        if 'description' not in data.columns:
            data['description'] = ''
        if 'direction' not in data.columns:
            data['direction'] = 'debit'
        if 'event_type' not in data.columns:
            data['event_type'] = 'expense'
            
        data['description'] = data['description'].fillna('')
        data['direction'] = data['direction'].fillna('debit')
        data['event_type'] = data['event_type'].fillna('expense')
        
        probabilities = self.pipeline.predict_proba(data[['description', 'direction', 'event_type']])
        pred_idx = np.argmax(probabilities, axis=1)
        confidences = np.max(probabilities, axis=1)
        
        predictions = [self.classes_[i] for i in pred_idx]
        
        statuses = [
            'confirmed' if c >= CONFIDENCE_HIGH_THRESHOLD else 'review_needed'
            for c in confidences
        ]
        levels = [
            'high' if c >= CONFIDENCE_HIGH_THRESHOLD 
            else ('medium' if c >= CONFIDENCE_MEDIUM_THRESHOLD else 'low')
            for c in confidences
        ]
        
        result_df = pd.DataFrame({
            'predicted_category': predictions,
            'ml_confidence': np.round(confidences, 4),
            'ml_status': statuses,
            'ml_confidence_level': levels
        }, index=df.index)
        
        return result_df

    def predict_single(
        self,
        description: str,
        direction: str = "debit",
        event_type: str = "expense",
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Inference on a single transaction.
        """
        df_single = pd.DataFrame([{
            'description': description,
            'direction': direction,
            'event_type': event_type
        }])
        res = self.predict_records(df_single).iloc[0]
        
        # Get top 3 candidate categories with probabilities
        if self.pipeline is not None:
            probs = self.pipeline.predict_proba(df_single[['description', 'direction', 'event_type']])[0]
            top_indices = np.argsort(probs)[::-1][:3]
            top_candidates = [
                {"category": self.classes_[i], "confidence": round(float(probs[i]), 4)}
                for i in top_indices
            ]
        else:
            top_candidates = []
            
        return {
            "predicted_category": res['predicted_category'],
            "ml_confidence": float(res['ml_confidence']),
            "ml_status": res['ml_status'],
            "ml_confidence_level": res['ml_confidence_level'],
            "top_candidates": top_candidates
        }

    def save(self, filepath: Optional[Path] = None, meta_path: Optional[Path] = None) -> None:
        """
        Serialize model pipeline and metadata.
        """
        p_path = filepath or CATEGORIZER_MODEL_PATH
        m_path = meta_path or CATEGORIZER_META_PATH
        
        os.makedirs(os.path.dirname(p_path), exist_ok=True)
        joblib.dump(self.pipeline, p_path)
        with open(m_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2)

    @classmethod
    def load(cls, filepath: Optional[Path] = None, meta_path: Optional[Path] = None) -> "TransactionCategorizer":
        """
        Load trained model from disk.
        """
        p_path = filepath or CATEGORIZER_MODEL_PATH
        m_path = meta_path or CATEGORIZER_META_PATH
        
        if not os.path.exists(p_path):
            raise FileNotFoundError(f"Trained pipeline artifact not found at {p_path}")
            
        instance = cls()
        instance.pipeline = joblib.load(p_path)
        instance.classes_ = list(instance.pipeline.named_steps['classifier'].classes_)
        if os.path.exists(m_path):
            with open(m_path, 'r', encoding='utf-8') as f:
                instance.metadata = json.load(f)
        return instance
