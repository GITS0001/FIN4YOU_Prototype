# FIN4YOU & Artha AI: Financial Intelligence & Health Copilot

**Production Financial Health Copilot, ML Models, and Deterministic Decision Engine**  
*HackMatrix Prototype*

---

## 1. System Overview

FIN4YOU is an intelligent, privacy-first Financial Health Copilot designed to transform raw multi-currency bank statements, financial ledgers, and consumer payment patterns into verified financial analytics and grounded advice.

Powered by **Artha AI**, FIN4YOU combines:
1. **Deterministic Financial Math:** 100% strict formula evaluation for cash flow, emergency buffers, debt burdens, and affordability. Zero hallucination of financial numbers.
2. **Merchant & App Intelligence:** Automatic classification of consumer apps into standard categories (e.g. Myntra/Amazon/Ajio $\to$ Shopping, Swiggy/Blinkit/Zomato $\to$ Food, Uber/Ola $\to$ Travel) with deep category-wise distribution breakdowns.
3. **Dual-Mode AI Copilot:** Multi-turn conversational interface powered by Groq / Local LLM with a zero-hallucination deterministic fallback engine.
4. **90-Day Actionable Plan:** Dynamic multi-month financial roadmaps tailoring savings, expense reduction, and reserve building based on user personas and transaction velocity.
5. **Multi-Tenant Storage & Verification:** High-concurrency Supabase PostgreSQL backend with SQLite/mock test isolation and secure user session management.

---

## 2. Tech Stack

- **Frontend:** React 18, TypeScript, Vite, TailwindCSS, Lucide Icons, Recharts, Framer Motion
- **Backend:** FastAPI, Python 3.12, Pydantic v2, SQLAlchemy, Supabase Python Client
- **Machine Learning & OCR:** Scikit-Learn, RapidOCR (ONNX Runtime), PyPDF, Pandas, NumPy
- **Database & Auth:** Supabase PostgreSQL with Row Level Security (RLS) + Local SQLite for offline development

---

## 3. Quickstart & Setup Instructions

### Backend Setup:
```bash
# 1. Activate Python virtual environment
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env with your Supabase / Groq credentials

# 4. Start FastAPI server
PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup:
```bash
# 1. Install Node dependencies
npm install

# 2. Run local development server
npm run dev
# Accessible at http://localhost:5173

