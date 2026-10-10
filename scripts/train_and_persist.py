import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
from fin4you.data.loader import load_events
from fin4you.models.categorizer import TransactionCategorizer
from fin4you.config import CATEGORIZER_MODEL_PATH, CATEGORIZER_META_PATH

print("Loading events...")
df_events = load_events()
print(f"Loaded {len(df_events)} events.")

categorizer = TransactionCategorizer(C=5.0, random_state=42)
print("Fitting categorizer pipeline on full labeled dataset...")
categorizer.fit(df_events)

print("Persisting pipeline...")
categorizer.save()

print(f"Model saved to {CATEGORIZER_MODEL_PATH}")
print(f"Metadata saved to {CATEGORIZER_META_PATH}")
print("Training metadata:", categorizer.metadata)

# Verification inference
test_sample = "Apartment rent transfer"
pred = categorizer.predict_single(test_sample, direction='debit', event_type='expense')
print(f"\nVerification on '{test_sample}':\n", pred)
