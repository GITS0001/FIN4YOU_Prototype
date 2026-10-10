import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, date
import uuid

from app.supabase_config import get_supabase_client, is_supabase_configured

logger = logging.getLogger("fin4you.supabase_repo")

class SupabaseRepositoryError(Exception):
    """Custom exception for Supabase repository layer operations."""
    pass

class SupabaseRepository:
    """
    Repository layer for interacting with Supabase tables:
    - "Profiles"
    - "Transactions"
    - "Financial_Summaries"
    - "Forecasts"
    - "Monthly_Reports"

    Adheres strictly to PostgreSQL mixed-case quoted table names.
    Provides batch deduplication and user-scoped data isolation.
    """
    def __init__(self, client=None):
        self._client = client

    @property
    def client(self):
        if self._client is not None:
            return self._client
        client = get_supabase_client(use_secret_key=True)
        return client

    # --------------------------------------------------------------------------
    # Profiles Operations
    # --------------------------------------------------------------------------
    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch profile for a specific user ID."""
        client = self.client
        if not client:
            return None

        try:
            res = client.table("Profiles").select("*").eq("user_id", str(user_id)).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching profile for user: {type(e).__name__}")
            raise SupabaseRepositoryError("Failed to retrieve user profile.") from e

    def upsert_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upsert user profile."""
        client = self.client
        if not client:
            raise SupabaseRepositoryError("Supabase client is not available.")

        data = {**profile_data, "user_id": str(user_id), "updated_at": datetime.utcnow().isoformat()}
        try:
            # Check if profile already exists for this user_id
            existing = self.get_profile(user_id)
            if existing:
                res = client.table("Profiles").update(data).eq("user_id", str(user_id)).execute()
            else:
                if "id" in data:
                    del data["id"]
                res = client.table("Profiles").insert(data).execute()

            if res.data and len(res.data) > 0:
                return res.data[0]
            return data
        except Exception as e:
            logger.error(f"Error upserting profile: {type(e).__name__}")
            raise SupabaseRepositoryError("Failed to save user profile.") from e

    # --------------------------------------------------------------------------
    # Transactions Operations & Deduplication
    # --------------------------------------------------------------------------
    def get_existing_transaction_ids(self, user_id: str, candidate_ids: List[str]) -> Set[str]:
        """
        Retrieves existing transaction_ids for a user among a set of candidate IDs.
        Used for safe deduplication during statement uploads.
        """
        client = self.client
        if not client or not candidate_ids:
            return set()

        try:
            # Query in batches of 100 to avoid URL length limitations
            batch_size = 100
            existing_ids = set()
            for i in range(0, len(candidate_ids), batch_size):
                chunk = candidate_ids[i:i + batch_size]
                res = client.table("Transactions") \
                            .select("transaction_id") \
                            .eq("user_id", str(user_id)) \
                            .in_("transaction_id", chunk) \
                            .execute()
                if res.data:
                    for row in res.data:
                        existing_ids.add(row["transaction_id"])
            return existing_ids
        except Exception as e:
            logger.error(f"Error checking existing transactions: {type(e).__name__}")
            raise SupabaseRepositoryError("Failed to query transaction deduplication records.") from e

    def save_transactions(self, user_id: str, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Batch saves transactions with deduplication on transaction_id.
        Does not create duplicates when identical statements are re-uploaded.
        """
        client = self.client
        if not client:
            raise SupabaseRepositoryError("Supabase client is not available.")

        if not transactions:
            return {"inserted_count": 0, "skipped_duplicates_count": 0, "total_processed": 0}

        candidate_ids = [t["transaction_id"] for t in transactions if "transaction_id" in t]
        existing_ids = self.get_existing_transaction_ids(user_id, candidate_ids)

        new_records = []
        skipped_count = 0

        for t in transactions:
            tx_id = t.get("transaction_id")
            if tx_id in existing_ids:
                skipped_count += 1
                continue

            record = {
                "transaction_id": tx_id,
                "user_id": str(user_id),
                "event_type": t.get("event_type"),
                "description": t.get("description"),
                "category": t.get("category"),
                "direction": t.get("direction"),
                "amount": float(t.get("amount", 0.0)),
                "currency": t.get("currency", "USD"),
                "event_date": str(t.get("event_date")),
                "settlement_date": str(t["settlement_date"]) if t.get("settlement_date") else None,
                "status": t.get("status", "SETTLED"),
                "flexibility": t.get("flexibility", "variable"),
                "ml_confidence": t.get("ml_confidence"),
                "ml_status": t.get("ml_status"),
                "ml_confidence_level": t.get("ml_confidence_level"),
                "created_at": datetime.utcnow().isoformat()
            }
            new_records.append(record)

        inserted_count = 0
        if new_records:
            try:
                # Insert in batches of 100
                batch_size = 100
                for i in range(0, len(new_records), batch_size):
                    chunk = new_records[i:i + batch_size]
                    res = client.table("Transactions").insert(chunk).execute()
                    if res.data:
                        inserted_count += len(res.data)
                    else:
                        inserted_count += len(chunk)
            except Exception as e:
                logger.error(f"Error inserting transactions: {type(e).__name__}")
                raise SupabaseRepositoryError("Failed to persist transactions to Supabase.") from e

        return {
            "inserted_count": inserted_count,
            "skipped_duplicates_count": skipped_count,
            "total_processed": len(transactions)
        }

    def get_transactions(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch transactions belonging strictly to the authenticated user."""
        client = self.client
        if not client:
            return []

        try:
            res = client.table("Transactions") \
                        .select("*") \
                        .eq("user_id", str(user_id)) \
                        .order("event_date", desc=True) \
                        .limit(limit) \
                        .execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Error fetching user transactions: {type(e).__name__}")
            raise SupabaseRepositoryError("Failed to retrieve user transactions.") from e

    # --------------------------------------------------------------------------
    # Financial Summaries Operations
    # --------------------------------------------------------------------------
    def save_financial_summary(self, user_id: str, summary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Persist computed financial summary to 'Financial_Summaries' table."""
        client = self.client
        if not client:
            return summary_data

        period = summary_data.get("reporting_period", datetime.utcnow().strftime("%Y-%m"))
        summary_id = summary_data.get("summary_id") or f"summary_{user_id}_{period}_{uuid.uuid4().hex[:8]}"

        record = {
            "summary_id": summary_id,
            "user_id": str(user_id),
            "reporting_period": period,
            "income": float(summary_data.get("income", 0.0)),
            "expenses": float(summary_data.get("expenses", 0.0)),
            "savings": float(summary_data.get("savings", 0.0)),
            "savings_rate": float(summary_data.get("savings_rate", 0.0)),
            "cash_flow": float(summary_data.get("cash_flow", 0.0)),
            "essential_expenses": float(summary_data.get("essential_expenses", 0.0)),
            "discretionary_expenses": float(summary_data.get("discretionary_expenses", 0.0)),
            "recurring_obligations": float(summary_data.get("recurring_obligations", 0.0)),
            "emi_burden": float(summary_data.get("emi_burden", 0.0)),
            "data_quality_confidence": float(summary_data.get("data_quality_confidence", 1.0)),
            "summary_data": summary_data.get("raw_summary", summary_data),
            "created_at": datetime.utcnow().isoformat()
        }

        try:
            # Check if summary for this user and period already exists
            existing = client.table("Financial_Summaries") \
                             .select("id, summary_id") \
                             .eq("user_id", str(user_id)) \
                             .eq("reporting_period", period) \
                             .execute()

            if existing.data and len(existing.data) > 0:
                res = client.table("Financial_Summaries") \
                            .update(record) \
                            .eq("id", existing.data[0]["id"]) \
                            .execute()
            else:
                if "id" in record:
                    del record["id"]
                res = client.table("Financial_Summaries").insert(record).execute()

            return res.data[0] if (res.data and len(res.data) > 0) else record
        except Exception as e:
            logger.error(f"Error saving financial summary: {type(e).__name__}")
            raise SupabaseRepositoryError("Failed to save financial summary.") from e

    def get_financial_summary(self, user_id: str, reporting_period: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve latest or period-specific financial summary."""
        client = self.client
        if not client:
            return None

        try:
            query = client.table("Financial_Summaries").select("*").eq("user_id", str(user_id))
            if reporting_period:
                query = query.eq("reporting_period", reporting_period)
            res = query.order("created_at", desc=True).limit(1).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            return None
        except Exception as e:
            logger.error(f"Error retrieving financial summary: {type(e).__name__}")
            raise SupabaseRepositoryError("Failed to retrieve financial summary.") from e

    # --------------------------------------------------------------------------
    # Forecasts Operations
    # --------------------------------------------------------------------------
    def save_forecast(self, user_id: str, forecast_data: Dict[str, Any]) -> Dict[str, Any]:
        """Persist prediction engine output to 'Forecasts' table."""
        client = self.client
        if not client:
            return forecast_data

        period = forecast_data.get("forecast_period", "")
        forecast_id = forecast_data.get("forecast_id") or f"fc_{user_id}_{period}_{uuid.uuid4().hex[:8]}"

        record = {
            "forecast_id": forecast_id,
            "user_id": str(user_id),
            "forecast_period": period,
            "projected_income": float(forecast_data.get("projected_income", 0.0)),
            "projected_expenses": float(forecast_data.get("projected_expenses", 0.0)),
            "known_obligations": float(forecast_data.get("known_obligations", 0.0)),
            "projected_cash_flow": float(forecast_data.get("projected_cash_flow", 0.0)),
            "uncertainty": float(forecast_data.get("uncertainty", 0.0)),
            "confidence": float(forecast_data.get("confidence", 1.0)),
            "evaluation_mae": forecast_data.get("evaluation_mae"),
            "evaluation_rmse": forecast_data.get("evaluation_rmse"),
            "forecast_data": forecast_data.get("raw_forecast", forecast_data),
            "created_at": datetime.utcnow().isoformat()
        }

        try:
            existing = client.table("Forecasts") \
                             .select("id, forecast_id") \
                             .eq("user_id", str(user_id)) \
                             .eq("forecast_period", period) \
                             .execute()

            if existing.data and len(existing.data) > 0:
                res = client.table("Forecasts") \
                            .update(record) \
                            .eq("id", existing.data[0]["id"]) \
                            .execute()
            else:
                if "id" in record:
                    del record["id"]
                res = client.table("Forecasts").insert(record).execute()

            return res.data[0] if (res.data and len(res.data) > 0) else record
        except Exception as e:
            logger.error(f"Error saving forecast: {type(e).__name__}")
            raise SupabaseRepositoryError("Failed to save forecast.") from e

    def get_forecast(self, user_id: str, forecast_period: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve forecast for a user and period."""
        client = self.client
        if not client:
            return None

        try:
            query = client.table("Forecasts").select("*").eq("user_id", str(user_id))
            if forecast_period:
                query = query.eq("forecast_period", forecast_period)
            res = query.order("created_at", desc=True).limit(1).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            return None
        except Exception as e:
            logger.error(f"Error retrieving forecast: {type(e).__name__}")
            raise SupabaseRepositoryError("Failed to retrieve forecast.") from e

    # --------------------------------------------------------------------------
    # Monthly Reports Operations
    # --------------------------------------------------------------------------
    def save_monthly_report(self, user_id: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Persist deterministic monthly report to 'Monthly_Reports' table."""
        client = self.client
        if not client:
            return report_data

        period = report_data.get("report_period") or report_data.get("reporting_period", "")
        report_id = report_data.get("report_id") or f"rep_{user_id}_{period}_{uuid.uuid4().hex[:8]}"

        record = {
            "report_id": report_id,
            "user_id": str(user_id),
            "reporting_period": period,
            "previous_period": report_data.get("previous_period"),
            "report_data": report_data,
            "storage_reference": report_data.get("storage_reference"),
            "created_at": datetime.utcnow().isoformat()
        }

        try:
            existing = client.table("Monthly_Reports") \
                             .select("id, report_id") \
                             .eq("user_id", str(user_id)) \
                             .eq("reporting_period", period) \
                             .execute()

            if existing.data and len(existing.data) > 0:
                res = client.table("Monthly_Reports") \
                            .update(record) \
                            .eq("id", existing.data[0]["id"]) \
                            .execute()
            else:
                if "id" in record:
                    del record["id"]
                res = client.table("Monthly_Reports").insert(record).execute()

            return res.data[0] if (res.data and len(res.data) > 0) else record
        except Exception as e:
            logger.error(f"Error saving monthly report: {type(e).__name__}")
            raise SupabaseRepositoryError("Failed to save monthly report.") from e

    def get_monthly_reports(self, user_id: str, reporting_period: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve monthly reports for a user."""
        client = self.client
        if not client:
            return []

        try:
            query = client.table("Monthly_Reports").select("*").eq("user_id", str(user_id))
            if reporting_period:
                query = query.eq("reporting_period", reporting_period)
            res = query.order("created_at", desc=True).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Error retrieving monthly reports: {type(e).__name__}")
            raise SupabaseRepositoryError("Failed to retrieve monthly reports.") from e

# Default global instance
supabase_repository = SupabaseRepository()
