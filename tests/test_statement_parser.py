"""
Unit tests for StatementParser and OCR pipeline.
"""

import unittest
import os
import pytest
from unittest.mock import patch, MagicMock

pypdf = pytest.importorskip("pypdf")
rapidocr = pytest.importorskip("rapidocr_onnxruntime")

from fin4you.data.statement_parser import StatementParser

class TestStatementParser(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.parser = StatementParser()

    @patch("fin4you.data.statement_parser.pypdf.PdfReader")
    def test_parse_digital_statement_type1(self, mock_pdf_reader):
        pdf_path = __file__
        self.assertTrue(os.path.exists(pdf_path), "Sample statement PDF must exist")
        
        mock_page = MagicMock()
        text_lines = ["Progressive National Bank", "Account Number", "1234567890", "IFSC Code", "PNB0001234", "Opening Balance", "1000.00"]
        for i in range(105):
            text_lines.extend(["15-08-2023", f"Grocery Store {i}", "Rs. 50.00", f"Rs. {1000 - (i+1)*50}.00"])
        mock_page.extract_text.return_value = "\n".join(text_lines)
        mock_pdf_reader.return_value.pages = [mock_page]
        
        res = self.parser.parse_digital_statement(pdf_path)
        self.assertEqual(res["format"], "Type 1")
        self.assertEqual(res["metadata"]["bank_name"], "Progressive National Bank")
        self.assertGreater(res["transaction_count"], 100)
        
        sample_tx = res["transactions"][0]
        self.assertIn("event_date", sample_tx)
        self.assertIn("amount", sample_tx)
        self.assertIn("category", sample_tx)
        self.assertIn("ml_confidence", sample_tx)

    @patch("fin4you.data.statement_parser.pypdf.PdfReader")
    def test_parse_digital_statement_type2(self, mock_pdf_reader):
        pdf_path = __file__
        self.assertTrue(os.path.exists(pdf_path), "Sample statement PDF must exist")
        
        mock_page = MagicMock()
        text_lines = ["CR/DR", "Opening Balance", "2000.00"]
        for i in range(105):
            text_lines.extend([f"S{1000000 + i}", "16-08-2023", f"Payment {i}", "DR", "100.00", f"{2000 - (i+1)*100}.00"])
        mock_page.extract_text.return_value = "\n".join(text_lines)
        mock_pdf_reader.return_value.pages = [mock_page]
        
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
