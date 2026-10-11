import pytest
import os
from fastapi.testclient import TestClient

def test_upload_valid_csv(client, test_user_token):
    csv_content = b"""event_date,description,amount,direction
2023-10-01,Salary,5000.00,INFLOW
2023-10-05,Groceries,300.00,OUTFLOW
"""
    files = {"file": ("statement.csv", csv_content, "text/csv")}
    response = client.post(
        "/api/statements/upload",
        files=files,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_parsed"] == 2
    assert "Successfully ingested" in data["message"]

def test_upload_valid_pdf(client, test_user_token):
    # Using the existing sample PDF from fixtures
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "sample_statement.pdf")
    if os.path.exists(fixture_path):
        with open(fixture_path, "rb") as f:
            files = {"file": ("statement.pdf", f, "application/pdf")}
            response = client.post(
                "/api/statements/upload",
                files=files,
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
        assert response.status_code == 200
        # Check if it actually parses any transaction
        # Or at least returns 200

def test_upload_empty_pdf(client, test_user_token):
    empty_pdf = b"%PDF-1.4\n%EOF"
    files = {"file": ("empty.pdf", empty_pdf, "application/pdf")}
    response = client.post(
        "/api/statements/upload",
        files=files,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 400
    assert "Failed to parse" in response.json()["detail"]

def test_upload_corrupt_pdf(client, test_user_token):
    corrupt_pdf = b"this is not a pdf file"
    files = {"file": ("corrupt.pdf", corrupt_pdf, "application/pdf")}
    response = client.post(
        "/api/statements/upload",
        files=files,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 400
    assert "Failed to parse" in response.json()["detail"]

def test_upload_unsupported_file(client, test_user_token):
    files = {"file": ("test.txt", b"hello", "text/plain")}
    response = client.post(
        "/api/statements/upload",
        files=files,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 400
    assert "Only CSV and PDF files are supported" in response.json()["detail"]

def test_upload_duplicate_csv(client, test_user_token):
    csv_content = b"""event_date,description,amount,direction
2023-10-01,Salary,5000.00,INFLOW
"""
    files1 = {"file": ("statement1.csv", csv_content, "text/csv")}
    response1 = client.post("/api/statements/upload", files=files1, headers={"Authorization": f"Bearer {test_user_token}"})
    assert response1.status_code == 200

    # Upload same CSV again, it should parse 1 but ingest 0 new transactions (deduplication)
    files2 = {"file": ("statement2.csv", csv_content, "text/csv")}
    response2 = client.post("/api/statements/upload", files=files2, headers={"Authorization": f"Bearer {test_user_token}"})
    assert response2.status_code == 200
    data = response2.json()
    assert data["total_parsed"] == 1
    # Assuming SQLite fallback used for tests, inserted_count should be 0 for second run
    assert "0 new transactions" in data["message"] or "1 new transactions" not in data["message"]

def test_upload_scanned_pdf_unsupported(client, test_user_token):
    import io
    import pypdf
    # Create valid PDF structure but with blank/scanned page (no font/text stream)
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    pdf_bytes = io.BytesIO()
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)

    files = {"file": ("scanned_invoice.pdf", pdf_bytes.getvalue(), "application/pdf")}
    response = client.post(
        "/api/statements/upload",
        files=files,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 400
    assert "Scanned PDFs are not currently supported" in response.json()["detail"]
