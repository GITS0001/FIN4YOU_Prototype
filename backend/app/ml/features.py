import pandas as pd
from typing import List, Dict, Any
from app.schemas.financial import Transaction

class FeatureEngineer:
    """
    Engineers time-based financial features from canonical transactions.
    These features feed into Forecasting and Anomaly Detection models.
    """

    @staticmethod
    def engineer_features(transactions: List[Transaction]) -> Dict[str, Any]:
        if not transactions:
            return {}

        # Convert to DataFrame
        df = pd.DataFrame([t.model_dump() for t in transactions])
        df['event_date'] = pd.to_datetime(df['event_date'])
        df = df.sort_values('event_date')

        # 1. Base Aggregations
        income_df = df[df['event_type'] == 'income']
        expense_df = df[df['event_type'] == 'expense']

        total_income = income_df['amount'].sum()
        total_expense = expense_df['amount'].sum()

        # 2. Time-based rolling features (Monthly)
        df.set_index('event_date', inplace=True)
        monthly_expenses = expense_df.set_index('event_date').resample('ME')['amount'].sum()
        monthly_income = income_df.set_index('event_date').resample('ME')['amount'].sum()

        rolling_3m_expenses = monthly_expenses.rolling(window=3, min_periods=1).mean().iloc[-1] if not monthly_expenses.empty else 0.0
        rolling_3m_income = monthly_income.rolling(window=3, min_periods=1).mean().iloc[-1] if not monthly_income.empty else 0.0

        # 3. Volatility (Standard Deviation of monthly cash flow)
        monthly_cash_flow = monthly_income.fillna(0) - monthly_expenses.fillna(0)
        cash_flow_volatility = float(monthly_cash_flow.std()) if len(monthly_cash_flow) > 1 else 0.0

        # 4. Expense Ratio and Savings Rate
        expense_ratio = float(total_expense / total_income) if total_income > 0 else 1.0
        savings_rate = float(max(0, (total_income - total_expense)) / total_income) if total_income > 0 else 0.0

        # 5. Category Concentration
        category_spending = expense_df.groupby('category')['amount'].sum()
        top_category = category_spending.idxmax() if not category_spending.empty else "None"
        top_category_concentration = float(category_spending.max() / total_expense) if total_expense > 0 and not category_spending.empty else 0.0

        return {
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "rolling_3m_expenses": float(rolling_3m_expenses),
            "rolling_3m_income": float(rolling_3m_income),
            "cash_flow_volatility": cash_flow_volatility,
            "expense_ratio": expense_ratio,
            "savings_rate": savings_rate,
            "top_expense_category": top_category,
            "top_category_concentration": top_category_concentration
        }
