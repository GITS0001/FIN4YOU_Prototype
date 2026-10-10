from typing import List, Dict, Any, Optional
from datetime import datetime, date
import pandas as pd
from app.schemas.financial import Transaction, FinancialState

class MonthlyReportEngine:
    """
    Generates a deterministic Monthly Financial Report by comparing the
    current month to the previous month.
    """

    @staticmethod
    def generate_report(transactions: List[Transaction], current_state: FinancialState) -> Dict[str, Any]:
        if not transactions:
            return {"error": "No transactions available for report generation"}

        # Convert to pandas
        df = pd.DataFrame([t.model_dump() for t in transactions])
        df['event_date'] = pd.to_datetime(df['event_date'])

        # Sort and find current vs previous month
        # Assuming data ends at the most recent transaction date
        max_date = df['event_date'].max()
        if pd.isna(max_date):
            return {"error": "Invalid date in transactions"}

        current_month_str = f"{max_date.year}-{max_date.month:02d}"

        # Determine previous month string
        prev_month = max_date.month - 1
        prev_year = max_date.year
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1
        prev_month_str = f"{prev_year}-{prev_month:02d}"

        # Group data
        df['month_key'] = df['event_date'].dt.strftime('%Y-%m')

        curr_df = df[df['month_key'] == current_month_str]
        prev_df = df[df['month_key'] == prev_month_str]

        # Calculate totals
        curr_income = curr_df[curr_df['event_type'] == 'income']['amount'].sum()
        curr_expense = curr_df[curr_df['event_type'] == 'expense']['amount'].sum()
        curr_savings = max(0, curr_income - curr_expense)
        curr_savings_rate = (curr_savings / curr_income) if curr_income > 0 else 0.0

        prev_income = prev_df[prev_df['event_type'] == 'income']['amount'].sum()
        prev_expense = prev_df[prev_df['event_type'] == 'expense']['amount'].sum()
        prev_savings = max(0, prev_income - prev_expense)
        prev_savings_rate = (prev_savings / prev_income) if prev_income > 0 else 0.0

        # Change calculation
        income_change = curr_income - prev_income
        expense_change = curr_expense - prev_expense
        savings_change = curr_savings - prev_savings

        # Top Categories Current Month
        curr_categories = curr_df[curr_df['event_type'] == 'expense'].groupby('category')['amount'].sum().to_dict()

        # Extract Anomalies from the current state
        anomaly_summaries = [f"{a.reason} (Score: {a.anomaly_score:.2f})" for a in current_state.anomalies if a.is_anomaly]

        # Major Observations
        observations = []
        if expense_change > 0:
            observations.append(f"Expenses increased by {expense_change:.2f} compared to last month.")
        else:
            observations.append(f"Great job! Expenses decreased by {abs(expense_change):.2f} compared to last month.")

        if curr_savings_rate < 0.10:
            observations.append("Your savings rate is below 10%. Consider reducing discretionary spending.")

        return {
            "report_period": current_month_str,
            "previous_period": prev_month_str,
            "metrics": {
                "current_month": {
                    "income": float(curr_income),
                    "expense": float(curr_expense),
                    "savings": float(curr_savings),
                    "savings_rate": float(curr_savings_rate)
                },
                "previous_month": {
                    "income": float(prev_income),
                    "expense": float(prev_expense),
                    "savings": float(prev_savings),
                    "savings_rate": float(prev_savings_rate)
                },
                "changes": {
                    "income_change": float(income_change),
                    "expense_change": float(expense_change),
                    "savings_change": float(savings_change)
                }
            },
            "category_breakdown": curr_categories,
            "anomalies_detected": anomaly_summaries,
            "major_observations": observations
        }
