"""
AgamiAI Ground-Truth Validation for Statement Parser.
Compares parser extraction against ground-truth JSON files
from the Indian-Bank-Statements dataset.
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fin4you.data.statement_parser import StatementParser


def load_ground_truth(json_path: str) -> Dict[str, Any]:
    """Load ground-truth JSON for a statement."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_statement_type1(
    parser: StatementParser,
    pdf_path: str,
    json_path: str
) -> Dict[str, Any]:
    """Validate Type 1 digital statement against ground truth."""
    gt = load_ground_truth(json_path)
    result = parser.parse_digital_statement(pdf_path)

    gt_transactions = gt.get('transactions', [])
    parsed_transactions = result.get('transactions', [])

    gt_count = len(gt_transactions)
    parsed_count = len(parsed_transactions)

    # Check metadata
    metadata_checks = {
        "account_number_match": gt.get('account_number', '') == result['metadata'].get('account_number', ''),
        "currency_match": gt.get('currency', 'INR') == result['metadata'].get('currency', ''),
    }

    # Count matching amounts
    gt_amounts = set()
    for t in gt_transactions:
        amt = t.get('debit') or t.get('credit')
        if amt is not None:
            gt_amounts.add(round(float(amt), 2))

    parsed_amounts = set()
    for t in parsed_transactions:
        amt = t.get('amount')
        if amt is not None:
            parsed_amounts.add(round(float(amt), 2))

    amount_matches = len(gt_amounts & parsed_amounts)
    amount_recall = amount_matches / len(gt_amounts) if gt_amounts else 0.0

    return {
        "pdf_file": os.path.basename(pdf_path),
        "ground_truth_transactions": gt_count,
        "parsed_transactions": parsed_count,
        "extraction_rate": round(parsed_count / gt_count, 4) if gt_count > 0 else 0.0,
        "unique_amounts_in_gt": len(gt_amounts),
        "unique_amounts_parsed": len(parsed_amounts),
        "amount_matches": amount_matches,
        "amount_recall": round(amount_recall, 4),
        "metadata_checks": metadata_checks,
        "gt_opening_balance": gt.get('opening_balance'),
        "gt_closing_balance": gt.get('closing_balance'),
        "parsed_opening_balance": result['metadata'].get('opening_balance'),
        "parsed_closing_balance": result['metadata'].get('closing_balance'),
    }


def validate_statement_type2(
    parser: StatementParser,
    pdf_path: str,
    json_path: str
) -> Dict[str, Any]:
    """Validate Type 2 digital statement against ground truth."""
    gt = load_ground_truth(json_path)
    result = parser.parse_digital_statement(pdf_path)

    gt_transactions = gt.get('transactions', [])
    parsed_transactions = result.get('transactions', [])

    gt_count = len(gt_transactions)
    parsed_count = len(parsed_transactions)

    # Directional accuracy
    gt_debits = sum(1 for t in gt_transactions if t.get('debit') is not None)
    gt_credits = sum(1 for t in gt_transactions if t.get('credit') is not None)

    parsed_debits = sum(1 for t in parsed_transactions if t.get('direction') == 'debit')
    parsed_credits = sum(1 for t in parsed_transactions if t.get('direction') == 'credit')

    return {
        "pdf_file": os.path.basename(pdf_path),
        "ground_truth_transactions": gt_count,
        "parsed_transactions": parsed_count,
        "extraction_rate": round(parsed_count / gt_count, 4) if gt_count > 0 else 0.0,
        "gt_debits": gt_debits,
        "gt_credits": gt_credits,
        "parsed_debits": parsed_debits,
        "parsed_credits": parsed_credits,
        "format_detected": result.get("format", ""),
    }


def run_full_validation() -> Dict[str, Any]:
    """Run validation across multiple statements from the AgamiAI dataset."""
    base_dir = Path("Indian-Bank-Statements/train")
    type1_dir = base_dir / "India_Bank_Statement_Digital_Type1"
    type2_dir = base_dir / "India_Bank_Statement_Digital_Type2"

    parser = StatementParser()

    results = {
        "type1_validations": [],
        "type2_validations": [],
        "summary": {}
    }

    # Validate first 5 Type 1 statements
    type1_files = sorted([f for f in os.listdir(type1_dir) if f.endswith('.pdf')])[:5]
    for pdf_file in type1_files:
        pdf_path = str(type1_dir / pdf_file)
        json_file = pdf_file.replace('.pdf', '.json')
        json_path = str(type1_dir / json_file)

        if os.path.exists(json_path):
            try:
                validation = validate_statement_type1(parser, pdf_path, json_path)
                results["type1_validations"].append(validation)
                print(f"  Type1 {pdf_file}: {validation['parsed_transactions']}/{validation['ground_truth_transactions']} transactions (rate: {validation['extraction_rate']:.2%})")
            except Exception as e:
                print(f"  Type1 {pdf_file}: ERROR - {e}")
                results["type1_validations"].append({
                    "pdf_file": pdf_file,
                    "error": str(e)
                })

    # Validate first 5 Type 2 statements
    type2_files = sorted([f for f in os.listdir(type2_dir) if f.endswith('.pdf')])[:5]
    for pdf_file in type2_files:
        pdf_path = str(type2_dir / pdf_file)
        json_file = pdf_file.replace('.pdf', '.json')
        json_path = str(type2_dir / json_file)

        if os.path.exists(json_path):
            try:
                validation = validate_statement_type2(parser, pdf_path, json_path)
                results["type2_validations"].append(validation)
                print(f"  Type2 {pdf_file}: {validation['parsed_transactions']}/{validation['ground_truth_transactions']} transactions (rate: {validation['extraction_rate']:.2%})")
            except Exception as e:
                print(f"  Type2 {pdf_file}: ERROR - {e}")
                results["type2_validations"].append({
                    "pdf_file": pdf_file,
                    "error": str(e)
                })

    # Summary
    t1_rates = [v['extraction_rate'] for v in results['type1_validations'] if 'extraction_rate' in v]
    t2_rates = [v['extraction_rate'] for v in results['type2_validations'] if 'extraction_rate' in v]

    results["summary"] = {
        "type1_files_tested": len(results['type1_validations']),
        "type1_mean_extraction_rate": round(sum(t1_rates) / len(t1_rates), 4) if t1_rates else 0.0,
        "type2_files_tested": len(results['type2_validations']),
        "type2_mean_extraction_rate": round(sum(t2_rates) / len(t2_rates), 4) if t2_rates else 0.0,
    }

    return results


if __name__ == "__main__":
    print("=" * 70)
    print("AgamiAI Ground-Truth Statement Parser Validation")
    print("=" * 70)
    results = run_full_validation()
    print("\n--- Summary ---")
    print(f"Type 1 mean extraction rate: {results['summary']['type1_mean_extraction_rate']:.2%}")
    print(f"Type 2 mean extraction rate: {results['summary']['type2_mean_extraction_rate']:.2%}")

    # Save results
    import json as json_module
    output_path = "reports/ocr_validation_results.json"
    with open(output_path, 'w') as f:
        json_module.dump(results, f, indent=2, default=str)
    print(f"\nDetailed results saved to {output_path}")
