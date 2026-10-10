import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import pypdf
import json
import re

pdf_path = "Indian-Bank-Statements/train/India_Bank_Statement_Digital_Type1/00001.pdf"
json_path = "Indian-Bank-Statements/train/India_Bank_Statement_Digital_Type1/00001.json"

with open(json_path, 'r', encoding='utf-8') as f:
    ground_truth = json.load(f)

print(f"Ground Truth Metadata:")
print(f"  Bank: {ground_truth.get('bank_name')}")
print(f"  Account: {ground_truth.get('account_number')}")
print(f"  Transactions count: {len(ground_truth.get('transactions', []))}")
print(f"  Sample GT txn: {ground_truth.get('transactions', [])[0]}")

reader = pypdf.PdfReader(pdf_path)
full_text = "\n".join([page.extract_text() or '' for page in reader.pages])

print(f"\nPDF pages: {len(reader.pages)}, extracted text length: {len(full_text)} chars")
lines = [l.strip() for l in full_text.split('\n') if l.strip()]
print(f"Total lines: {len(lines)}")
print("Sample lines (first 30):")
for i, l in enumerate(lines[:30]):
    print(f"  {i}: {l}")
