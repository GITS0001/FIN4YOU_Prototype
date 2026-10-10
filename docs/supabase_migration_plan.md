# FIN4YOU — Supabase Migration Plan & Architecture Audit

## 1. Executive Summary & Existing Architecture Audit

### 1.1 Overview
FIN4YOU is an AI-powered Financial Health Copilot featuring:
- **Frontend**: React + TypeScript + Vite (`frontend/`) using Axios client with Bearer token authentication.
- **Backend**: Python FastAPI (`backend/app/`) exposing REST endpoints for financial intelligence, cash flow forecasting, decision simulation, statement upload, and conversational copilot.
- **Persistence (Current Prototype)**: SQLite database (`data/fin4you.db`) accessed via SQLAlchemy `engine` (`backend/app/database.py`).
- **Target Persistence**: Supabase PostgreSQL containing tables:
  1. `Profiles`
  2. `Transactions`
  3. `Financial_Summaries`
  4. `Forecasts`
  5. `Monthly_Reports`

### 1.2 Audit of Existing Database Usages & SQLite Touchpoints
| Component / File | Current Role | Migration Strategy |
|---|---|---|
| `backend/app/database.py` | Creates SQLAlchemy engine with SQLite default (`sqlite:///./data/fin4you.db`) | Support PostgreSQL connection strings via `DATABASE_URL` alongside official Supabase client configuration. |
| `backend/app/models.py` | Defines `User`, `OTP`, `Profile`, `Transaction`, `CopilotRequest`, `PlaidItem` | Keep existing models; add mappings/schemas for `Financial_Summaries`, `Forecasts`, and `Monthly_Reports` targeting Supabase tables. |
| `backend/app/services/db_service.py` | Fetches `Profile` and `Transaction` from DB session | Refactor into/integrate with Supabase repository layer with fallback test fixture compatibility. |
| `backend/app/api/statements.py` | Ingests CSVs, runs ML categorizer, saves to SQLite with duplicate check | Route persistence to Supabase `"Transactions"` using batch deduplication on `transaction_id`. |
| `backend/app/api/users.py` | Reads/updates profile, transactions, state, prediction, statement, forecast history | Persist and retrieve financial summaries, forecasts, and monthly reports to/from Supabase. |
| `backend/app/api/auth.py` & `auth.py` | Local JWT issuance & bcrypt password verification | Validate Supabase Auth tokens; extract authenticated user identity from verified claims. |
| `tests/test_e2e.py` | Uses SQLite `:memory:` for test isolation | Keep test isolation intact so CI and local test suites execute without requiring live cloud credentials. |
| `docker-compose.yml` | Configures `DATABASE_URL=sqlite:///./financial.db` | Update environment options for Supabase / PostgreSQL. |

### 1.3 Preserved Core Functionality
- **ML & Data Quality Pipeline**: `TransactionCategorizer` and `StatementParser` remain intact.
- **Financial Intelligence**: `FinancialStateEngine` deterministic metrics calculation is 100% preserved.
- **Forecasting Engine**: `PredictionEngine` time series moving average and evaluation calculations are 100% preserved.
- **Decision Engine**: `AffordabilityEngine`, `WhatIfSimulator`, and `ImpactEngine` are 100% preserved.
- **Copilot**: `CopilotOrchestrator` intent parsing and response generator remain intact.
- **API Contracts**: All frontend-facing API signatures remain unchanged.

---

## 2. Supabase Schema Verification & Column Mapping (Phase 2)

