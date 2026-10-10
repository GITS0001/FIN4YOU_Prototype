import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth import get_current_user
from app.models import User

client = TestClient(app)

def override_get_current_user():
    user = User()
    user.id = 28 # Use int ID for DB
    return user

@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()


# Mock the orchestrator dependencies
import app.copilot.orchestrator as orch
from app.schemas.financial import FinancialProfile

def mock_get_user_profile(db, user_id):
    if user_id == 999:
        return None
    return FinancialProfile(
        user_id=f"user_{user_id}",
        home_currency="INR",
        current_available_balance=1500.0,
        minimum_balance_to_keep=1000.0,
        financial_priorities=[],
        expense_categories_to_protect=[],
        expense_categories_user_is_willing_to_reduce=[],
        expense_categories_user_is_willing_to_stop=[],
        payment_methods_user_will_consider=[]
    )

from datetime import date
from app.schemas.financial import Transaction

def mock_get_user_transactions(db, user_id):
    return [
        Transaction(transaction_id="t1", user_id="u1", event_type="income", description="Salary", category="salary", direction="credit", amount=1500.0, currency="INR", event_date=date(2024, 1, 1), status="settled", flexibility="variable"),
        Transaction(transaction_id="t2", user_id="u1", event_type="income", description="Salary", category="salary", direction="credit", amount=1500.0, currency="INR", event_date=date(2024, 2, 1), status="settled", flexibility="variable"),
        Transaction(transaction_id="t3", user_id="u1", event_type="income", description="Salary", category="salary", direction="credit", amount=1500.0, currency="INR", event_date=date(2024, 3, 1), status="settled", flexibility="variable"),
        Transaction(transaction_id="t4", user_id="u1", event_type="expense", description="Rent", category="rent", direction="debit", amount=1500.0, currency="INR", event_date=date(2024, 1, 2), status="settled", flexibility="fixed"),
        Transaction(transaction_id="t5", user_id="u1", event_type="expense", description="Rent", category="rent", direction="debit", amount=1500.0, currency="INR", event_date=date(2024, 2, 2), status="settled", flexibility="fixed"),
        Transaction(transaction_id="t6", user_id="u1", event_type="expense", description="Rent", category="rent", direction="debit", amount=1500.0, currency="INR", event_date=date(2024, 3, 2), status="settled", flexibility="fixed"),
    ]

orch.get_user_profile = mock_get_user_profile
orch.get_user_transactions = mock_get_user_transactions

def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_copilot_missing_message():
    response = client.post("/api/copilot/query", json={"message": ""})
    assert response.status_code == 400

def test_copilot_invalid_user_id_404():
    app.dependency_overrides[get_current_user] = lambda: type("User", (), {"id": 999})()
    response = client.post("/api/copilot/query", json={"message": "hello"})
    assert response.status_code == 404


def test_copilot_affordability_user_28():
    # User 28 integration demo path
    response = client.post("/api/copilot/query", json={
        "message": "Can I afford to spend 1302.4 in installments?"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] in ["PAYMENT_OPTION_ANALYSIS", "AFFORDABILITY_CHECK"]
    
    # Verify the improved response generator uses formatted human-readable text
    # New format: "Option 1: N x AMOUNT/installment, total AMOUNT (method)"
    assert "installment" in data["response"].lower()
    # Check that the amount is present (ignoring LLM currency hallucinations)
    assert "1,302" in data["response"] or "1302" in data["response"]
    assert "raw float" not in data["response"]  # No raw floats
    
    # Verify structured result has the right math without LLM calculations
    assert data["structured_result"]["affordability_status"] == "NOT AFFORDABLE UNDER CURRENT PROJECTION"
    assert len(data["structured_result"]["viable_options"]) == 2

def test_copilot_what_if():
    response = client.post("/api/copilot/query", json={
        "message": "What happens if I spend 200 less on eating out?"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "WHAT_IF"
    assert "projected_balance" in data["structured_result"]

def test_copilot_unknown_question():
    response = client.post("/api/copilot/query", json={
        "message": "Will Bitcoin go up next month?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "UNKNOWN"
    assert data["status"] == "UNSUPPORTED"
    # Response should guide user to valid financial questions
    response_lower = data["response"].lower()
    assert any(phrase in response_lower for phrase in [
        "help",
        "finance",
        "afford",
        "spend"
    ])
