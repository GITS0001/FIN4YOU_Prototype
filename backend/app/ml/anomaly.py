from typing import List, Dict
import math
from app.schemas.financial import Transaction, AnomalySignal

class AnomalyDetector:
    """
    Baseline ML anomaly detector.
    Uses category-level mean and standard deviation to flag unusually high expenses.
    """
    def __init__(self, std_threshold: float = 2.0):
        self.std_threshold = std_threshold

    def detect_anomalies(self, transactions: List[Transaction]) -> List[AnomalySignal]:
        if not transactions:
            return []

        # Group amounts by category (for expenses only)
        category_amounts: Dict[str, List[float]] = {}
        for t in transactions:
            if t.direction == "debit":
                if t.category not in category_amounts:
                    category_amounts[t.category] = []
                category_amounts[t.category].append(t.amount)

        # Calculate mean and std deviation per category
        category_stats = {}
        for cat, amounts in category_amounts.items():
            n = len(amounts)
            if n < 3:
                # Not enough data for statistical anomaly detection
                category_stats[cat] = {"mean": 0, "std": 0}
                continue
            
            mean = sum(amounts) / n
            variance = sum((x - mean) ** 2 for x in amounts) / (n - 1)
            std = math.sqrt(variance)
            category_stats[cat] = {"mean": mean, "std": std}

        signals = []
        for t in transactions:
            is_anomaly = False
            score = 0.0
            reason = "Normal"

            if t.direction == "debit" and t.category in category_stats:
                stats = category_stats[t.category]
                if stats["std"] > 0:
                    z_score = (t.amount - stats["mean"]) / stats["std"]
                    if z_score > self.std_threshold:
                        is_anomaly = True
                        score = z_score
                        reason = f"Statistically unusual amount for category '{t.category}' (z-score: {z_score:.2f})"

            if is_anomaly:
                signals.append(
                    AnomalySignal(
                        transaction_id=t.transaction_id,
                        is_anomaly=is_anomaly,
                        anomaly_score=score,
                        reason=reason
                    )
                )

        return signals
