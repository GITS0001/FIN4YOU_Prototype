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
            desc_str = str(row.get('description', '')).strip().lower()
            dir_raw = str(row.get('direction', 'debit')).strip().lower()
            raw_ev = row.get('event_type')
            is_refund = ('refund' in dir_raw) or (raw_ev and 'refund' in str(raw_ev).lower()) or ('refund' in desc_str and ('cr' in dir_raw or 'credit' in dir_raw or 'inflow' in dir_raw))

            if is_refund:
                canonical_dir = 'credit'
                canonical_ev = 'refund'
            elif ('cr' in dir_raw or 'credit' in dir_raw or 'inflow' in dir_raw or 'income' in dir_raw):
                canonical_dir = 'credit'
                canonical_ev = str(raw_ev).lower() if raw_ev and str(raw_ev).strip() else 'income'
            else:
                canonical_dir = 'debit'
                canonical_ev = str(raw_ev).lower() if raw_ev and str(raw_ev).strip() else 'expense'

            if raw_id and raw_id.strip() and raw_id != 'nan':
                tx_id = raw_id.strip()
            else:
                # Generate deterministic fingerprint based on transaction attributes
                ev_date_str = str(row['event_date'].date()) if hasattr(row['event_date'], 'date') else str(row['event_date'])
                amt_str = f"{float(row.get('amount', 0.0)):.2f}"
                fingerprint = f"{self.user_id}_{ev_date_str}_{amt_str}_{desc_str}_{canonical_ev}_{canonical_dir}"
                tx_id = f"tx_{hashlib.sha256(fingerprint.encode('utf-8')).hexdigest()[:16]}"

            t = Transaction(
                transaction_id=tx_id,
                user_id=self.user_id,
                event_type=canonical_ev,
                description=str(row.get('description', 'Unknown')),
                category=str(row.get('category', 'Uncategorized')),
                direction=canonical_dir,
                amount=float(row.get('amount', 0.0)),
                currency=str(row.get('currency', 'INR')),
                event_date=row['event_date'].date(),
                settlement_date=None,
                status="COMPLETED",
                flexibility=str(row.get('flexibility', 'variable'))
            )
            transactions.append(t)

        return transactions, metrics

    def parse_pdf(self, file_content: bytes) -> Tuple[List[Transaction], Dict[str, Any]]:
        import io
        import re
        from pypdf import PdfReader

        try:
            reader = PdfReader(io.BytesIO(file_content))
        except Exception as e:
            raise ValueError("Failed to read PDF file. It might be encrypted or malformed.")
            
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        if not text.strip():
            # No text, might be scanned
            raise ValueError("No selectable text found in PDF. Scanned PDFs are not currently supported by this parser.")

        # Try to find transaction lines
        # E.g. "2023-10-05 Groceries 300.00" or "05/10/2023 Salary 5000.00 CR"
        # Since layouts vary wildly, we'll do a simple heuristic for demonstration.
        lines = text.split('\n')
        transactions_data = []
        
        # Regex for statement lines with two amounts (Amount and Running Balance)
        # e.g., "01/04/2025 NEFT DR/SALARY/RAHUL MEHTA S000001 12000.00 400500.00"
        two_amt_pattern = re.compile(
            r'^(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4})\s+(.+?)\s+([\d,]+\.\d{2})\s*(CR|DR|credit|debit)?\s+([\d,]+\.\d{2})\s*(CR|DR|credit|debit)?$',
            re.IGNORECASE
        )
        # Regex for statement lines with a single amount
        single_amt_pattern = re.compile(
            r'^(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4})\s+(.+?)\s+([\d,]+\.\d{2})\s*(CR|DR|credit|debit)?$',
            re.IGNORECASE
        )

        for line in lines:
            line = line.strip()
            if not line:
                continue

            match_two = two_amt_pattern.match(line)
            if match_two:
                date_str = match_two.group(1)
                desc = match_two.group(2).strip()
                amt_str = match_two.group(3).replace(',', '')
                dir_tag = (match_two.group(4) or "").lower()

                # Infer direction from tag or description text
                desc_upper = desc.upper()
                if "cr" in dir_tag or any(k in desc_upper for k in ["CR/", "CREDIT", "NEFT CR", "RTGS CR", "IMPS CR", "INFLOW"]):
                    direction = "credit"
                else:
                    direction = "debit"

                # Clean trailing reference code from description if present
                clean_desc = re.sub(r'\s+S\d{4,}\b', '', desc, flags=re.IGNORECASE).strip()

                transactions_data.append({
                    "event_date": date_str,
                    "description": clean_desc,
                    "amount": float(amt_str),
                    "direction": direction
                })
                continue

            match_single = single_amt_pattern.match(line)
            if match_single:
                date_str = match_single.group(1)
                desc = match_single.group(2).strip()
                amt_str = match_single.group(3).replace(',', '')
                dir_tag = (match_single.group(4) or "").lower()

                desc_upper = desc.upper()
                if "cr" in dir_tag or any(k in desc_upper for k in ["CR/", "CREDIT", "NEFT CR", "RTGS CR", "IMPS CR", "INFLOW"]):
                    direction = "credit"
                else:
                    direction = "debit"

                clean_desc = re.sub(r'\s+S\d{4,}\b', '', desc, flags=re.IGNORECASE).strip()

                transactions_data.append({
                    "event_date": date_str,
                    "description": clean_desc,
                    "amount": float(amt_str),
                    "direction": direction
                })

        if not transactions_data:
            # Fallback scanner for date at line start and multiple amounts
            for line in lines:
                line = line.strip()
                date_m = re.match(r'^(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4})\s+(.+)$', line)
                if not date_m:
                    continue
                date_str = date_m.group(1)
                rest = date_m.group(2).strip()
                
                num_matches = list(re.finditer(r'([\d,]+\.\d{2})\s*(CR|DR|credit|debit)?', rest, re.IGNORECASE))
                if len(num_matches) >= 2:
                    # Penultimate number is the transaction amount; last number is running balance
                    tx_amt_m = num_matches[-2]
                    amt_str = tx_amt_m.group(1).replace(',', '')
                    dir_tag = (tx_amt_m.group(2) or "").lower()
                    desc = rest[:tx_amt_m.start()].strip()
                    clean_desc = re.sub(r'\s+S\d{4,}\b', '', desc, flags=re.IGNORECASE).strip()
                    desc_upper = clean_desc.upper()
                    direction = "credit" if ("cr" in dir_tag or any(k in desc_upper for k in ["CR/", "CREDIT", "NEFT CR", "RTGS CR", "IMPS CR", "INFLOW"])) else "debit"
                    transactions_data.append({
                        "event_date": date_str,
                        "description": clean_desc,
                        "amount": float(amt_str),
                        "direction": direction
                    })
                elif len(num_matches) == 1:
                    tx_amt_m = num_matches[0]
                    amt_str = tx_amt_m.group(1).replace(',', '')
                    dir_tag = (tx_amt_m.group(2) or "").lower()
                    desc = rest[:tx_amt_m.start()].strip()
                    clean_desc = re.sub(r'\s+S\d{4,}\b', '', desc, flags=re.IGNORECASE).strip()
                    desc_upper = clean_desc.upper()
                    direction = "credit" if ("cr" in dir_tag or any(k in desc_upper for k in ["CR/", "CREDIT", "NEFT CR", "RTGS CR", "IMPS CR", "INFLOW"])) else "debit"
                    transactions_data.append({
                        "event_date": date_str,
                        "description": clean_desc,
                        "amount": float(amt_str),
                        "direction": direction
                    })

        if not transactions_data:
            # Multi-line fallback: Date -> Description -> Amount -> Balance
            # e.g., 15-08-2023 \n Grocery Store 0 \n Rs. 50.00 \n Rs. 950.00
            for i in range(len(lines) - 3):
                l1 = lines[i].strip()
                l2 = lines[i+1].strip()
                l3 = lines[i+2].strip()
                if re.match(r'^(\d{2}-\d{2}-\d{4}|\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})$', l1):
                    if l3.startswith('Rs.') or re.match(r'^[\d,]+\.\d{2}$', l3):
                        amt_str = l3.replace('Rs.', '').replace(',', '').strip()
                        try:
                            amt = float(amt_str)
                            direction = "debit" 
                            transactions_data.append({
                                "event_date": l1,
                                "description": l2,
                                "amount": amt,
                                "direction": direction
                            })
                        except ValueError:
                            pass

        if not transactions_data:
            raise ValueError("Could not extract any transactions from the PDF text. Layout may not be supported.")

        # Convert to DataFrame
        df = pd.DataFrame(transactions_data)
        
        # The pipeline expects certain columns to exist, so ensure we have them
        if 'event_type' not in df.columns:
            df['event_type'] = df['direction'].apply(lambda x: 'income' if x == 'credit' else 'expense')
            
        # Apply ML Data Quality Pipeline
        cleaned_df, metrics = self.pipeline.process(df)

        transactions = []
        for _, row in cleaned_df.iterrows():
            raw_id = str(row.get('transaction_id') or row.get('event_id') or '')
            desc_raw = str(row.get('description', '')).strip()
            # Clean any leading date that might have leaked into description
            clean_desc_str = re.sub(r'^\d{2}[-/]\d{2}[-/]\d{4}\s+', '', desc_raw).strip()
            desc_str = clean_desc_str.lower()

            dir_raw = str(row.get('direction', 'debit')).strip().lower()
            raw_ev = row.get('event_type')
            is_refund = ('refund' in dir_raw) or (raw_ev and 'refund' in str(raw_ev).lower()) or ('refund' in desc_str and ('cr' in dir_raw or 'credit' in dir_raw or 'inflow' in dir_raw))

            if is_refund:
                canonical_dir = 'credit'
                canonical_ev = 'refund'
            elif ('cr' in dir_raw or 'credit' in dir_raw or 'inflow' in dir_raw or 'income' in dir_raw):
                canonical_dir = 'credit'
                canonical_ev = str(raw_ev).lower() if raw_ev and str(raw_ev).strip() else 'income'
            else:
                canonical_dir = 'debit'
                canonical_ev = str(raw_ev).lower() if raw_ev and str(raw_ev).strip() else 'expense'

            if raw_id and raw_id.strip() and raw_id != 'nan':
                tx_id = raw_id.strip()
            else:
                ev_date_str = str(row['event_date'].date()) if hasattr(row['event_date'], 'date') else str(row['event_date'])
                amt_str = f"{float(row.get('amount', 0.0)):.2f}"
                fingerprint = f"{self.user_id}_{ev_date_str}_{amt_str}_{desc_str}_{canonical_ev}_{canonical_dir}"
                tx_id = f"tx_{hashlib.sha256(fingerprint.encode('utf-8')).hexdigest()[:16]}"

            t = Transaction(
                transaction_id=tx_id,
                user_id=self.user_id,
                event_type=canonical_ev,
                description=clean_desc_str if clean_desc_str else "Unknown",
                category=str(row.get('category', 'Uncategorized')),
                direction=canonical_dir,
                amount=float(row.get('amount', 0.0)),
                currency=str(row.get('currency', 'INR')),
                event_date=row['event_date'].date(),
                settlement_date=None,
                status="COMPLETED",
                flexibility=str(row.get('flexibility', 'variable'))
            )
            transactions.append(t)

        return transactions, metrics
