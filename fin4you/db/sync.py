"""
Database Synchronization Module for FIN4YOU.
Populates SQLite fin4you.db with transactions, profiles, and ML prediction scores.
"""

import sys
import os
import sqlite3
import pandas as pd
from typing import Optional
from pathlib import Path

from fin4you.config import DB_PATH
from fin4you.data.loader import load_events, load_profiles, load_requests
from fin4you.models.categorizer import TransactionCategorizer

def sync_database(db_path: Optional[Path] = None) -> int:
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    print(f"Connecting to database: {path}")
    
    # 1. Load data
    events = load_events()
    profiles = load_profiles()
    requests = load_requests()
    
    # 2. Run ML categorizer to get confidence and status
    categorizer = TransactionCategorizer.load()
    ml_preds = categorizer.predict_records(events)
    
    events['ml_confidence'] = ml_preds['ml_confidence']
    events['ml_status'] = ml_preds['ml_status']
    events['ml_confidence_level'] = ml_preds['ml_confidence_level']
    
    # 3. Clear existing transactions and insert
    cursor.execute("DELETE FROM transactions;")
    
    insert_sql = """
    INSERT INTO transactions (
        transaction_id, user_id, event_type, description, category,
        direction, amount, currency, event_date, settlement_date,
        status, flexibility, ml_confidence, ml_status, ml_confidence_level
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    records = []
    for _, row in events.iterrows():
        records.append((
            str(row.get('event_id', '')),
            str(row.get('user_id', '')),
            str(row.get('event_type', '')),
            str(row.get('description', '')),
            str(row.get('category', '')),
            str(row.get('direction', '')),
            float(row.get('amount', 0.0)),
            str(row.get('currency', '')),
            str(row.get('event_date', '')),
            str(row.get('settlement_date', '')),
            str(row.get('status', '')),
            str(row.get('flexibility', '')),
            float(row.get('ml_confidence', 1.0)),
            str(row.get('ml_status', 'confirmed')),
            str(row.get('ml_confidence_level', 'high'))
        ))
        
    cursor.executemany(insert_sql, records)
    
    # 4. Sync profiles
    cursor.execute("DELETE FROM profiles WHERE user_id > 1;") # Preserve existing test profile
    for _, prof in profiles.iterrows():
        # Check if profile already exists
        cursor.execute("SELECT id FROM profiles WHERE full_name = ?", (prof['user_id'],))
        row = cursor.fetchone()
        if not row:
            cursor.execute("""
            INSERT INTO profiles (
                user_id, full_name, age, marital_status, dependents, occupation,
                city_tier, home_currency, current_available_balance, minimum_balance_to_keep,
                financial_priorities, expense_categories_to_protect,
                expense_categories_user_is_willing_to_reduce, expense_categories_user_is_willing_to_stop,
                payment_methods_user_will_consider, max_installment_months
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                1, # linked to user id 1
                str(prof['user_id']),
                "30", "Single", "0", "Professional", "Tier 1",
                str(prof['home_currency']),
                float(prof['current_available_balance']),
                float(prof['minimum_balance_to_keep']),
                str(prof.get('financial_priorities', '')),
                str(prof.get('expense_categories_to_protect', '')),
                str(prof.get('expense_categories_user_is_willing_to_reduce', '')),
                str(prof.get('expense_categories_user_is_willing_to_stop', '')),
                str(prof.get('payment_methods_user_will_consider', '')),
                int(prof['max_installment_months']) if pd.notnull(prof.get('max_installment_months')) else 12
            ))
            
    conn.commit()
    count = cursor.execute("SELECT count(*) FROM transactions;").fetchone()[0]
    conn.close()
    print(f"Successfully synchronized {count} transactions into SQLite database.")
    return count

if __name__ == '__main__':
    sync_database()
