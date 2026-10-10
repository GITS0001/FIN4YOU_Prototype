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

        # Required columns (or fallbacks)
        if 'amount' not in df.columns:
            # Try to find something that looks like amount
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
        # Fill missing descriptions
        missing_desc = df['description'].isna().sum()
        self.metrics["missing_values"] += int(missing_desc)
        df['description'] = df['description'].fillna("Unknown Transaction")

        # Normalise amount to numeric
        df['amount'] = pd.to_numeric(df['amount'].replace(r'[^\d\.\-]', '', regex=True), errors='coerce')
        invalid_amounts = df['amount'].isna().sum()
        self.metrics["invalid_records"] += int(invalid_amounts)
        df = df.dropna(subset=['amount'])

        # 2. Date parsing
        df['event_date'] = pd.to_datetime(df['event_date'], errors='coerce')
        invalid_dates = df['event_date'].isna().sum()
        self.metrics["invalid_records"] += int(invalid_dates)
        df = df.dropna(subset=['event_date'])

        # 3. Direction normalization
        if 'direction' not in df.columns:
            # Infer direction from amount if direction column is missing
            df['direction'] = df['amount'].apply(lambda x: 'INFLOW' if x > 0 else 'OUTFLOW')
            df['event_type'] = df['amount'].apply(lambda x: 'income' if x > 0 else 'expense')

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
