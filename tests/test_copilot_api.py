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

def test_copilot_affordability_user_28():
    # User 28 integration demo path
    response = client.post("/api/copilot/query", json={
        "user_id": "user_28",
        "message": "Can I afford to spend 1302.4 in installments?"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "PAYMENT_OPTION_ANALYSIS"
    
    # Verify the fallback response generator caught the viable options
    assert "Option payment_option_79" in data["response"]
    assert "Option payment_option_80" in data["response"]
    
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
    assert "I cannot safely answer that question" in data["response"]
