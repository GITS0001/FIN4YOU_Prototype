import pandas as pd
import uuid
import hashlib
from typing import List, Dict, Any, Tuple
from app.schemas.financial import Transaction
from app.ml.preprocessing import DataQualityPipeline

class StatementParser:
    """
    Parses generic CSV statements into the canonical Transaction schema,
    applying the DataQualityPipeline in the process.
    Uses deterministic deduplication fingerprinting so retried uploads
    do not create duplicate transactions.
    """
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.pipeline = DataQualityPipeline()

    def parse_csv(self, file_content: bytes) -> Tuple[List[Transaction], Dict[str, Any]]:
        from io import BytesIO
        df = pd.read_csv(BytesIO(file_content))

        # Apply ML Data Quality Pipeline
        cleaned_df, metrics = self.pipeline.process(df)

        transactions = []
        for _, row in cleaned_df.iterrows():
            # Check for existing ID in CSV
            raw_id = str(row.get('transaction_id') or row.get('event_id') or '')
            if raw_id and raw_id.strip() and raw_id != 'nan':
                tx_id = raw_id.strip()
            else:
                # Generate deterministic fingerprint based on transaction attributes
                ev_date_str = str(row['event_date'].date()) if hasattr(row['event_date'], 'date') else str(row['event_date'])
                amt_str = f"{float(row.get('amount', 0.0)):.2f}"
                desc_str = str(row.get('description', '')).strip().lower()
                dir_str = str(row.get('direction', '')).strip().upper()
                fingerprint = f"{self.user_id}_{ev_date_str}_{amt_str}_{desc_str}_{dir_str}"
                tx_id = f"tx_{hashlib.sha256(fingerprint.encode('utf-8')).hexdigest()[:16]}"

            t = Transaction(
                transaction_id=tx_id,
                user_id=self.user_id,
                event_type=row.get('event_type', 'expense' if row.get('direction') == 'OUTFLOW' else 'income'),
                description=str(row.get('description', 'Unknown')),
                category=str(row.get('category', 'Uncategorized')),
                direction=str(row.get('direction', 'OUTFLOW')),
                amount=float(row.get('amount', 0.0)),
                currency=str(row.get('currency', 'INR')),
                event_date=row['event_date'].date(),
                settlement_date=None,
                status="COMPLETED",
                flexibility=str(row.get('flexibility', 'variable'))
            )
            transactions.append(t)

        return transactions, metrics