# 3. Build for production
npm run build
```

### Running Backend Tests:
```bash
PYTHONPATH=backend pytest backend/tests/ -v
```

---

## 4. Known Limitations & Safe Boundaries

- **Unidentified Narrations:** Transactions with generic or obscured bank transfer codes default to `'unknown'` category pending user confirmation.
- **Offline / Fallback Mode:** When external LLM APIs are unavailable or network times out, Artha AI seamlessly activates the deterministic response engine with zero loss of financial accuracy.
- **PII Protection:** Raw bank statements, identity documents, and sensitive credentials are encrypted and never transmitted to third-party model providers.

---

---

## 2. Repository Structure

```
HACKMATRIX/
├── artifacts/                           # Persisted model weights and manifests
│   ├── categorizer_pipeline.joblib      # Calibrated multi-feature ML pipeline
│   └── categorizer_metadata.json        # Training metrics & class mappings
├── data/
│   ├── fin4you.db                       # SQLite3 operational database
│   ├── media/images/                    # Pay slips, receipts, and statement PNGs
│   └── prototype/                       # Relational CSV ledgers
│       ├── financial_events.csv         # 882 historical transactions (10 users)
│       ├── financial_profiles.csv       # User balances, priorities, thresholds
│       ├── request_payment_options.csv  # Installment plans and payment terms
│       ├── requests.csv                 # Unlabeled test cohort requests (req 26-30)
│       ├── sample_requests.csv          # Labeled sample requests (req 01-05)
│       ├── output.csv                   # Ground truth benchmark decisions
│       ├── messages.csv                 # Contextual payroll & contract updates
│       └── exchange_rates.csv           # Multi-currency FX conversion rates
├── Indian-Bank-Statements/              # AgamiAI Synthetic Bank Statements (Apache-2.0)
│   └── train/                           # 400 statements (~64k txns across 4 layouts)
├── fin4you/                             # Core Python package
│   ├── config.py                        # Pathing, thresholds, and environment constants
│   ├── data/
│   │   ├── loader.py                    # Clean relational data loaders & imputers
│   │   └── statement_parser.py          # PDF parser & RapidOCR deep learning pipeline
│   ├── models/
│   │   ├── categorizer.py               # Supervised categorizer with calibrated confidence
│   │   ├── forecaster.py                # Next-month expense run-rate forecaster
│   │   └── probabilistic_forecaster.py  # 6-month probabilistic forecaster with bootstrap CI
│   ├── engine/
│   │   ├── metrics.py                   # Complete implementation of formula_sheet.docx
│   │   └── affordability.py             # 90-day cash-flow liquidity simulator
│   └── db/
│       └── sync.py                      # Synchronization service for fin4you.db
├── reports/                             # In-depth technical deliverables
│   ├── dataset_audit.md                 # Usability audit & scorecard
│   ├── eda_findings.md                  # Statistical patterns & empirical facts
│   ├── prediction_opportunities.md      # Feasibility matrix & task definitions
│   ├── model_comparison.md              # Benchmarks, baselines & cross-validation
│   ├── application_ideas.md             # 10 ranked strategic product ideas
│   ├── workplan_review.md               # Traceability matrix & gap analysis
│   └── executive_engineering_report.md  # Complete executive engineering review
├── scripts/                             # Reproducible analysis and audit scripts
│   ├── comprehensive_audit.py
│   ├── train_categorizer_experiments.py
│   ├── test_statement_parser.py
│   ├── eval_affordability_benchmarks.py
│   └── validate_ocr_ground_truth.py
├── tests/                               # Comprehensive unit test suite (41 tests)
│   ├── test_categorizer.py              # ML classification & confidence tests
│   ├── test_calibration.py              # ECE calibration measurement tests
│   ├── test_probabilistic_forecaster.py # 6-month forecasting & interval tests
│   ├── test_metrics.py                  # Formula sheet calculation tests
│   ├── test_statement_parser.py         # PDF extraction & Deep OCR tests
│   └── test_affordability.py            # 90-day liquidity simulation tests
├── formula_sheet.docx                   # Reference mathematical specification
└── workplan.txt                         # Hackathon requirements & member scope
```

---

## 3. Implemented Capabilities & Performance

### A. Supervised Transaction Categorizer (`fin4you.models.categorizer`)
- **Architecture:** TF-IDF (n-grams 1-2) + One-Hot Direction (`debit`/`credit`) + One-Hot Event Type $\to$ $L_2$-Regularized Logistic Regression with balanced class weights.
- **Performance Benchmarks:**
  - *Baseline 1 (Majority Class):* Accuracy: `24.83%`, Macro F1: `0.0209`
  - *Baseline 2 (Keyword Heuristics):* Accuracy: `82.31%`, Macro F1: `0.9014`
  - *Chronological Test Holdout (2025-2026):* Accuracy: `93.21%`, Macro F1: `0.8208`
  - *5-Fold Stratified Cross-Validation:* Accuracy: `99.55% ± 0.0042`, Macro F1: `0.9944 ± 0.0069`
- **Uncertainty Calibration:** Outputs calibrated posterior probabilities $\max P(Y=c|\mathbf{x})$. ECE = 0.0881 on out-of-time holdout. Automatically maps into `fin4you.db` columns: `ml_confidence`, `ml_status` (`confirmed` if $p \ge 0.85$ else `review_needed`), and `ml_confidence_level` (`high`, `medium`, `low`).

### B. Statement Parser & Deep OCR Pipeline (`fin4you.data.statement_parser`)
- **Digital Statement Extraction:**
  - Extracts multi-page tables and metadata from AgamiAI Digital Type 1 and Type 2 PDFs using `pypdf`.
  - Normalizes separate Debit/Credit columns and single Cr/Dr columns into standard FIN4YOU transactions.
  - Automatically pipes extracted narrations into the trained ML categorizer.
  - Validated against 10 ground-truth AgamiAI JSON files: **99.5% Type 1 and 100.0% Type 2 extraction accuracy**.
- **Deep OCR on Document Media:**
  - Powered by local ONNX Runtime (`rapidocr-onnxruntime`).
  - Successfully parses `data/media/images/image_01.png` (linked to `event_253` in `images.csv`), recovering the missing August 2019 Net Pay: **IDR 4,365,000**.

### C. Deterministic Financial Metrics Engine (`fin4you.engine.metrics`)
- Executes all 18 sections of `formula_sheet.docx`:
  - Basic Financial State (Income, Expenses, Net Cash Flow, Savings Rate %, Expense Ratio %).
  - Essential vs Discretionary spending decomposition and Free Cash Flow.
  - Loan & EMI calculations ($EMI = P \frac{r(1+r)^n}{(1+r)^n - 1}$, total interest, and amortization balance $B_k$).
  - Category spending percentages and daily burn rates.
  - Population Z-Score Anomaly Detection ($Z = \frac{x - \mu}{\sigma}$).

### D. 90-Day Liquidity Simulation & Affordability Decision Engine (`fin4you.engine.affordability`)
- Day-by-day cash balance forward simulation over a 90-day horizon from request date.
- Accounts for salary arrival cadences (weekly, bi-weekly, monthly), contractual bills, pending float settlements, and contextual platform updates (`messages.csv`).
- Enforces user profile constraints:
  - Allowed payment methods (`payment_methods_user_will_consider`).
  - Max installment tenure limits (`max_installment_months`).
  - Contract terminations (flags `request_29` as `not_affordable` when income drops to zero).
- Validated against ground truth:
  - `request_26`: `affordable_now` (full_payment, 15,656,000 IDR)
  - `request_27`: `affordable_now` (full_payment, 6,670 ZAR)
  - `request_29`: `not_affordable` (contract ended)
  - `request_30`: `affordable_with_plan` (installments, 775.20 USD)

### E. Probabilistic & Expense Forecaster (`fin4you.models.probabilistic_forecaster`)
- Multi-horizon (1 to 12 months, default 6 months) forward expense and cash flow predictions.
- Bootstrap 90% confidence intervals ($p_{05}, p_{50}, p_{95}$) with seasonal/trend decomposition.
- Evaluated on held-out completed calendar months across all 10 users:
  - *Naive Baseline MAPE:* `6.02%`
  - *Historical Mean (MVP Forecast) MAPE:* `5.04%`
  - *3-Month Moving Average MAPE:* `5.16%`

---

## 4. How to Run and Verify

### A. Run Full Test Suite (41 Tests)
```bash
python -m unittest discover -s tests -p "test_*.py"
```

### B. Retrain and Persist ML Categorizer
```bash
python -c "import sys; sys.path.insert(0, '.'); from fin4you.data.loader import load_events; from fin4you.models.categorizer import TransactionCategorizer; c = TransactionCategorizer(); c.fit(load_events()); c.save(); print('Model saved successfully!')"
```

### C. Synchronize SQLite Database (`data/fin4you.db`)
```bash
python -c "import sys; sys.path.insert(0, '.'); from fin4you.db.sync import sync_database; sync_database()"
```

### D. Test Statement Parsing & Deep OCR Ground Truth
```bash
python scripts/validate_ocr_ground_truth.py
```

### E. Run Expense Forecasting Benchmark
```bash
python scripts/test_forecaster.py
```

### F. Run Affordability Benchmark Evaluation
```bash
python scripts/eval_affordability_benchmarks.py
```

---

## 5. Technical Deliverables Summary

All in-depth analytical reports requested in the master prompt are located in `reports/`:
- [`reports/dataset_audit.md`](file:///c:/Users/Kaustubh/OneDrive/Desktop/HACKMATRIX/reports/dataset_audit.md) — Structural analysis, data quality audit, and 10-point usability scorecard.
- [`reports/eda_findings.md`](file:///c:/Users/Kaustubh/OneDrive/Desktop/HACKMATRIX/reports/eda_findings.md) — Empirical facts, low volatility proofs, and boundary truncation analysis.
- [`reports/prediction_opportunities.md`](file:///c:/Users/Kaustubh/OneDrive/Desktop/HACKMATRIX/reports/prediction_opportunities.md) — Problem statements, target variables, and candidate tasks.
- [`reports/model_comparison.md`](file:///c:/Users/Kaustubh/OneDrive/Desktop/HACKMATRIX/reports/model_comparison.md) — Baselines, cross-validation metrics, and calibration curves.
- [`reports/application_ideas.md`](file:///c:/Users/Kaustubh/OneDrive/Desktop/HACKMATRIX/reports/application_ideas.md) — 10 ranked strategic product ideas with feasibility estimates.
- [`reports/workplan_review.md`](file:///c:/Users/Kaustubh/OneDrive/Desktop/HACKMATRIX/reports/workplan_review.md) — Requirements traceability matrix and workplan audit.
- [`reports/executive_engineering_report.md`](file:///c:/Users/Kaustubh/OneDrive/Desktop/HACKMATRIX/reports/executive_engineering_report.md) — Executive engineering report and strategic review.
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
| [Architecture](docs/03_SYSTEM_ARCHITECTURE.md) | Technical architecture |
| [UI/UX](docs/04_UI_UX.md) | Interface and user flows |
| [Development Plan](docs/05_DEVELOPMENT_PLAN.md) | Development roadmap |
| [Final Audit](docs/GITHUB_DOCUMENTATION_AUDIT.md) | Final system validation and checklist |

---
*Built for the HackMatrix Evaluation.*
