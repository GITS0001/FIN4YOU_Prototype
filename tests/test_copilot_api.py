import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_copilot_missing_user():
    response = client.post("/api/copilot/query", json={"user_id": "", "message": "hello"})
    assert response.status_code == 400

def test_copilot_missing_message():
    response = client.post("/api/copilot/query", json={"user_id": "user_28", "message": ""})
    assert response.status_code == 400

def test_copilot_invalid_user_id_404():
    response = client.post("/api/copilot/query", json={"user_id": "user_invalid_999", "message": "hello"})
    assert response.status_code == 404

def test_copilot_affordability_user_28():
    # User 28 integration demo path
    response = client.post("/api/copilot/query", json={
        "user_id": "user_28",
        "message": "Can I afford to spend 1302.4 in installments?"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "PAYMENT_OPTION_ANALYSIS"
    
    # Verify the improved response generator uses formatted human-readable text
    # New format: "Option 1: N x AMOUNT/installment, total AMOUNT (method)"
    assert "installment" in data["response"].lower()
    assert "€" in data["response"]  # Currency formatted correctly
    assert "raw float" not in data["response"]  # No raw floats
    
    # Verify structured result has the right math without LLM calculations
    assert data["structured_result"]["affordability_status"] == "NOT AFFORDABLE UNDER CURRENT PROJECTION"
    assert len(data["structured_result"]["viable_options"]) == 2

def test_copilot_what_if():
    response = client.post("/api/copilot/query", json={
        "user_id": "user_28",
        "message": "What happens if I spend 200 less on eating out?"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "WHAT_IF"
    assert "projected_balance" in data["structured_result"]

def test_copilot_unknown_question():
    response = client.post("/api/copilot/query", json={
        "user_id": "user_28",
        "message": "Will Bitcoin go up next month?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "UNKNOWN"
    assert data["status"] == "UNSUPPORTED"
    # Response should guide user to valid financial questions
    assert any(phrase in data["response"] for phrase in [
        "I can help you",
        "questions about",
        "financial",
    ])
