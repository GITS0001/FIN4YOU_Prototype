"""
Unit tests for StatementParser and OCR pipeline.
"""

import unittest
import os
from fin4you.data.statement_parser import StatementParser

class TestStatementParser(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.parser = StatementParser()

    def test_parse_digital_statement_type1(self):
        pdf_path = "Indian-Bank-Statements/train/India_Bank_Statement_Digital_Type1/00001.pdf"
        self.assertTrue(os.path.exists(pdf_path), "Sample statement PDF must exist")
        res = self.parser.parse_digital_statement(pdf_path)
        self.assertEqual(res["format"], "Type 1")
        self.assertEqual(res["metadata"]["bank_name"], "Progressive National Bank")
        self.assertGreater(res["transaction_count"], 100)
        
        sample_tx = res["transactions"][0]
        self.assertIn("event_date", sample_tx)
        self.assertIn("amount", sample_tx)
        self.assertIn("category", sample_tx)
        self.assertIn("ml_confidence", sample_tx)

    def test_parse_digital_statement_type2(self):
        pdf_path = "Indian-Bank-Statements/train/India_Bank_Statement_Digital_Type2/00001.pdf"
        self.assertTrue(os.path.exists(pdf_path), "Sample statement PDF must exist")
        res = self.parser.parse_digital_statement(pdf_path)
        self.assertEqual(res["format"], "Type 2")
        self.assertGreater(res["transaction_count"], 100)

    def test_ocr_pay_slip_extraction(self):
        img_path = "data/media/images/image_01.png"
        self.assertTrue(os.path.exists(img_path), "image_01.png must exist")
        res = self.parser.parse_image_document(img_path)
        self.assertEqual(res["document_type"], "salary_payslip")
        self.assertIsNotNone(res["net_amount"])
        self.assertEqual(res["net_amount"], 4365000.0)

if __name__ == '__main__':
    unittest.main()
