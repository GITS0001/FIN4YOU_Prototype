# FIN4YOU — Financial Health Copilot

A deterministic financial modeling and decision-support prototype powered by a conversational interface (Artha AI). 

## Problem Statement
Personal finance tools often look backwards at past spending without helping users make confident, forward-looking decisions. Users struggle to answer complex questions like "Can I afford this?" or "What happens if I reduce my dining budget?"

## Solution
FIN4YOU bridges the gap between historical tracking and future planning. It ingests transaction data, deterministically models next month's cash flow, and allows users to simulate the impact of their financial decisions before making them—all through an intuitive conversational Copilot layer (Artha AI).

## Key Features
- **Observed Financial State:** Tracks and categorizes historical income, expenses, and savings.
- **Deterministic Forecasting:** Projects next month's cash flow by analyzing past variable spending and identifying recurring fixed obligations.
- **Affordability Engine:** Evaluates if a proposed purchase is viable outright or via installment plans without violating the user's minimum safety buffer.
- **What-If Simulator:** Models the impact of modified spending habits on future cash flow.
- **Artha AI (Copilot):** A conversational interface that routes natural-language questions to the correct mathematical engine and explains the structured result along with a transparent "Decision Trace".

## Product Flow & Architecture Overview
**User → React Frontend → FastAPI → Artha AI (Intent Router) → Deterministic Engines → Structured Explanation → User**

FIN4YOU relies on a decoupled architecture. The frontend acts purely as a presentation layer. The backend acts as the source of truth, performing all mathematical logic and simulations over the ingested prototype dataset.

## Tech Stack
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Lucide Icons.
- **Backend:** Python 3.12, FastAPI, Pydantic, Uvicorn, Pytest.
- **AI/ML Components:** The prototype uses algorithmic rolling-average forecasting, deterministic categorical matching, and rule-based anomaly detection. The conversational layer parses user intents and maps them to these deterministic endpoints.

## Known Limitations (Prototype Context)
- Data is loaded from static CSV files (`data/prototype/`) and stored in memory.
- Multi-month or long-term retirement modeling is not supported; predictions look 1-month forward.
- The prototype currently runs in a single-user mode (`user_28` / Aditya) without active database persistence (PostgreSQL) or OAuth integration.

## Project Structure
```text
FIN4YOU_Frontend_Test/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/              # Route controllers
│   │   ├── copilot/          # Artha AI Intent router & response generator
│   │   ├── decision/         # Affordability & Simulation engines
│   │   ├── financial/        # Financial state calculation
│   │   ├── ingestion/        # CSV Data loaders
│   │   ├── ml/               # Forecasting engine
│   │   └── schemas/          # Pydantic typing
│   ├── data/prototype/       # Static datasets
│   └── tests/                # Pytest suites
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── api/              # Axios API clients
│   │   ├── components/       # Shared UI components (Sidebar, Topbar, CopilotChat)
│   │   ├── context/          # Global state management
│   │   ├── pages/            # Dashboard, Forecast, Affordability, etc.
│   │   └── types/            # TypeScript interfaces
└── docs/                     # Project documentation
```

## How to Run

### Backend
1. Open a terminal and navigate to the `backend` directory.
2. Ensure you have Python 3.12 installed.
3. Install dependencies: `pip install -r requirements.txt`
4. Start the server: `uvicorn app.main:app --reload --port 8000`
5. The API will be available at `http://localhost:8000`.

### Frontend
1. Open a terminal and navigate to the `frontend` directory.
2. Install dependencies: `npm install`
3. Start the development server: `npm run dev`
4. The application will be available at `http://localhost:5173`.

### Testing
- Backend unit and integration tests: `python3.12 -m pytest -q`
- Frontend type checking: `npx tsc --noEmit`
- Frontend production build check: `npm run build`

## Example User Journey
1. Navigate to the **Dashboard** to view high-level KPIs and warnings (e.g., "Cash Flow Pressure").
2. Open **Artha AI** via the sidebar or top navigation.
3. Ask: *"Can I afford a new iPhone for ₹80,000?"*
4. View the structured response detailing if it breaks your minimum balance buffer, alongside safe 3, 6, or 12-month installment recommendations.
5. Click **Decision Trace** to inspect the exact math used by the backend engine.

## Documentation Table

| Document | Description |
|---|---|
| [PRD](docs/01_PRD.md) | Product requirements |
| [SRS](docs/02_SRS.md) | Software requirements |
| [Architecture](docs/03_SYSTEM_ARCHITECTURE.md) | Technical architecture |
| [UI/UX](docs/04_UI_UX.md) | Interface and user flows |
| [Development Plan](docs/05_DEVELOPMENT_PLAN.md) | Development roadmap |
| [Final Audit](docs/GITHUB_DOCUMENTATION_AUDIT.md) | Final system validation and checklist |

---
*Built for the HackMatrix Evaluation.*