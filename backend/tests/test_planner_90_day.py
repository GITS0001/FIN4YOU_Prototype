import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_90_day_financial_plan_endpoint(test_user_token):
    client = TestClient(app)
    response = client.get(
        "/api/users/planner/90-day-plan",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "dataset_summary" in data
    assert "total_90_day_savings_target" in data
    assert "phases" in data
    assert len(data["phases"]) == 3
    assert "financial_terms" in data
    assert len(data["financial_terms"]) >= 4

    p1 = data["phases"][0]
    assert p1["phase_number"] == 1
    assert "Days 1–30" in p1["days"]
    assert len(p1["advice"]) >= 2
    assert len(p1["actions"]) >= 2

    # Check financial terms
    term_names = [t["term"] for t in data["financial_terms"]]
    assert any("Emergency Reserve Buffer" in t for t in term_names)
    assert any("Liquidity Runway" in t for t in term_names)
    assert any("Discretionary" in t for t in term_names)
