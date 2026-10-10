"""
Deterministic Financial Metrics Engine for FIN4YOU.
Implements the exact mathematical formulas specified in formula_sheet.docx.
No LLM estimation; pure Python, NumPy, and Pandas calculations.
"""

import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

ESSENTIAL_CATEGORIES = {
    'rent', 'housing', 'utilities', 'groceries', 'debt_repayment',
    'insurance', 'healthcare', 'education', 'family_support'
}

DISCRETIONARY_CATEGORIES = {
    'dining', 'entertainment', 'shopping', 'streaming',
    'music_subscription', 'delivery_membership', 'gym', 'cloud_storage'
}

def calculate_basic_financial_state(df_events: pd.DataFrame, days_elapsed: Optional[int] = None) -> Dict[str, Any]:
    """
    Section 1: Basic Financial State & Section 7: Essential vs Discretionary
    """
    if df_events.empty:
        return {
            "total_income": 0.0,
            "total_expenses": 0.0,
            "net_cash_flow": 0.0,
            "monthly_savings": 0.0,
            "savings_rate_pct": 0.0,
            "expense_ratio_pct": 0.0,
            "essential_expenses": 0.0,
            "discretionary_expenses": 0.0,
            "discretionary_ratio_pct": 0.0,
            "free_cash_flow": 0.0
        }
        
    income = float(df_events[df_events['direction'] == 'credit']['amount'].sum())
    expenses = float(df_events[df_events['direction'] == 'debit']['amount'].sum())
    net_cash_flow = income - expenses
    
    # Estimate months
    if days_elapsed and days_elapsed > 0:
        months = max(1.0, days_elapsed / 30.4375)
    elif 'event_date' in df_events.columns and len(df_events) > 1:
        dates = pd.to_datetime(df_events['event_date'])
        delta_days = (dates.max() - dates.min()).days + 1
        months = max(1.0, delta_days / 30.4375)
    else:
        months = 1.0
        
    monthly_income = income / months
    monthly_expenses = expenses / months
    monthly_savings = monthly_income - monthly_expenses
    savings_rate = (monthly_savings / monthly_income * 100.0) if monthly_income > 0 else 0.0
    expense_ratio = (monthly_expenses / monthly_income * 100.0) if monthly_income > 0 else 0.0
    
    # Essential vs Discretionary
    debit_df = df_events[df_events['direction'] == 'debit']
    essential_mask = debit_df['category'].isin(ESSENTIAL_CATEGORIES)
    essential_expenses = float(debit_df[essential_mask]['amount'].sum())
    discretionary_expenses = float(debit_df[~essential_mask]['amount'].sum())
    
    monthly_essential = essential_expenses / months
    monthly_discretionary = discretionary_expenses / months
    discretionary_ratio = (monthly_discretionary / monthly_income * 100.0) if monthly_income > 0 else 0.0
    
    # Debt payments
    debt_payments = float(debit_df[debit_df['category'] == 'debt_repayment']['amount'].sum()) / months
    free_cash_flow = monthly_income - monthly_essential - debt_payments
    
    return {
        "total_income": round(income, 2),
        "total_expenses": round(expenses, 2),
        "monthly_income": round(monthly_income, 2),
        "monthly_expenses": round(monthly_expenses, 2),
        "net_cash_flow": round(net_cash_flow, 2),
        "monthly_savings": round(monthly_savings, 2),
        "savings_rate_pct": round(savings_rate, 2),
        "expense_ratio_pct": round(expense_ratio, 2),
        "essential_expenses": round(essential_expenses, 2),
        "monthly_essential": round(monthly_essential, 2),
        "discretionary_expenses": round(discretionary_expenses, 2),
        "monthly_discretionary": round(monthly_discretionary, 2),
        "discretionary_ratio_pct": round(discretionary_ratio, 2),
        "free_cash_flow": round(free_cash_flow, 2)
    }

