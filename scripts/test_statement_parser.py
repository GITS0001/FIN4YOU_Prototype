import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from fin4you.data.statement_parser import StatementParser

print("Initializing StatementParser with trained ML Categorizer...")
parser = StatementParser()

# Test 1: Digital Type 1 Statement
pdf_type1 = "Indian-Bank-Statements/train/India_Bank_Statement_Digital_Type1/00001.pdf"
print(f"\n--- 1. Parsing Digital Type 1 Statement: {pdf_type1} ---")
res_t1 = parser.parse_digital_statement(pdf_type1)
print(f"Bank Name: {res_t1['metadata'].get('bank_name')}")
print(f"Extracted transactions count: {res_t1['transaction_count']}")
if res_t1['transactions']:
    print("Sample extracted & ML-categorized transaction:")
    sample = res_t1['transactions'][0]
    print(f"  Date: {sample['event_date']}")
    print(f"  Description: {sample['description']}")
    print(f"  Amount: {sample['amount']} ({sample['direction']})")
    print(f"  Balance: {sample['balance']}")
    print(f"  Predicted Category: {sample.get('category')} (conf: {sample.get('ml_confidence')})")

# Test 2: Digital Type 2 Statement
pdf_type2 = "Indian-Bank-Statements/train/India_Bank_Statement_Digital_Type2/00001.pdf"
print(f"\n--- 2. Parsing Digital Type 2 Statement: {pdf_type2} ---")
res_t2 = parser.parse_digital_statement(pdf_type2)
print(f"Format: {res_t2['metadata'].get('format_type')}")
print(f"Extracted transactions count: {res_t2['transaction_count']}")
if res_t2['transactions']:
    print("Sample extracted & ML-categorized transaction:")
    sample = res_t2['transactions'][0]
    print(f"  Date: {sample['event_date']}")
    print(f"  Description: {sample['description']}")
    print(f"  Amount: {sample['amount']} ({sample['direction']})")
    print(f"  Balance: {sample['balance']}")
    print(f"  Predicted Category: {sample.get('category')} (conf: {sample.get('ml_confidence')})")

# Test 3: OCR on Pay Slip Image
img_path = "data/media/images/image_01.png"
print(f"\n--- 3. Running Deep OCR on Pay Slip Image: {img_path} ---")
res_ocr = parser.parse_image_document(img_path)
print(f"Document Type: {res_ocr['document_type']}")
print(f"Extracted Date: {res_ocr['date']}")
print(f"Extracted Net Salary: {res_ocr['net_amount']}")
print(f"Total lines read by OCR: {res_ocr['raw_lines_count']}")
