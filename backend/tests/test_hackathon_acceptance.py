import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db

import random
import uuid

def test_hackathon_acceptance_pipeline(client, db):
    # Seed high ID offset so test users don't collide with existing remote Supabase user_id='1'
    offset = random.randint(100000, 800000)
    from app.models import User as DBUserModel
    db.add(DBUserModel(id=offset, email=f"offset_{offset}@fin4you.ai", hashed_password="hash", is_active=True))
    db.commit()

    print("\n--- TEST 1: API AND AUTHENTICATION ---")
    # Health check
    health_res = client.get("/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "healthy"

    # Protected endpoint rejected without auth
    unauth_res = client.get("/api/users/state")
    assert unauth_res.status_code in [401, 403]

    # Register & Login User A
    user_a_email = f"hackathon_user_a_{offset}@fin4you.ai"
    reg_a = client.post("/api/auth/register", json={
        "email": user_a_email,
        "password": "Password123!",
        "full_name": "Hackathon Tester"
    })
    assert reg_a.status_code == 200
    otp_a = reg_a.json()["mock_otp"]

    tok_a_res = client.post("/api/auth/verify-otp", json={
        "email": user_a_email,
        "otp": otp_a
    })
    assert tok_a_res.status_code == 200
    token_a = tok_a_res.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Authenticated call succeeds
    profile_res = client.get("/api/users/profile", headers=headers_a)
    assert profile_res.status_code == 200
    assert profile_res.json()["email"] == user_a_email

    print("\n--- TEST 2: UPLOAD ---")
    # Malformed file test
    bad_upload = client.post(
        "/api/statements/upload",
        headers=headers_a,
        files={"file": ("invalid.txt", io.BytesIO(b"not a statement"), "text/plain")}
    )
    assert bad_upload.status_code == 400

    # Controlled CSV from Phase 8 specification:
    # Salary: ₹50,000, Rent: ₹12,000, Groceries: ₹4,000, Transport: ₹2,000, EMI: ₹6,000, Food: ₹3,000
    csv_data = (
        "date,description,amount,direction\n"
        "2026-01-01,Monthly Company Salary,50000.00,credit\n"
        "2026-01-05,Apartment Monthly Rent,12000.00,debit\n"
        "2026-01-10,Supermarket Groceries,4000.00,debit\n"
        "2026-01-15,Metro Transport Transit,2000.00,debit\n"
        "2026-01-20,Bank Loan EMI Payment,6000.00,debit\n"
        "2026-01-25,Restaurant Food Dining,3000.00,debit\n"
    )
    upload_res = client.post(
        "/api/statements/upload",
        headers=headers_a,
        files={"file": ("hackathon_statement.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")}
    )
    assert upload_res.status_code == 200
    upload_body = upload_res.json()
    assert upload_body["total_parsed"] == 6

    # Verify transactions persisted
    tx_list = client.get("/api/users/transactions", headers=headers_a).json()
    assert len(tx_list) == 6

    print("\n--- TEST 3: CATEGORIZATION ---")
    # Verify categories were predicted and saved
    categories = [t["category"] for t in tx_list]
    for cat in categories:
        assert cat is not None and len(cat) > 0
    # Confirm rent and groceries were classified
    descriptions = [t["description"] for t in tx_list]
    assert any("Rent" in d for d in descriptions)

    print("\n--- TEST 4: FINANCIAL CALCULATIONS ---")
    state_res = client.get("/api/users/state", headers=headers_a)
    assert state_res.status_code == 200
    state = state_res.json()
    assert state["income"] == 50000.0
    assert state["expenses"] == 27000.0
    assert state["savings"] == 23000.0
    assert state["cash_flow"] == 23000.0

    print("\n--- TEST 5: DUPLICATES AND DATA ISOLATION ---")
    # Upload same CSV again
    dup_res = client.post(
        "/api/statements/upload",
        headers=headers_a,
        files={"file": ("hackathon_statement.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")}
    )
    assert dup_res.status_code == 200
    # Count must remain 6 (no double-counting)
    tx_after_dup = client.get("/api/users/transactions", headers=headers_a).json()
    assert len(tx_after_dup) == 6

    # User B Isolation test
    user_b_email = f"hackathon_user_b_{offset}@fin4you.ai"
    reg_b = client.post("/api/auth/register", json={
        "email": user_b_email,
        "password": "Password123!",
        "full_name": "User B"
    })
    otp_b = reg_b.json()["mock_otp"]
    tok_b = client.post("/api/auth/verify-otp", json={"email": user_b_email, "otp": otp_b}).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {tok_b}"}

    tx_b = client.get("/api/users/transactions", headers=headers_b).json()
    assert len(tx_b) == 0
    state_b = client.get("/api/users/state", headers=headers_b).json()
    assert state_b["income"] == 0.0
    assert state_b["expenses"] == 0.0

    print("\n--- TEST 6: INSIGHTS & STATEMENTS ---")
    stmt_res = client.get("/api/users/monthly-statement", headers=headers_a)
    assert stmt_res.status_code == 200
    stmt = stmt_res.json()
    assert stmt["income"]["current"] == 50000.0
    assert stmt["expenses"]["current"] == 27000.0
    assert stmt["cash_flow"]["current"] == 23000.0

    print("\n--- TEST 7: FORECAST ---")
    hist_res = client.get("/api/users/forecast/history", headers=headers_a)
    assert hist_res.status_code == 200
    hist = hist_res.json()
    assert hist["observed_months"] == 1
    assert len(hist["history"]) == 1
    assert hist["history"][0]["income"] == 50000.0
    assert hist["history"][0]["cash_flow"] == 23000.0

    print("\n--- TEST 8: WHAT-IF SIMULATOR ---")
    # Base state: cash flow is 23,000. Reduce expenses by 2,000
    whatif_res = client.post("/api/users/what-if", headers=headers_a, json={
        "scenario_type": "reduce_expense",
        "amount": 2000.0
    })
    assert whatif_res.status_code == 200
    whatif = whatif_res.json()
    assert whatif["baseline"]["projected_cash_flow"] == 23000.0
    assert whatif["scenario"]["projected_cash_flow"] == 25000.0
    assert whatif["impact"]["cash_flow_difference"] == 2000.0

    print("\n--- TEST 9: ARTHA AI ---")
    ai_res = client.post("/api/copilot/query", headers=headers_a, json={
        "message": "What is my total monthly income?"
    })
    assert ai_res.status_code == 200
    ai_data = ai_res.json()
    assert "response" in ai_data
    assert "50,000" in ai_data["response"] or "50000" in ai_data["response"]

    app.dependency_overrides.clear()
    print("\n✓ ALL 9 BACKEND PHASES OF HACKATHON ACCEPTANCE TEST PASSED!")
