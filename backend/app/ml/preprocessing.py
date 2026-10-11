import pandas as pd
from typing import Dict, Any, Tuple
from datetime import datetime
import numpy as np

class DataQualityPipeline:
    """
    A robust data quality pipeline for financial transactions.
    Handles missing values, duplicate detection, date normalization,
    and generates data quality metrics.
    """
    def __init__(self):
        self.metrics = {
            "total_records": 0,
            "valid_records": 0,
            "invalid_records": 0,
            "missing_values": 0,
            "duplicates": 0,
            "categories_discovered": [],
            "date_range": None
        }

    def process(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        if df.empty:
            return df, self.metrics

        self.metrics["total_records"] = len(df)

        # Standardize column names to lowercase and strip whitespace
        df.columns = [str(c).lower().strip().replace(' ', '_') for c in df.columns]

        # Check for separate debit/credit or withdrawal/deposit columns
        debit_cols = [c for c in df.columns if any(k in c for k in ['debit', 'withdrawal', 'dr']) and 'dr_cr' not in c and 'cr_dr' not in c]
        credit_cols = [c for c in df.columns if any(k in c for k in ['credit', 'deposit', 'cr']) and 'dr_cr' not in c and 'cr_dr' not in c]

        if 'amount' not in df.columns and (debit_cols or credit_cols):
            deb_col = debit_cols[0] if debit_cols else None
            cred_col = credit_cols[0] if credit_cols else None
            
            amounts = []
            directions = []
            for _, r in df.iterrows():
                d_str = str(r.get(deb_col, '0') if deb_col else '0').replace(',', '').replace('(', '-').replace(')', '').strip()
                c_str = str(r.get(cred_col, '0') if cred_col else '0').replace(',', '').replace('(', '-').replace(')', '').strip()
                d_val = pd.to_numeric(d_str, errors='coerce') or 0.0
                c_val = pd.to_numeric(c_str, errors='coerce') or 0.0
                
                if c_val > 0:
                    amounts.append(c_val)
                    directions.append('credit')
                elif d_val > 0:
                    amounts.append(d_val)
                    directions.append('debit')
                else:
                    amounts.append(0.0)
                    directions.append('debit')
            df['amount'] = amounts
            df['direction'] = directions

        # Required columns (or fallbacks)
        if 'amount' not in df.columns:
            amount_cols = [c for c in df.columns if 'amount' in c or 'value' in c]
            if amount_cols:
                df['amount'] = df[amount_cols[0]]
            else:
                raise ValueError("Could not find an 'amount' column in the dataset")

        if 'date' not in df.columns and 'event_date' not in df.columns:
            date_cols = [c for c in df.columns if 'date' in c or 'time' in c or 'timestamp' in c]
            if date_cols:
                df['event_date'] = df[date_cols[0]]
            else:
                raise ValueError("Could not find a 'date' column in the dataset")
        elif 'date' in df.columns and 'event_date' not in df.columns:
            df['event_date'] = df['date']

        # Ensure description
        if 'description' not in df.columns:
            desc_cols = [c for c in df.columns if 'desc' in c or 'merchant' in c or 'name' in c or 'particulars' in c]
            df['description'] = df[desc_cols[0]] if desc_cols else "Unknown"

        # 1. Missing values
        missing_desc = df['description'].isna().sum()
        self.metrics["missing_values"] += int(missing_desc)
        df['description'] = df['description'].fillna("Unknown Transaction")

        # Normalize amount to numeric: handle parenthesized negative (e.g. "(1,234.56)" -> "-1234.56")
        amount_series = df['amount'].astype(str).str.replace(r'\((.*?)\)', r'-\1', regex=True)
        # Strip currency symbols like ₹, Rs., Rs, INR, $, €
        amount_series = amount_series.str.replace(r'[₹$€]|rs\.?|inr', '', case=False, regex=True)
        # Strip commas and any non-numeric except minus and dot
        amount_series = amount_series.str.replace(r'[^\d.\-]', '', regex=True)
        df['amount'] = pd.to_numeric(amount_series, errors='coerce')
        invalid_amounts = df['amount'].isna().sum()
        self.metrics["invalid_records"] += int(invalid_amounts)
        df = df.dropna(subset=['amount'])

        # 2. Date parsing
        df['event_date'] = pd.to_datetime(df['event_date'], errors='coerce')
        invalid_dates = df['event_date'].isna().sum()
        self.metrics["invalid_records"] += int(invalid_dates)
        df = df.dropna(subset=['event_date'])

        # 3. Direction normalization
        direction_col = next((c for c in df.columns if c in ['direction', 'type', 'transaction_type', 'tx_type', 'dr_cr', 'cr_dr', 'mode']), None)
        
        if direction_col:
            def norm_dir(val):
                v = str(val).lower()
                if 'refund' in v: return 'refund'
                if 'cr' in v or 'credit' in v or 'inflow' in v or 'income' in v: return 'credit'
                return 'debit'
            df['direction'] = df[direction_col].apply(norm_dir)
        else:
            # Infer direction from amount sign or description
            def infer_dir(row):
                amt = row['amount']
                desc = str(row.get('description', '')).upper()
                if 'REFUND' in desc: return 'refund'
                if any(k in desc for k in ['NEFT CR', 'RTGS CR', 'IMPS CR', 'CR/', 'CREDIT']): return 'credit'
                if any(k in desc for k in ['NEFT DR', 'RTGS DR', 'IMPS DR', 'DR/', 'DEBIT', 'BILLPAY']): return 'debit'
                return 'credit' if amt > 0 else 'debit'
            df['direction'] = df.apply(infer_dir, axis=1)
            
        def norm_event(row):
            d = row['direction']
            desc = str(row.get('description', '')).upper()
            if d == 'refund' or ('REFUND' in desc and d in ['credit', 'refund']):
                return 'refund'
            return 'income' if d == 'credit' else 'expense'

        df['event_type'] = df.apply(norm_event, axis=1)

        # Make amounts absolute
        df['amount'] = df['amount'].abs()

        # 4. Deduplication
        # Consider a transaction duplicate if date, amount, and description are identical
        initial_count = len(df)
        df = df.drop_duplicates(subset=['event_date', 'amount', 'description'], keep='first')
        self.metrics["duplicates"] = initial_count - len(df)

        # Set default categories if missing
        if 'category' not in df.columns:
            df['category'] = 'Uncategorized'
        else:
            df['category'] = df['category'].fillna('Uncategorized')

        self.metrics["categories_discovered"] = df['category'].unique().tolist()

        # Provide date range
        min_date = df['event_date'].min()
        max_date = df['event_date'].max()
        self.metrics["date_range"] = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
        self.metrics["valid_records"] = len(df)

        return df, self.metrics
