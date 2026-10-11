# FIN4YOU Demonstration Runbook & Architecture Verification

**Project**: FIN4YOU — Financial Health Copilot  
**Demonstration Mode**: Live Hackathon Showcase  
**Target Environment**: Local FastAPI Backend + Vite React Frontend with Supabase Integration

---

## 1. Startup Commands

### Backend Startup
```bash
# From workspace root
source .venv/bin/activate
cd backend
uvicorn app.main:app --reload --port 8000
```
- **Base URL**: `http://localhost:8000`
- **Swagger Documentation**: `http://localhost:8000/docs`

### Frontend Startup
```bash
# From workspace root
npm run dev
```
- **Application URL**: `http://localhost:5173`

---

## 2. Required Environment Variables
The following environment variables are required in `.env` (secrets omitted):
- `DATABASE_URL`: SQLite connection URI (`sqlite:///./fin4you.db`)
- `SECRET_KEY`: JWT session signing key
- `SUPABASE_URL`: Remote Supabase project URL
- `SUPABASE_ANON_KEY`: Supabase client anonymous API key
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase administrative role key for batch sync
- `GROQ_API_KEY`: Groq API key for LLaMA 3.3 financial reasoning (system automatically falls back to deterministic financial engine if unconfigured)
- `VITE_API_URL`: Frontend API target (`http://localhost:8000`)

---

## 3. Health-Check Procedure

Verify backend operational health:
```bash
curl -s http://localhost:8000/health
```
**Expected Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "supabase_connected": true,
  "ml_model_loaded": true,
  "copilot_provider": "groq"
}
```

---

## 4. End-to-End Demonstration Workflow

### Step 1: User Sign Up & Authentication
1. Navigate to `http://localhost:5173`.
2. Click **Sign In** or **Get Started** in the top navigation bar.
3. Fill in email, password, and full name on the Registration tab.
4. Input the provided verification OTP to log in.
5. Notice that the top navbar immediately reflects your authenticated state with your **User Avatar / Username Menu**.
6. Refresh the page: the session seamlessly persists without forcing re-login.

### Step 2: Upload Bank Statement
1. Click **Dashboard** in the header or user dropdown menu.
2. Under **Upload Statement**, upload a supported CSV statement (e.g., standard column headers: `date`, `description`, `amount`, `direction` or `type`).
3. The upload pipeline parses transactions, normalizes debit/credit/refund directions, executes ML categorization, and persists transactions to the user account with SHA-256 deduplication.

### Step 3: Verified Financial Dashboard & Calculations
1. The dashboard figures update deterministically from saved user transactions:
   - **Total Monthly Income**
   - **Total Monthly Expenses** (properly netting refunds rather than treating them as income)
   - **Net Cash Flow & Savings**
   - **Category-wise Spending Breakdown**
2. In the transactions table, notice that transactions display predicted ML categories and confidence levels.

### Step 4: Insights & Forecasting
1. **Financial Insights**: Generated deterministically based on actual observed spending ratios, high-value expense alerts, and recurring obligations.
2. **Forecasting**: Visualizes observed transaction history and linear/trend projection. If historical data spans fewer than 3 months, the system displays an honest educational state explaining that additional history is needed for reliable predictive modeling.

### Step 5: What-If Scenario Simulator
1. Navigate to the **What-If Simulator** card.
2. Choose a scenario: e.g. "Reduce Expenses" by ₹2,000 or "Take a New Loan EMI".
3. Click Simulate: The calculation recalculates outputs using the user's real financial baseline (e.g. ₹23,000 cash flow baseline increases to ₹25,000 with a ₹2,000 expense reduction).

### Step 6: Artha AI Financial Copilot
1. Click on the Artha AI Copilot tab or chat drawer.
2. Ask a question: *"What is my total monthly income?"* or *"Analyze my spending habits."*
3. Artha AI delivers a formatted response grounded strictly in the user's verified backend figures with clear Markdown headers, bullet points, and disclaimer.

---

## 5. Automated Regression Test Execution

Run the complete backend regression suite:
```bash
source .venv/bin/activate
cd backend
pytest -v
```
**Verification Status**: All 25 tests pass.

---

## 6. Known Limitations & Unverified Features
1. **Scanned PDF OCR**: Text-based PDFs with digital font streams (`pdfplumber` / `pypdf`) are fully supported. Scanned image-only PDFs without text layers require Tesseract OCR which is not bundled; an informative validation error is raised to the user.
2. **Multi-Year History for Sparse Data**: Accounts with fewer than 3 months of statement history will show baseline observed metrics with an informative notice rather than fabricated multi-year forecasts.
