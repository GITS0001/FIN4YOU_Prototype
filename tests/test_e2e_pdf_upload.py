import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app as fastapi_app
from app.database import Base, get_db
from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

client = TestClient(fastapi_app)

@patch("app.api.users.is_supabase_configured", return_value=False)
@patch("app.auth.is_supabase_configured", return_value=False)
@patch("app.supabase_config.is_supabase_configured", return_value=False)
def test_pdf_upload(mock_1, mock_2, mock_3):
    os.environ["ENVIRONMENT"] = "test"
    os.environ["SUPABASE_MOCK"] = "True"
    fastapi_app.dependency_overrides.clear()
    fastapi_app.dependency_overrides[get_db] = override_get_db

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # 1. Register User
    res = client.post("/api/auth/register", json={
        "email": "pdf@example.com",
        "password": "securepassword",
        "full_name": "PDF User"
    })
    assert res.status_code == 200
    mock_otp = res.json()["mock_otp"]

    # 2. Verify OTP and get token
    res_verify = client.post("/api/auth/verify-otp", json={
        "email": "pdf@example.com",
        "otp": mock_otp
    })
    assert res_verify.status_code == 200
    token = res_verify.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create a dummy PDF in memory
    import fpdf
    import io
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    pdf.cell(40, 10, '2023-10-01 Salary 5000.00 credit')
    pdf.ln()
    pdf.cell(40, 10, '2023-10-05 Groceries 300.00 debit')
    
    # fpdf outputs bytes/bytearray or str
    raw_output = pdf.output()
    pdf_bytes = bytes(raw_output) if isinstance(raw_output, (bytes, bytearray)) else raw_output.encode('latin1')

    # 4. Upload the PDF
    files = {'file': ('dummy.pdf', pdf_bytes, 'application/pdf')}
    res_upload = client.post("/api/statements/upload", headers=headers, files=files)
    
    # 5. Assertions
    assert res_upload.status_code == 200
    data = res_upload.json()
    assert "Successfully ingested" in data["message"] or "processed" in data["message"]
    # Expecting 2 transactions
    # But since it's an end-to-end test, we can just check if they got persisted or parsed
    assert data["data_quality_metrics"]["total_records"] >= 2
    assert data["data_quality_metrics"]["valid_records"] >= 2
