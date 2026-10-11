from typing import List, Dict, Optional
from datetime import date
from app.schemas.financial import (
    Transaction, FinancialState, CategorySpending, FinancialProfile,
    FinancialPeriod, DataQualitySummary
)
from app.ml.anomaly import AnomalyDetector
from app.financial.merchants import resolve_category_from_description

class FinancialStateEngine:
    """
    Calculates deterministic financial metrics based on transaction history.
    Adheres strictly to the single canonical financial state contract.
    """
    def __init__(self, user_id: str, std_threshold: float = 2.0):
        self.user_id = user_id
        self.anomaly_detector = AnomalyDetector(std_threshold=std_threshold)

    def calculate_state(
        self,
        transactions: List[Transaction],
        profile: Optional[FinancialProfile] = None,
        data_quality_confidence: float = 1.0,
        period_type: str = "all",
        month_filter: Optional[str] = None
    ) -> FinancialState:
        currency = profile.home_currency if profile else "INR"
        available_balance = profile.current_available_balance if profile else None
        minimum_buffer = profile.minimum_balance_to_keep if profile else None

        if not transactions:
            period = FinancialPeriod(start=None, end=None, type=period_type, month=month_filter)
            dq = DataQualitySummary(
                has_transactions=False,
                has_balance=available_balance is not None and available_balance > 0,
                warnings=["No transactions available for the selected period."]
            )
            return FinancialState(
                user_id=self.user_id,
                income=0.0,
                expenses=0.0,
                savings=0.0,
                savings_rate=0.0,
                expense_ratio=0.0,
                essential_expenses=0.0,
                discretionary_expenses=0.0,
                recurring_obligations=0.0,
                emi_burden=0.0,
                cash_flow=0.0,
                category_spending=[],
                anomalies=[],
                data_quality_confidence=data_quality_confidence,
                currency=currency,
                period=period,
                available_balance=available_balance,
                minimum_buffer=minimum_buffer,
                total_income=0.0,
                total_expenses=0.0,
                net_cash_flow=0.0,
                category_breakdown=[],
                transaction_count=0,
                data_quality=dq
            )

        # Helper to get month string YYYY-MM
        def get_m_str(d) -> str:
            if hasattr(d, 'strftime'):
                return d.strftime("%Y-%m")
            return str(d)[:7]

        # Apply monthly filter if specified, or if period_type is monthly and transactions span multiple months
        filtered_txs = transactions
        active_month = month_filter
        if month_filter and month_filter.lower() != "all":
            filtered_txs = [t for t in transactions if get_m_str(t.event_date) == month_filter]
        elif period_type == "monthly":
            all_months = sorted(set(get_m_str(t.event_date) for t in transactions if t.event_date))
            if all_months:
                active_month = all_months[-1]
                filtered_txs = [t for t in transactions if get_m_str(t.event_date) == active_month]

        income = 0.0
        expenses = 0.0
        essential_expenses = 0.0
        discretionary_expenses = 0.0
        recurring_obligations = 0.0
        emi_burden = 0.0
        
        category_totals: Dict[str, float] = {}

        for t in filtered_txs:
            ev_type = str(t.event_type or "").lower()
            dir_type = str(t.direction or "").lower()
            cat_name = str(t.category or "").lower()
            desc_lower = str(t.description or "").lower()

            # Internal transfers and credit card settlements must not inflate income or expenses
            if (
                ev_type in ["transfer", "internal_transfer"]
                or cat_name in ["transfer", "internal_transfer"]
                or "credit card payment" in desc_lower
                or "cc payment" in desc_lower
                or "card bill payment" in desc_lower
            ):
                continue

            # Amount is always non-negative
            amt = abs(t.amount)

            if ev_type == "income" or (dir_type in ["credit", "inflow"] and ev_type != "refund" and dir_type != "refund"):
                income += amt
            elif ev_type == "refund" or dir_type == "refund" or "refund" in desc_lower:
                # Refunds reduce expenses and category totals
                expenses = expenses - amt
                cat = resolve_category_from_description(t.description, t.category)
                category_totals[cat] = category_totals.get(cat, 0.0) - amt
                if t.flexibility == "fixed":
                    essential_expenses = essential_expenses - amt
                else:
                    discretionary_expenses = discretionary_expenses - amt
            elif dir_type in ["debit", "outflow"] or ev_type in ["expense", "subscription", "debt_payment"]:
                expenses += amt
                
                # Category breakdown
                cat = resolve_category_from_description(t.description, t.category)
                category_totals[cat] = category_totals.get(cat, 0.0) + amt

                # Essential vs Discretionary
                if t.flexibility == "fixed":
                    essential_expenses += amt
                    if t.event_type in ["subscription", "debt_payment"]:
                        recurring_obligations += amt
                else:
                    discretionary_expenses += amt
                
                # EMI Burden (debt repayment)
                if t.event_type == "debt_payment" or cat in ["debt_repayment", "emi"]:
                    emi_burden += amt

        savings = income - expenses
        cash_flow = savings
        savings_rate = (savings / income) if income > 0 else 0.0
        expense_ratio = (expenses / income) if income > 0 else 0.0

        # Sort category spending by highest amount
        cat_spending = [
            CategorySpending(category=k, total_amount=round(v, 2)) 
            for k, v in sorted(category_totals.items(), key=lambda item: item[1], reverse=True)
            if v != 0
        ]

        # Anomaly Detection on current batch
        anomalies = self.anomaly_detector.detect_anomalies(filtered_txs)

        dates = [t.event_date for t in filtered_txs if t.event_date]
        min_date = str(min(dates)) if dates else None
        max_date = str(max(dates)) if dates else None
        period = FinancialPeriod(start=min_date, end=max_date, type=period_type, month=active_month)

        warnings = []
        if income == 0 and expenses > 0:
            warnings.append("No income detected for this period.")
        if expenses > income and income > 0:
            warnings.append("Expenses exceed income for this period.")
        if available_balance is None:
            warnings.append("Available balance is not set in user profile.")

        dq = DataQualitySummary(
            has_transactions=len(filtered_txs) > 0,
            has_balance=available_balance is not None and available_balance > 0,
            warnings=warnings
        )

        return FinancialState(
            user_id=self.user_id,
            income=round(income, 2),
            expenses=round(expenses, 2),
            savings=round(savings, 2),
            savings_rate=round(savings_rate, 4) if savings_rate is not None else None,
            expense_ratio=round(expense_ratio, 4),
            essential_expenses=round(essential_expenses, 2),
            discretionary_expenses=round(discretionary_expenses, 2),
            recurring_obligations=round(recurring_obligations, 2),
            emi_burden=round(emi_burden, 2),
            cash_flow=round(cash_flow, 2),
            category_spending=cat_spending,
            anomalies=anomalies,
            data_quality_confidence=data_quality_confidence,
            currency=currency,
            period=period,
            available_balance=available_balance,
            minimum_buffer=minimum_buffer,
            total_income=round(income, 2),
            total_expenses=round(expenses, 2),
            net_cash_flow=round(cash_flow, 2),
            category_breakdown=cat_spending,
            transaction_count=len(filtered_txs),
            data_quality=dq
        )