### 2.1 Table: `"Profiles"`
| Existing Python Model / Schema Field | Supabase Target Column | Type | Constraints / Description |
|---|---|---|---|
| `user_id` | `user_id` | `UUID` / `TEXT` | PRIMARY KEY or UNIQUE, references `auth.users(id)` |
| `full_name` | `full_name` | `TEXT` | User's full name |
| `age` | `age` | `TEXT` | Demographic age string |
| `marital_status` | `marital_status` | `TEXT` | E.g., 'Single', 'Married' |
| `dependents` | `dependents` | `TEXT` | Number of dependents |
| `occupation` | `occupation` | `TEXT` | Professional profile |
| `city_tier` | `city_tier` | `TEXT` | 'Tier 1', 'Tier 2', etc. |
| `home_currency` | `home_currency` | `VARCHAR(10)` | Default 'USD' / 'EUR' / 'INR' |
| `current_available_balance` | `current_available_balance` | `NUMERIC(14,2)` | Current available funds |
| `minimum_balance_to_keep` | `minimum_balance_to_keep` | `NUMERIC(14,2)` | Emergency / safety buffer |
| `financial_priorities` | `financial_priorities` | `TEXT` / `JSONB` | Delimited or JSON array of priorities |
| `expense_categories_to_protect` | `expense_categories_to_protect` | `TEXT` / `JSONB` | Essential categories |
| `expense_categories_user_is_willing_to_reduce` | `expense_categories_user_is_willing_to_reduce` | `TEXT` / `JSONB` | Flexible categories |
| `expense_categories_user_is_willing_to_stop` | `expense_categories_user_is_willing_to_stop` | `TEXT` / `JSONB` | Discretionary stop categories |
| `payment_methods_user_will_consider` | `payment_methods_user_will_consider` | `TEXT` / `JSONB` | Credit / debit / BNPL options |
| `max_installment_months` | `max_installment_months` | `INTEGER` | Max allowable tenure |
| `created_at` / `updated_at` | `updated_at` | `TIMESTAMPTZ` | Timestamp of last modification |

### 2.2 Table: `"Transactions"`
| Existing Python Model / Schema Field | Supabase Target Column | Type | Constraints / Description |
|---|---|---|---|
| `transaction_id` | `transaction_id` | `TEXT` | UNIQUE INDEX, external deduplication key |
| `user_id` | `user_id` | `UUID` / `TEXT` | References `auth.users(id)` |
| `event_type` | `event_type` | `TEXT` | 'income', 'expense', 'refund', 'subscription' |
| `description` | `description` | `TEXT` | Transaction description / merchant |
| `category` | `category` | `TEXT` | Categorized spending bucket |
| `direction` | `direction` | `TEXT` | 'debit' or 'credit' |
| `amount` | `amount` | `NUMERIC(14,2)` | Positive numerical amount |
| `currency` | `currency` | `VARCHAR(10)` | Currency ISO |
| `event_date` | `event_date` | `DATE` | Transaction date |
| `settlement_date` | `settlement_date` | `DATE` | Optional settlement date |
| `status` | `status` | `TEXT` | 'SETTLED', 'PENDING' |
| `flexibility` | `flexibility` | `TEXT` | 'fixed', 'variable' |
| `ml_confidence` | `ml_confidence` | `FLOAT8` | Model confidence score (0.0 - 1.0) |
| `ml_status` | `ml_status` | `TEXT` | 'classified', 'rule_matched' |
| `ml_confidence_level` | `ml_confidence_level` | `TEXT` | 'high', 'medium', 'low' |
| `created_at` | `created_at` | `TIMESTAMPTZ` | Ingestion timestamp |

### 2.3 Table: `"Financial_Summaries"`
| Logical Model Field | Supabase Target Column | Type | Constraints / Description |
|---|---|---|---|
| `summary_id` | `summary_id` | `TEXT` | Primary key or unique identifier |
| `user_id` | `user_id` | `UUID` / `TEXT` | References `auth.users(id)` |
| `reporting_period` | `reporting_period` | `TEXT` | E.g., '2026-10' |
| `income` | `income` | `NUMERIC(14,2)` | Total period income |
| `expenses` | `expenses` | `NUMERIC(14,2)` | Total period expenses |
| `savings` | `savings` | `NUMERIC(14,2)` | Net savings |
| `savings_rate` | `savings_rate` | `FLOAT8` | Savings percentage |
| `cash_flow` | `cash_flow` | `NUMERIC(14,2)` | Net cash flow |
| `essential_expenses` | `essential_expenses` | `NUMERIC(14,2)` | Fixed obligations |
| `discretionary_expenses`| `discretionary_expenses` | `NUMERIC(14,2)` | Variable discretionary spend |
| `emi_burden` | `emi_burden` | `FLOAT8` | Debt / EMI service ratio |
| `summary_data` | `summary_data` | `JSONB` | Full categorized breakdown & anomaly list |
| `created_at` | `created_at` | `TIMESTAMPTZ` | Computation timestamp |

