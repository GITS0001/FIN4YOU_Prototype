import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Tuple
from app.schemas.financial import Transaction, FinancialProfile, CopilotRequest, PaymentOption

class DataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        
    def load_events(self) -> List[Transaction]:
        path = self.data_dir / "financial_events.csv"
        if not path.exists():
            return []
            
        df = pd.read_csv(path)
        
        # Data Cleaning: Drop rows without amounts
        df = df.dropna(subset=['amount'])
        
        # Duplicate detection (exact duplicates)
        df = df.drop_duplicates()
        
        # Missing value handling for dates
        df['settlement_date'] = df['settlement_date'].fillna(df['event_date'])
        
        # Ensure status is filled
        df['status'] = df['status'].fillna('unknown')
        
        # Ensure flexibility is filled
        df['flexibility'] = df['flexibility'].fillna('variable')
        
        # Convert to dictionary for Pydantic validation
        records = df.to_dict(orient='records')
        
        transactions = []
        for rec in records:
            # Rename event_id to transaction_id to match our schema
            rec['transaction_id'] = rec.pop('event_id')
            try:
                transactions.append(Transaction(**rec))
            except Exception as e:
                print(f"Validation error for transaction {rec.get('transaction_id')}: {e}")
                
        return transactions

    def load_profiles(self) -> List[FinancialProfile]:
        path = self.data_dir / "financial_profiles.csv"
        if not path.exists():
            return []
            
        df = pd.read_csv(path)
        df = df.drop_duplicates()
        
        # Handle completely missing string columns
        list_cols = [
            'financial_priorities', 
            'expense_categories_to_protect', 
            'expense_categories_user_is_willing_to_reduce', 
            'expense_categories_user_is_willing_to_stop',
            'payment_methods_user_will_consider'
        ]
        for col in list_cols:
            if col not in df.columns:
                df[col] = ''
            df[col] = df[col].fillna('')
            
        # Convert any remaining NaNs (like in max_installment_months) to None
        df = df.where(pd.notnull(df), None)
        records = df.to_dict(orient='records')
        
        profiles = []
        for rec in records:
            try:
                profiles.append(FinancialProfile(**rec))
            except Exception as e:
                print(f"Validation error for profile {rec.get('user_id')}: {e}")
                
        return profiles

    def load_requests(self) -> List[CopilotRequest]:
        path = self.data_dir / "requests.csv"
        if not path.exists():
            return []
            
        df = pd.read_csv(path)
        df = df.drop_duplicates()
        
        records = df.to_dict(orient='records')
        requests = []
        for rec in records:
            try:
                requests.append(CopilotRequest(**rec))
            except Exception as e:
                print(f"Validation error for request {rec.get('request_id')}: {e}")
        return requests