def calculate_category_spending(df_events: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Section 2: Category Spending breakdown
    """
    debits = df_events[df_events['direction'] == 'debit']
    total_debit = debits['amount'].sum()
    if total_debit == 0:
        return []
        
    dates = pd.to_datetime(df_events['event_date']) if 'event_date' in df_events.columns else None
    num_days = max(1, (dates.max() - dates.min()).days + 1) if dates is not None and len(dates) > 1 else 30
    
    breakdown = []
    for cat, grp in debits.groupby('category'):
        cat_spend = float(grp['amount'].sum())
        cat_pct = (cat_spend / total_debit * 100.0)
        txn_count = len(grp)
        avg_txn = cat_spend / txn_count if txn_count > 0 else 0.0
        daily_spend = cat_spend / num_days
        
        breakdown.append({
            "category": cat,
            "total_spend": round(cat_spend, 2),
            "percentage_of_total": round(cat_pct, 2),
            "transaction_count": txn_count,
            "average_transaction": round(avg_txn, 2),
            "average_daily_spend": round(daily_spend, 2),
            "is_essential": cat in ESSENTIAL_CATEGORIES
        })
        
    breakdown.sort(key=lambda x: x['total_spend'], reverse=True)
    return breakdown

def calculate_loan_emi(
    principal: float,
    annual_interest_rate_pct: float,
    tenure_years: float,
    payments_made_k: int = 0
) -> Dict[str, float]:
    """
    Section 4: Loan & EMI Calculations
    r = Annual Rate / (12 * 100)
    n = Tenure * 12
    EMI = P * [r(1+r)^n] / [(1+r)^n - 1]
    Remaining Balance B_k = P(1+r)^k - EMI * [(1+r)^k - 1] / r
    """
    p = float(principal)
    r = float(annual_interest_rate_pct) / (12.0 * 100.0)
    n = int(tenure_years * 12)
    k = int(payments_made_k)
    
    if r == 0:
        emi = p / n if n > 0 else 0.0
        total_payment = p
        total_interest = 0.0
        rem_balance = max(0.0, p - emi * k)
    else:
        numerator = r * math.pow(1.0 + r, n)
        denominator = math.pow(1.0 + r, n) - 1.0
        emi = p * (numerator / denominator)
        total_payment = emi * n
        total_interest = total_payment - p
        
        # Remaining balance after k payments
        rem_balance = p * math.pow(1.0 + r, k) - emi * (math.pow(1.0 + r, k) - 1.0) / r
        rem_balance = max(0.0, rem_balance)
        
    return {
        "principal": round(p, 2),
        "monthly_interest_rate": round(r, 6),
        "total_payments_n": n,
        "payments_made_k": k,
        "monthly_emi": round(emi, 2),
        "total_loan_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "remaining_balance": round(rem_balance, 2)
    }

def calculate_financial_health_metrics(
    df_events: pd.DataFrame,
    current_liquid_savings: float,
    monthly_debt_emi: Optional[float] = None
) -> Dict[str, Any]:
    """
    Section 15: Financial Health Metrics to Display (separate transparent metrics)
    """
    state = calculate_basic_financial_state(df_events)
    monthly_income = state["monthly_income"]
    monthly_essential = state["monthly_essential"]
    
    # 1. Savings Rate (%)
    savings_rate = state["savings_rate_pct"]
    
    # 2. Expense Ratio (%)
    expense_ratio = state["expense_ratio_pct"]
    
    # 3. EMI Burden & DTI (%)
    debit_df = df_events[df_events['direction'] == 'debit']
    if monthly_debt_emi is not None:
        emi_val = monthly_debt_emi
    else:
        debt_txns = debit_df[debit_df['category'] == 'debt_repayment']
        emi_val = float(debt_txns['amount'].mean()) if not debt_txns.empty else 0.0
        
    emi_burden = (emi_val / monthly_income * 100.0) if monthly_income > 0 else 0.0
    
    # 4. Emergency Fund Coverage (Months)
    emergency_months = (current_liquid_savings / monthly_essential) if monthly_essential > 0 else 999.0
    
    # 5. Recurring Obligation Ratio (%)
    fixed_mask = debit_df['flexibility'] == 'fixed'
    fixed_monthly = float(debit_df[fixed_mask]['amount'].sum()) / max(1.0, state["total_income"] / monthly_income if monthly_income > 0 else 1.0)
    recurring_obligation_ratio = (fixed_monthly / monthly_income * 100.0) if monthly_income > 0 else 0.0
    
    return {
        "savings_rate_pct": round(savings_rate, 2),
        "expense_ratio_pct": round(expense_ratio, 2),
        "emi_burden_pct": round(emi_burden, 2),
        "emergency_coverage_months": round(emergency_months, 2),
        "recurring_obligation_ratio_pct": round(recurring_obligation_ratio, 2),
        "monthly_income": state["monthly_income"],
        "monthly_expenses": state["monthly_expenses"],
        "monthly_essential": state["monthly_essential"],
        "monthly_discretionary": state["monthly_discretionary"],
        "current_liquid_savings": round(current_liquid_savings, 2)
    }

def detect_transaction_anomalies(
    df_events: pd.DataFrame,
    z_threshold: float = 2.5
) -> List[Dict[str, Any]]:
    """
    Section 13: Anomaly Detection using Population Z-Scores per category
    Z = (x - mu) / sigma
    """
    debits = df_events[df_events['direction'] == 'debit'].copy()
    anomalies = []
    
    for cat, grp in debits.groupby('category'):
        if len(grp) < 3:
            continue
        amounts = grp['amount'].values
        mu = np.mean(amounts)
        sigma = np.std(amounts)
        if sigma == 0:
            continue
            
        for idx, row in grp.iterrows():
            x = row['amount']
            z = (x - mu) / sigma
            if abs(z) >= z_threshold:
                anomalies.append({
                    "event_id": row.get('event_id', str(idx)),
                    "category": cat,
                    "description": row.get('description', ''),
                    "amount": round(float(x), 2),
                    "category_mean": round(float(mu), 2),
                    "category_std": round(float(sigma), 2),
                    "z_score": round(float(z), 2),
                    "severity": "critical" if abs(z) >= 3.5 else "warning",
                    "event_date": str(row.get('event_date', ''))
                })
                
    anomalies.sort(key=lambda a: abs(a['z_score']), reverse=True)
    return anomalies
