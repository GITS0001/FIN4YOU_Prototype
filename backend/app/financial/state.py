from typing import List, Dict
from app.schemas.financial import Transaction, FinancialState, CategorySpending
from app.ml.anomaly import AnomalyDetector

class FinancialStateEngine:
    """
    Calculates deterministic financial metrics based on transaction history.
    """
    def __init__(self, user_id: str, std_threshold: float = 2.0):
        self.user_id = user_id
        self.anomaly_detector = AnomalyDetector(std_threshold=std_threshold)

    def calculate_state(self, transactions: List[Transaction], data_quality_confidence: float = 1.0) -> FinancialState:
        income = 0.0
        expenses = 0.0
        essential_expenses = 0.0
        discretionary_expenses = 0.0
        recurring_obligations = 0.0
        emi_burden = 0.0
        
        category_totals: Dict[str, float] = {}

        for t in transactions:
            # We assume t.amount is already absolute
            if t.event_type == "income":
                income += t.amount
            elif t.event_type == "refund":
                expenses -= t.amount
                cat = t.category if t.category else "unknown"
                category_totals[cat] = category_totals.get(cat, 0.0) - t.amount
                if t.flexibility == "fixed":
                    essential_expenses -= t.amount
                else:
                    discretionary_expenses -= t.amount
            elif t.direction == "debit":
                expenses += t.amount
                
                # Category breakdown
                cat = t.category if t.category else "unknown"
                category_totals[cat] = category_totals.get(cat, 0.0) + t.amount

                # Essential vs Discretionary
                if t.flexibility == "fixed":
                    essential_expenses += t.amount
                    
                    # Recurring obligations (subscriptions or debt payments that are fixed)
                    if t.event_type in ["subscription", "debt_payment"]:
                        recurring_obligations += t.amount
                else:
                    discretionary_expenses += t.amount
                
                # EMI Burden (debt repayment)
                if t.event_type == "debt_payment" or cat == "debt_repayment":
                    emi_burden += t.amount

        savings = income - expenses
        cash_flow = savings
        savings_rate = (savings / income) if income > 0 else 0.0
        expense_ratio = (expenses / income) if income > 0 else 0.0

        # Sort category spending by highest amount
        cat_spending = [
            CategorySpending(category=k, total_amount=v) 
            for k, v in sorted(category_totals.items(), key=lambda item: item[1], reverse=True)
        ]

        # Anomaly Detection
        anomalies = self.anomaly_detector.detect_anomalies(transactions)

        return FinancialState(
            user_id=self.user_id,
            income=income,
            expenses=expenses,
            savings=savings,
            savings_rate=savings_rate,
            expense_ratio=expense_ratio,
            essential_expenses=essential_expenses,
            discretionary_expenses=discretionary_expenses,
            recurring_obligations=recurring_obligations,
            emi_burden=emi_burden,
            cash_flow=cash_flow,
            category_spending=cat_spending,
            anomalies=anomalies,
            data_quality_confidence=data_quality_confidence
        )
