"""
Regression test for the FIN4YOU Artha AI Mediclaim Affordability Scenario Defect.

Exact Scenario Inputs:
- Monthly income: ₹60,000
- Bank balance: ₹1,50,000
- Monthly expenses: ₹35,000
- Minimum emergency fund: ₹75,000
- Annual premium: ₹18,000

Expected Grounded Mathematical Calculations:
- Monthly expenses = ₹35,000
- Monthly savings = ₹25,000 (₹60,000 - ₹35,000)
- Monthly premium provision = ₹1,500 (₹18,000 / 12)
- Immediate post-payment balance = ₹1,32,000 (₹1,50,000 - ₹18,000)
- Balance above emergency fund = ₹57,000 (₹1,32,000 - ₹75,000)
- Resulting balance (after month's net cash flow) = ₹1,57,000 (₹1,50,000 + ₹25,000 - ₹18,000)
- Recommendation = "AFFORDABLE"
- Confidence != "HIGH" (Must be downgraded to "MEDIUM" due to conflict with profile on record)
- Transparent calculation breakdown with identified data sources
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import SessionLocal
from app.models import User, Profile
from app.copilot.intent_parser import IntentParser
from app.copilot.orchestrator import CopilotOrchestrator
from app.schemas.copilot import CopilotRequest, IntentType
from app.schemas.financial import FinancialProfile, PredictionEngineResult, ProjectedCashFlow
from app.decision.affordability import AffordabilityEngine
from app.auth import create_access_token


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_intent_parser_extracts_all_mediclaim_scenario_parameters():
    """Verify that intent parser extracts stated scenario variables from user query."""
    parser = IntentParser()
    message = (
        "I tested the mediclaim purchase scenario with these inputs:\n"
        "Monthly income: ₹60,000\n"
        "Bank balance: ₹1,50,000\n"
        "Monthly expenses: ₹35,000\n"
        "Minimum emergency fund: ₹75,000\n"
        "Annual premium: ₹18,000"
    )

    parsed = parser.parse(message)

    assert parsed.intent == IntentType.AFFORDABILITY_CHECK
    assert parsed.amount == 18000.0
    assert parsed.stated_balance == 150000.0
    assert parsed.stated_income == 60000.0
    assert parsed.stated_expenses == 35000.0
    assert parsed.stated_buffer == 75000.0
    assert parsed.is_annual is True
    assert parsed.item_description == "mediclaim"


def test_affordability_engine_mathematical_calculations():
    """Verify exact mathematical calculations in AffordabilityEngine."""
    # Stored user profile has different historical balance and buffer
    profile = FinancialProfile(
        user_id="user_test",
        home_currency="INR",
        current_available_balance=70000.0,
        minimum_balance_to_keep=11000.0,
        financial_priorities=[],
        expense_categories_to_protect=[],
        expense_categories_user_is_willing_to_reduce=[],
        expense_categories_user_is_willing_to_stop=[],
        payment_methods_user_will_consider=[],
    )

    baseline_prediction = PredictionEngineResult(
        available=True,
        projected_cash_flow=ProjectedCashFlow(
            period="2026-11",
            projected_income=51000.0,
            projected_expenses=2398.0,
            projected_cash_flow=48602.0,
            known_obligations=0.0,
        ),
    )

    engine = AffordabilityEngine(profile, baseline_prediction)

    result = engine.evaluate_purchase(
        amount=18000.0,
        stated_balance=150000.0,
        stated_income=60000.0,
        stated_expenses=35000.0,
        stated_buffer=75000.0,
        is_annual=True,
    )

    # Assert exact required mathematical calculations
    assert result.status == "AFFORDABLE"
    assert result.monthly_savings == 25000.0  # 60,000 - 35,000
    assert result.monthly_premium_provision == 1500.0  # 18,000 / 12
    assert result.immediate_post_payment_balance == 132000.0  # 150,000 - 18,000
    assert result.balance_above_emergency_fund == 57000.0  # 132,000 - 75,000
    assert result.resulting_balance == 157000.0  # 150,000 + 25,000 - 18,000
    assert result.shortfall == 0.0

    # Assert conflict detection and data source auditing
    assert result.has_conflict is True
    assert result.data_sources["current_balance"] == "Stated Scenario Override"
    assert result.data_sources["minimum_buffer"] == "Stated Emergency Fund Target"
    assert result.data_sources["monthly_income"] == "Stated Scenario Input"
    assert result.data_sources["monthly_expenses"] == "Stated Scenario Input"


def test_orchestrator_mediclaim_scenario_confidence_downgrade(db_session: Session):
    """Verify that CopilotOrchestrator downgrades confidence when inputs conflict with profile."""
    orchestrator = CopilotOrchestrator()
    message = (
        "I tested the mediclaim purchase scenario with these inputs:\n"
        "Monthly income: ₹60,000\n"
        "Bank balance: ₹1,50,000\n"
        "Monthly expenses: ₹35,000\n"
        "Minimum emergency fund: ₹75,000\n"
        "Annual premium: ₹18,000"
    )

    req = CopilotRequest(user_id="1", message=message)
    res = orchestrator.process_query(req, db_session)

    assert res.intent == IntentType.AFFORDABILITY_CHECK
    assert res.status == "SUCCESS"

    # CRITICAL: Artha AI cannot report HIGH confidence when inputs conflict with stored profile
    assert res.confidence != "HIGH"
    assert res.confidence == "MEDIUM"

    sr = res.structured_result
    assert sr is not None
    assert sr["current_balance"] == 150000.0
    assert sr["minimum_buffer"] == 75000.0
    assert sr["monthly_income"] == 60000.0
    assert sr["monthly_expenses"] == 35000.0
    assert sr["monthly_savings"] == 25000.0
    assert sr["monthly_premium_provision"] == 1500.0
    assert sr["immediate_post_payment_balance"] == 132000.0
    assert sr["balance_above_emergency_fund"] == 57000.0
    assert sr["affordability_status"] == "AFFORDABLE"
    assert sr["has_conflict"] is True

    # Transparent calculation breakdown in observed facts
    facts_str = " ".join(res.observed_facts)
    assert "150,000" in facts_str
    assert "75,000" in facts_str
    assert "60,000" in facts_str
    assert "35,000" in facts_str
    assert "25,000" in facts_str
    assert "1,500" in facts_str
    assert "132,000" in facts_str
    assert "57,000" in facts_str


def test_api_copilot_query_mediclaim_endpoint(db_session: Session):
    """Verify complete API response over HTTP client with authentication."""
    user = db_session.query(User).filter(User.id == 1).first()
    if not user:
        user = User(email="test_user@fin4you.com")
        db_session.add(user)
        db_session.commit()

    token = create_access_token({"sub": user.email})
    client = TestClient(app)

    response = client.post(
        "/api/copilot/query",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "user_id": str(user.id),
            "message": (
                "I tested the mediclaim purchase scenario with these inputs:\n"
                "Monthly income: ₹60,000\n"
                "Bank balance: ₹1,50,000\n"
                "Monthly expenses: ₹35,000\n"
                "Minimum emergency fund: ₹75,000\n"
                "Annual premium: ₹18,000"
            ),
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["intent"] == "AFFORDABILITY_CHECK"
    assert data["status"] == "SUCCESS"
    assert data["confidence"] == "MEDIUM"

    sr = data["structured_result"]
    assert sr["current_balance"] == 150000.0
    assert sr["minimum_buffer"] == 75000.0
    assert sr["monthly_income"] == 60000.0
    assert sr["monthly_expenses"] == 35000.0
    assert sr["monthly_savings"] == 25000.0
    assert sr["monthly_premium_provision"] == 1500.0
    assert sr["immediate_post_payment_balance"] == 132000.0
    assert sr["balance_above_emergency_fund"] == 57000.0
    assert sr["affordability_status"] == "AFFORDABLE"
    assert sr["has_conflict"] is True
