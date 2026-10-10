"""
Data loading and normalization module for FIN4YOU.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
from fin4you.config import PROTOTYPE_DIR

def load_profiles(filepath: Optional[Path] = None) -> pd.DataFrame:
    path = filepath or (PROTOTYPE_DIR / "financial_profiles.csv")
    df = pd.read_csv(path)
    return df

def load_events(filepath: Optional[Path] = None, handle_missing: bool = True) -> pd.DataFrame:
    path = filepath or (PROTOTYPE_DIR / "financial_events.csv")
    df = pd.read_csv(path)
    df['event_date'] = pd.to_datetime(df['event_date'])
    df['settlement_date'] = pd.to_datetime(df['settlement_date'])
    
    if handle_missing:
        # If amount is NaN, for event_253 (salary) fill with regular salary baseline 4365000.0 IDR
        mask_missing_amount = df['amount'].isnull()
        if mask_missing_amount.any():
            # Fill known baseline salary if category is salary
            df.loc[mask_missing_amount & (df['category'] == 'salary'), 'amount'] = 4365000.0
            # Otherwise fill median of user category
            for idx in df[df['amount'].isnull()].index:
                u = df.loc[idx, 'user_id']
                cat = df.loc[idx, 'category']
                med = df[(df['user_id'] == u) & (df['category'] == cat)]['amount'].median()
                df.loc[idx, 'amount'] = med if not np.isnan(med) else 0.0
                
    return df

def load_requests(filepath: Optional[Path] = None) -> pd.DataFrame:
    path = filepath or (PROTOTYPE_DIR / "requests.csv")
    df = pd.read_csv(path)
    df['request_date'] = pd.to_datetime(df['request_date'])
    df['desired_completion_date'] = pd.to_datetime(df['desired_completion_date'])
    return df

def load_sample_requests(filepath: Optional[Path] = None) -> pd.DataFrame:
    path = filepath or (PROTOTYPE_DIR / "sample_requests.csv")
    df = pd.read_csv(path)
    df['request_date'] = pd.to_datetime(df['request_date'])
    df['desired_completion_date'] = pd.to_datetime(df['desired_completion_date'])
    return df

def load_payment_options(filepath: Optional[Path] = None) -> pd.DataFrame:
    path = filepath or (PROTOTYPE_DIR / "request_payment_options.csv")
    df = pd.read_csv(path)
    df['first_payment_date'] = pd.to_datetime(df['first_payment_date'])
    return df

def load_exchange_rates(filepath: Optional[Path] = None) -> pd.DataFrame:
    path = filepath or (PROTOTYPE_DIR / "exchange_rates.csv")
    df = pd.read_csv(path)
    df['rate_date'] = pd.to_datetime(df['rate_date'])
    return df

def load_messages(filepath: Optional[Path] = None) -> pd.DataFrame:
    path = filepath or (PROTOTYPE_DIR / "messages.csv")
    df = pd.read_csv(path)
    df['sent_at'] = pd.to_datetime(df['sent_at'])
    return df
