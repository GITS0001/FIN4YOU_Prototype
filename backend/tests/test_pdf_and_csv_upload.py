import unittest
import io
import pymupdf as fitz
from app.ingestion.parser import StatementParser
from app.ingestion.pdf_parser import PDFStatementParser
from app.schemas.financial import Transaction

class TestPDFAndCSVUpload(unittest.TestCase):

    def setUp(self):
        self.user_id = "test_user_999"
        self.parser = StatementParser(user_id=self.user_id)

    def test_01_valid_csv_parsing(self):
        csv_content = (
            "event_date,description,amount,direction,category\n"
            "2026-04-01,Salary Credit,75000.00,INFLOW,Income\n"
            "2026-04-05,Apartment Rent,18000.00,OUTFLOW,Rent & Housing\n"
        ).encode("utf-8")

        transactions, metrics = self.parser.parse_file(csv_content, "statement.csv")
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0].amount, 75000.00)
        self.assertEqual(transactions[0].direction, "INFLOW")
        self.assertEqual(transactions[1].amount, 18000.00)
        self.assertEqual(transactions[1].direction, "OUTFLOW")

    def test_02_valid_pdf_bank_statement_parsing(self):
        # Generate a synthetic multi-page bank statement PDF matching Setu Analyzer structure
        doc = fitz.open()
        
        # Page 1: Report Summary + Monthly Summary + Transactions
        page1 = doc.new_page()
        page1.insert_text((50, 40), "Bank Statement Analysis\nSummary\nTotal credits 18,42,000.00\nTotal debits 15,76,500.00\nNet cash flow 2,65,500.00\n")
        page1.insert_text((50, 150), "Monthly summary\nApr 2025 4,12,500.00 1,28,500.00 1,17,299.00 4,23,701.00\nMay 2025 4,23,701.00 1,42,500.00 1,06,449.00 4,59,752.00\n")
        page1.insert_text((50, 250), "Uncategorised — needs review\nDate Narration Amount\n01/04/2025 NEFT DR/SALARY/RAHUL MEHTA 12,000.00\n04/04/2025 NEFT CR/MERIDIAN RETAIL PVT LTD/INV-4523 26,500.00\n05/04/2025 ACH DR/OFFICE RENT/SKYLINE PROPERTIES 18,000.00\n")

        # Page 2: Transactions + Top Counterparties
        page2 = doc.new_page()
        page2.insert_text((50, 40), "Date Narration Amount\n13/04/2025 CASH DEPOSIT/CDM BRANCH COUNTER 23,500.00\n28/06/2025 INT.PD:SB INTEREST CREDIT 1,800.00\n30/03/2026 RTGS DR/PURCHASE/VERTEX SUPPLIES 1,38,982.00\n")
        page2.insert_text((50, 300), "Top counterparties\nParty Paid out Received Count\nGreenleaf Organics 0.00 4,63,000.00 11\nNorthstar Logistics 0.00 3,33,000.00 8\n")

        pdf_bytes = doc.tobytes()
        doc.close()

        transactions, metrics = self.parser.parse_file(pdf_bytes, "bank_statement.pdf")

        # Verify exact transactions extracted
        self.assertGreaterEqual(len(transactions), 6)
        
        # Verify direction detection
        dr_tx = next(t for t in transactions if "RAHUL MEHTA" in t.description)
        self.assertEqual(dr_tx.direction, "OUTFLOW")
        self.assertEqual(dr_tx.amount, 12000.00)

        cr_tx = next(t for t in transactions if "MERIDIAN RETAIL" in t.description)
        self.assertEqual(cr_tx.direction, "INFLOW")
        self.assertEqual(cr_tx.amount, 26500.00)

        # Verify Indian comma format parsing (1,38,982.00)
        rtgs_tx = next(t for t in transactions if "VERTEX SUPPLIES" in t.description)
        self.assertEqual(rtgs_tx.amount, 138982.00)

        # Verify summary sections (Monthly summary, Top counterparties) were NOT parsed as transactions
        for t in transactions:
            self.assertNotIn("Greenleaf Organics", t.description)
            self.assertNotIn("Total credits", t.description)

    def test_03_scanned_pdf_rejection(self):
        # Create an empty scanned image PDF without text layer
        doc = fitz.open()
        doc.new_page()
        pdf_bytes = doc.tobytes()
        doc.close()

        with self.assertRaises(ValueError) as ctx:
            self.parser.parse_file(pdf_bytes, "scanned_statement.pdf")
        self.assertIn("scanned document", str(ctx.exception).lower())

    def test_04_unsupported_file_extension(self):
        with self.assertRaises(ValueError) as ctx:
            self.parser.parse_file(b"test data", "statement.xlsx")
        self.assertIn("unsupported file type", str(ctx.exception).lower())

    def test_05_deduplication_fingerprint(self):
        doc = fitz.open()
        page = doc.new_page()
        # Same transaction printed twice in PDF
        page.insert_text((50, 40), "Date Narration Amount\n01/04/2025 NEFT DR/SALARY/RAHUL MEHTA 12,000.00\n01/04/2025 NEFT DR/SALARY/RAHUL MEHTA 12,000.00\n")
        pdf_bytes = doc.tobytes()
        doc.close()

        transactions, metrics = self.parser.parse_file(pdf_bytes, "dedup_test.pdf")
        self.assertEqual(len(transactions), 1)

if __name__ == "__main__":
    unittest.main()