### 2.4 Table: `"Forecasts"`
| Logical Model Field | Supabase Target Column | Type | Constraints / Description |
|---|---|---|---|
| `forecast_id` | `forecast_id` | `TEXT` | Primary key or unique identifier |
| `user_id` | `user_id` | `UUID` / `TEXT` | References `auth.users(id)` |
| `forecast_period` | `forecast_period` | `TEXT` | Projected month, e.g. '2026-11' |
| `projected_income` | `projected_income` | `NUMERIC(14,2)` | Forecasted income |
| `projected_expenses` | `projected_expenses` | `NUMERIC(14,2)` | Forecasted variable expenses |
| `known_obligations` | `known_obligations` | `NUMERIC(14,2)` | Known commitments |
| `projected_cash_flow` | `projected_cash_flow` | `NUMERIC(14,2)` | Net projected cash flow |
| `uncertainty` | `uncertainty` | `FLOAT8` | Estimated variance / uncertainty |
| `confidence` | `confidence` | `FLOAT8` | Confidence score |
| `evaluation_mae` | `evaluation_mae` | `FLOAT8` | Mean Absolute Error from validation |
| `evaluation_rmse` | `evaluation_rmse` | `FLOAT8` | RMSE from validation |
| `forecast_data` | `forecast_data` | `JSONB` | Detailed ForecastResult & cash flow gap objects |
| `created_at` | `created_at` | `TIMESTAMPTZ` | Prediction timestamp |

### 2.5 Table: `"Monthly_Reports"`
| Logical Model Field | Supabase Target Column | Type | Constraints / Description |
|---|---|---|---|
| `report_id` | `report_id` | `TEXT` | Unique report identifier |
| `user_id` | `user_id` | `UUID` / `TEXT` | References `auth.users(id)` |
| `reporting_period` | `reporting_period` | `TEXT` | Current analysis period ('2026-10') |
| `previous_period` | `previous_period` | `TEXT` | Comparison baseline ('2026-09') |
| `report_data` | `report_data` | `JSONB` | Full deterministic comparison report structure |
| `storage_reference` | `storage_reference` | `TEXT` | Optional Supabase Storage file URL / path |
| `created_at` | `created_at` | `TIMESTAMPTZ` | Report generation timestamp |

---

## 3. Potential Integration Risks & Mitigations

1. **PostgreSQL Identifier Case Sensitivity**:
   Supabase tables created as `Profiles`, `Transactions`, `Financial_Summaries`, `Forecasts`, `Monthly_Reports` have mixed case and require double-quoting in SQL (`"Profiles"`). The Supabase Python client accepts exact table name strings `"Profiles"`.
2. **Missing Environment Variables in Production**:
   If `SUPABASE_URL` or key is missing, production must fail fast with a descriptive `RuntimeError`, rather than silently falling back to a local SQLite file.
3. **Automated Testing Reliability**:
   CI and developer testing environments must not fail when offline. We will provide an in-memory/mock repository mode for test suites while verifying strict cloud configuration when deployed.
4. **Statement Upload Deduplication**:
   Users re-uploading statement CSVs must not duplicate transactions. Deduplication is enforced by querying existing `transaction_id`s in batch before inserting new rows.
5. **Zero Trust Authentication**:
   Client-supplied `user_id` parameters in request bodies or query params will never be trusted for authorization. The authenticated user ID is strictly extracted from the validated access token claims.
