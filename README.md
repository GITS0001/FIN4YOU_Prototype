# FIN4YOU — Financial Health Copilot

A deterministic financial modeling and decision-support application powered by an AI conversational interface (Artha AI) and backed by Supabase PostgreSQL persistence.

## Problem Statement
Personal finance tools often look backwards at past spending without helping users make confident, forward-looking decisions. Users struggle to answer complex questions like "Can I afford this?" or "What happens if I reduce my dining budget?"

## Solution
FIN4YOU bridges the gap between historical tracking and future planning. It ingests transaction data, deterministically models next month's cash flow, and allows users to simulate the impact of their financial decisions before making them—all through an intuitive conversational Copilot layer (Artha AI).

---

## Key Features
- **Observed Financial State:** Tracks and categorizes historical income, expenses, and savings.
- **Probabilistic Cash-Flow Forecasting (Addition 2):** Projects multi-period income, essential/discretionary expenses, and cumulative balances across >= 6 months with prediction intervals and reserve shortfall risk estimation $P(\text{Balance} < \text{Reserve})$.
- **Constrained Financial Action Planning (Addition 1):** Compares candidate action sequences across >= 6 monthly periods, enforces declared cash reserve constraints, detects infeasible goals with explicit relaxation proposals, and selects risk-aware recommendations.
- **Affordability Engine:** Evaluates if a proposed purchase is viable outright or via installment plans without violating the user's minimum safety buffer.
- **What-If Simulator:** Models the impact of modified spending habits on future cash flow.
- **Artha AI (Copilot):** A conversational interface that routes natural-language questions to the correct mathematical engine and explains the structured result along with a transparent "Decision Trace".
- **Supabase Cloud Persistence:** Fully migrated from local SQLite to Supabase PostgreSQL with strict Row Level Security (RLS) data isolation and batch deduplication.

---

## Tech Stack
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Lucide Icons, Axios.
- **Backend:** Python 3.12, FastAPI, Pydantic v2, Uvicorn, Pytest.
- **Persistence & Cloud:** Supabase PostgreSQL, `supabase-py`, PostgREST.
- **AI/ML Components:** Algorithmic rolling-average forecasting, deterministic categorical matching, and rule-based anomaly detection.

---

## Supabase Integration & Architecture

### 1. Persistent Tables
The persistent application layer uses 5 tables in Supabase (with exact mixed-case quoting in PostgreSQL):
1. **`"Profiles"`**: User financial profile, currency, minimum safety buffer, and category preference strings.
2. **`"Transactions"`**: Granular financial transactions, amounts, dates, classifications, and deduplication IDs.
3. **`"Financial_Summaries"`**: Historical period-level financial aggregates (income, expenses, savings rate, cash flow, emi burden).
4. **`"Forecasts"`**: Forward-looking projection snapshots, projected cash flow, and model evaluation metrics.
5. **`"Monthly_Reports"`**: Deterministic month-over-month comparisons, anomaly summaries, and category trends.

### 2. Authentication & Data Isolation
- **Zero Trust Identity:** The backend never trusts client-supplied `user_id` parameters. The authenticated user ID is strictly extracted from verified JWT claims (`get_current_user` dependency).
- **Row Level Security (RLS):** All tables enforce PostgreSQL RLS policies where `auth.uid()::text = user_id`.
- **Deduplication:** CSV statement uploads use deterministic fingerprinting and batch deduplication against existing `transaction_id`s in Supabase, preventing duplicate insertions on re-uploads.

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description | Exposed to Frontend? |
|---|---|---|
| `SUPABASE_URL` | Your Supabase project URL (e.g. `https://xyz.supabase.co`) | Yes (Vite: `VITE_SUPABASE_URL`) |
| `SUPABASE_PUBLISHABLE_KEY` | Public client/anon key with RLS | Yes (Vite: `VITE_SUPABASE_ANON_KEY`) |
| `SUPABASE_SECRET_KEY` | Privileged service-role key for backend admin operations | **NO (Server-side ONLY)** |
| `DATABASE_URL` | Direct PostgreSQL connection string | **NO (Server-side ONLY)** |
| `SECRET_KEY` | JWT signing secret for native auth | **NO (Server-side ONLY)** |
| `ENVIRONMENT` | `production` (requires Supabase) or `development`/`test` | No |

> [!CAUTION]
> **Never expose `SUPABASE_SECRET_KEY` in frontend environment files or client bundles!**

---

## Database Setup & SQL Migrations

1. Open your **Supabase Dashboard** -> **SQL Editor**.
2. Run the safe schema migration script:
   - [docs/supabase_schema_migration.sql](docs/supabase_schema_migration.sql)
3. Apply Row Level Security (RLS) policies:
   - [docs/supabase_rls_policies.sql](docs/supabase_rls_policies.sql)

---

## How to Run

### Running Locally (Development)

#### 1. Backend
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (including supabase-py)
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --reload --port 8000
```
Backend API will be running at `http://localhost:8000`. Health check is available at `http://localhost:8000/health`.

#### 2. Frontend
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```
Frontend will be available at `http://localhost:5173`.

---

## Running Automated Tests
Run full backend test suite (53 tests covering configuration, authentication, Supabase persistence, deduplication, financial intelligence, probabilistic forecasting, and constrained action planning):
```bash
pytest tests/
```

To run individual specialized suites:
```bash
# Probabilistic forecasting & prediction intervals (>= 6 months)
pytest tests/test_probabilistic_forecasting.py -v

# Constrained action planner across 5 required scenarios
pytest tests/test_action_planner.py -v

# Supabase repository & RLS isolation tests
pytest tests/test_supabase_integration.py -v
```

### Testing Live Supabase Integration Safely
When live Supabase credentials are configured in your `.env`, run the safe verification script:
```bash
python backend/verify_supabase_live.py
```
This tests live connectivity against the `"Profiles"` table over HTTPS without exposing secrets or mutating user data.

---

## Troubleshooting Guide

### 1. `SupabaseConfigError: CRITICAL CONFIGURATION ERROR`
- **Cause:** `ENVIRONMENT=production` is set, but `SUPABASE_URL` or `SUPABASE_SECRET_KEY`/`SUPABASE_PUBLISHABLE_KEY` is missing.
- **Resolution:** Check your `.env` file and verify all Supabase credentials are populated.

### 2. `401 Unauthorized` / `Could not validate credentials`
- **Cause:** Expired, missing, or invalid Bearer token in the `Authorization` header.
- **Resolution:** Re-authenticate via `/api/auth/login` or ensure valid Supabase Auth session token is passed.

### 3. PostgreSQL relation `"Profiles"` does not exist
- **Cause:** Schema migration was not executed in the Supabase SQL editor.
- **Resolution:** Execute `docs/supabase_schema_migration.sql` in the Supabase Dashboard SQL Editor.

---

## Documentation Table

| Document | Description |
|---|---|
| [Supabase Migration Plan](docs/supabase_migration_plan.md) | Architectural audit and schema mapping manifesto |
| [Supabase SQL Schema](docs/supabase_schema_migration.sql) | Safe non-destructive table definitions |
| [Supabase RLS Policies](docs/supabase_rls_policies.sql) | Row Level Security policies for user isolation |
| [Authentication Security](docs/authentication_security.md) | Zero-trust authentication specifications |
| [PRD](docs/01_PRD.md) | Product requirements |
| [SRS](docs/02_SRS.md) | Software requirements |
| [System Architecture](docs/03_SYSTEM_ARCHITECTURE.md) | Technical architecture |
| [UI/UX](docs/04_UI_UX.md) | Interface and user flows |