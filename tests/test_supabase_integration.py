import pytest
from unittest.mock import MagicMock, patch
import os
from datetime import date
from fastapi.testclient import TestClient

from app.main import app
from app.supabase_config import (
    validate_supabase_env,
    SupabaseConfigError,
    is_supabase_configured,
)
from app.services.supabase_repository import SupabaseRepository, SupabaseRepositoryError

client = TestClient(app)

# -----------------------------------------------------------------------------
# 1. Supabase Configuration & Missing Environment Tests
# -----------------------------------------------------------------------------
def test_supabase_config_missing_env_in_production(monkeypatch):
    """Verify that in production, missing Supabase credentials raise SupabaseConfigError."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setattr("app.supabase_config.ENVIRONMENT", "production")
    monkeypatch.setattr("app.supabase_config.SUPABASE_URL", "")
    monkeypatch.setattr("app.supabase_config.SUPABASE_SECRET_KEY", "")
    monkeypatch.setattr("app.supabase_config.SUPABASE_PUBLISHABLE_KEY", "")

    with pytest.raises(SupabaseConfigError) as exc_info:
        validate_supabase_env()
    assert "CRITICAL CONFIGURATION ERROR" in str(exc_info.value)
    assert "SUPABASE_URL" in str(exc_info.value)

def test_supabase_config_valid(monkeypatch):
    """Verify valid Supabase configuration detection."""
    monkeypatch.setattr("app.supabase_config.ENVIRONMENT", "development")
    monkeypatch.setattr("app.supabase_config.SUPABASE_URL", "https://xyz.supabase.co")
    monkeypatch.setattr("app.supabase_config.SUPABASE_SECRET_KEY", "secret_key_123")
    monkeypatch.setattr("app.supabase_config.SUPABASE_PUBLISHABLE_KEY", "anon_key_123")

    # Should not raise
    validate_supabase_env()
    assert is_supabase_configured() is True


# -----------------------------------------------------------------------------
# 2. Supabase Repository Unit Tests (with Isolated Mock Client)
# -----------------------------------------------------------------------------
@pytest.fixture
def mock_supabase_client():
    mock = MagicMock()
    return mock

def test_repository_profile_operations(mock_supabase_client):
    """Test saving and retrieving user profile via SupabaseRepository."""
    mock_table = MagicMock()
    mock_supabase_client.table.return_value = mock_table

    # Mock get_profile
    mock_table.select.return_value.eq.return_value.execute.return_value.data = [{
        "user_id": "user_42",
        "full_name": "Satya Nadella",
        "home_currency": "USD",
        "current_available_balance": 50000.0,
        "minimum_balance_to_keep": 10000.0,
        "financial_priorities": "retirement|health",
    }]

    repo = SupabaseRepository(client=mock_supabase_client)
    profile = repo.get_profile("user_42")

    assert profile is not None
    assert profile["full_name"] == "Satya Nadella"
    assert profile["home_currency"] == "USD"
    mock_supabase_client.table.assert_called_with("Profiles")

def test_repository_transactions_and_deduplication(mock_supabase_client):
    """
    Test batch transaction saving with deduplication.
    Ensures already existing transaction IDs are skipped.
    """
    mock_table = MagicMock()
    mock_supabase_client.table.return_value = mock_table

    # Existing transactions in DB: tx_1 already exists
    mock_table.select.return_value.eq.return_value.in_.return_value.execute.return_value.data = [
        {"transaction_id": "tx_1"}
    ]

    # Insert execution returns newly inserted row
    mock_table.insert.return_value.execute.return_value.data = [
        {"transaction_id": "tx_2", "amount": 100.0}
    ]

    repo = SupabaseRepository(client=mock_supabase_client)
    input_txs = [
        {
            "transaction_id": "tx_1",
            "amount": 50.0,
            "event_type": "expense",
            "description": "Lunch",
            "direction": "debit",
            "event_date": "2026-10-01"
        },
        {
            "transaction_id": "tx_2",
            "amount": 100.0,
            "event_type": "expense",
            "description": "Groceries",
            "direction": "debit",
            "event_date": "2026-10-02"
        }
    ]

    result = repo.save_transactions(user_id="user_42", transactions=input_txs)
    assert result["total_processed"] == 2
    assert result["skipped_duplicates_count"] == 1
    assert result["inserted_count"] == 1

def test_repository_user_isolation(mock_supabase_client):
    """
    Verify user-specific data isolation:
    Transactions query strictly binds the user_id.
    """
    mock_table = MagicMock()
    mock_supabase_client.table.return_value = mock_table
    mock_table.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"transaction_id": "tx_user_1", "user_id": "user_1"}
    ]

    repo = SupabaseRepository(client=mock_supabase_client)
    txs = repo.get_transactions("user_1")

    assert len(txs) == 1
    assert txs[0]["user_id"] == "user_1"
    # Ensure eq was called with "user_id" and "user_1"
    mock_table.select.return_value.eq.assert_called_with("user_id", "user_1")

def test_repository_financial_summary_persistence(mock_supabase_client):
    """Test saving and retrieving financial summaries."""
    mock_table = MagicMock()
    mock_supabase_client.table.return_value = mock_table

    # Existing check returns empty list (new insert)
    mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
    mock_table.insert.return_value.execute.return_value.data = [{
        "summary_id": "sum_1",
        "user_id": "user_1",
        "reporting_period": "2026-10",
        "income": 4000.0,
        "expenses": 2500.0,
        "cash_flow": 1500.0,
        "savings_rate": 0.375
    }]

    repo = SupabaseRepository(client=mock_supabase_client)
    saved = repo.save_financial_summary("user_1", {
        "reporting_period": "2026-10",
        "income": 4000.0,
        "expenses": 2500.0,
        "savings": 1500.0,
        "cash_flow": 1500.0,
        "savings_rate": 0.375
    })

    assert saved["income"] == 4000.0
    mock_supabase_client.table.assert_called_with("Financial_Summaries")

def test_repository_forecast_persistence(mock_supabase_client):
    """Test saving and retrieving forecasts."""
    mock_table = MagicMock()
    mock_supabase_client.table.return_value = mock_table

    mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
    mock_table.insert.return_value.execute.return_value.data = [{
        "forecast_id": "fc_1",
        "user_id": "user_1",
        "forecast_period": "2026-11",
        "projected_income": 4500.0,
        "projected_expenses": 2600.0,
        "projected_cash_flow": 1900.0
    }]

    repo = SupabaseRepository(client=mock_supabase_client)
    saved = repo.save_forecast("user_1", {
        "forecast_period": "2026-11",
        "projected_income": 4500.0,
        "projected_expenses": 2600.0,
        "projected_cash_flow": 1900.0,
        "known_obligations": 500.0
    })

    assert saved["projected_income"] == 4500.0
    mock_supabase_client.table.assert_called_with("Forecasts")

def test_repository_monthly_report_persistence(mock_supabase_client):
    """Test saving and retrieving monthly reports."""
    mock_table = MagicMock()
    mock_supabase_client.table.return_value = mock_table

    mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
    mock_table.insert.return_value.execute.return_value.data = [{
        "report_id": "rep_1",
        "user_id": "user_1",
        "reporting_period": "2026-10",
        "previous_period": "2026-09"
    }]

    repo = SupabaseRepository(client=mock_supabase_client)
    saved = repo.save_monthly_report("user_1", {
        "report_period": "2026-10",
        "previous_period": "2026-09",
        "metrics": {"current_month": {"income": 5000.0, "expense": 3000.0}}
    })

    assert saved["reporting_period"] == "2026-10"
    mock_supabase_client.table.assert_called_with("Monthly_Reports")


# -----------------------------------------------------------------------------
# 3. Security & Authentication Tests
# -----------------------------------------------------------------------------
def test_unauthorized_access_fails():
    """Verify missing or invalid token receives 401 Unauthorized."""
    # No auth header
    res = client.get("/api/users/profile")
    assert res.status_code == 401

    # Invalid token format
    res = client.get("/api/users/profile", headers={"Authorization": "Bearer invalid_garbage_token"})
    assert res.status_code == 401

def test_persisted_endpoints_require_auth():
    """Verify endpoints for summaries, forecasts, and reports reject unauthenticated calls."""
    res_sum = client.get("/api/users/financial-summaries")
    assert res_sum.status_code == 401

    res_fc = client.get("/api/users/forecasts")
    assert res_fc.status_code == 401

    res_rep = client.get("/api/users/monthly-reports")
    assert res_rep.status_code == 401


# -----------------------------------------------------------------------------
# 4. Statement Upload Deduplication & Regressions
# -----------------------------------------------------------------------------
def test_statement_upload_duplicate_handling(monkeypatch):
    """
    Test statement upload duplicate-handling logic.
    Ensures that re-uploading an identical statement does not create duplicate entries.
    """
    from app.models import User
    from app.auth import get_current_user

    mock_user = User(id=999, email="test_upload@example.com", is_verified=True, is_active=True)
    app.dependency_overrides[get_current_user] = lambda: mock_user

    try:
        csv_content = (
            "transaction_id,amount,category,event_type,description,direction,event_date,currency,status,flexibility\n"
            "tx_dup_1,150.0,groceries,expense,Supermarket,debit,2026-10-05,USD,settled,variable\n"
            "tx_dup_2,50.0,coffee,expense,Cafe,debit,2026-10-06,USD,settled,variable\n"
        )
        files = {"file": ("statement.csv", csv_content, "text/csv")}

        # First upload
        res1 = client.post("/api/statements/upload", files=files)
        assert res1.status_code == 200
        data1 = res1.json()
        assert "Successfully ingested" in data1["message"]

        # Re-upload the exact same CSV
        files_retry = {"file": ("statement.csv", csv_content, "text/csv")}
        res2 = client.post("/api/statements/upload", files=files_retry)
        assert res2.status_code == 200
        data2 = res2.json()
        # Should ingest 0 new transactions due to duplicate prevention
        assert data2["message"] == "Successfully ingested 0 new transactions"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
