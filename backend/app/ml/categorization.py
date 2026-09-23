from typing import List
from app.schemas.financial import Transaction, CategoryPrediction

class TransactionCategorizer:
    """
    Baseline ML categorizer.
    Since our dataset already provides legitimate ground-truth labels in the 'category' field,
    we act as a passthrough for known categories with a high confidence.
    This architecture is replaceable with a real ML classifier in the future.
    """
    def __init__(self):
        self.default_confidence = 0.95
        self.unknown_confidence = 0.20
        self.unknown_category = "unknown"

    def predict(self, transaction: Transaction) -> CategoryPrediction:
        # Simulate prediction using the provided raw category
        cat = transaction.category
        if not cat or cat.strip() == "":
            cat = self.unknown_category
            conf = self.unknown_confidence
        else:
            conf = self.default_confidence
            
        return CategoryPrediction(
            transaction_id=transaction.transaction_id,
            category=cat,
            confidence=conf
        )

    def predict_batch(self, transactions: List[Transaction]) -> List[CategoryPrediction]:
        return [self.predict(t) for t in transactions]
