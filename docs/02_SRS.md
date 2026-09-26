# Software Requirements Specification (SRS)
**FIN4YOU — Financial Health Copilot**

## 1. System Overview
FIN4YOU is a full-stack web application consisting of a React-based frontend and a FastAPI (Python) backend. The system acts as a deterministic financial modeling layer wrapped in a conversational AI interface. 

## 2. Functional Requirements

### 2.1 Data Requirements & Validation
- **Requirement:** The system MUST load predefined user profiles and transaction events from static CSV datasets (`data/prototype/`).
- **Validation:** The system MUST validate financial profiles against the `FinancialProfile` schema (e.g., enforcing required fields like `current_available_balance`, `minimum_balance_to_keep`).
- **Constraint:** Missing or incomplete transaction history for a user MUST result in gracefully degraded outputs (e.g., 0 observed months) rather than fatal crashes.

### 2.2 Financial State Calculation (Observed Fact)
- **Requirement:** The `FinancialStateEngine` MUST aggregate historical transactions into categorical buckets: Income, Variable Expenses, and Known Obligations.
- **Rules:** The system MUST calculate `savings` as `total_income - total_expenses` and `expense_ratio` as `total_expenses / max(total_income, 1)`.

### 2.3 Forecasting & Prediction (Model Prediction)
- **Requirement:** The `PredictionEngine` MUST forecast the next month's cash flow.
- **Rules:** 
  - Variable expenses are forecasted using a rolling average of past months.
  - Upcoming fixed obligations are deterministically identified from the recurring transactions logic.
  - `projected_cash_flow` = `projected_income - (projected_expenses + upcoming_obligations)`.

### 2.4 Decision Engine: Affordability & Payment Options (Scenario)
- **Requirement:** The `AffordabilityEngine` MUST determine if a user can afford a proposed purchase amount.
- **Rules:**
  - **Can afford outright:** If `current_available_balance - purchase_amount >= minimum_balance_to_keep` AND `projected_cash_flow > 0`.
  - **Can afford in installments:** If outright fails, the system divides the cost by 3, 6, or 12 months. An installment is viable if `projected_cash_flow - monthly_installment > 0`.
  - **Cannot afford:** If all options violate the minimum buffer or result in negative cash flow.

### 2.5 Decision Engine: What-If Simulator (Simulation & Impact)
- **Requirement:** The `WhatIfSimulator` MUST allow users to model adding an expense or reducing spending in a specific category.
- **Rules:** The simulator MUST return a `ScenarioResult` comparing the `baseline` cash flow against the `scenario` cash flow, and generate an `ExpectedImpact` delta (e.g., +X% improvement in cash flow).

### 2.6 Copilot Intent Routing
- **Requirement:** The `CopilotOrchestrator` MUST parse natural language via the `IntentParser` to identify user intents (e.g., `AFFORDABILITY_CHECK`, `WHAT_IF_ANALYSIS`, `FINANCIAL_SUMMARY`).
- **Constraint:** The Copilot layer MUST NOT perform any financial calculations itself. It strictly extracts parameters (e.g., amount), invokes the deterministic engines, and wraps the structured results in a conversational explanation.

### 2.7 Frontend Requirements
- **Requirement:** The React frontend MUST strictly act as a presentation layer. It MUST NOT compute financial values natively.
- **Requirement:** The frontend MUST utilize a Global Context to ensure cross-page reactivity when profile parameters (like available balance) are modified.

## 3. Non-Functional Requirements
- **Performance:** Financial calculations (being purely mathematical over limited datasets) MUST execute in <200ms to ensure a snappy Copilot experience.
- **Security:** The system MUST NOT log sensitive raw transaction values in plain text if deployed, though the current prototype runs in-memory securely.
- **Edge Cases & Error Handling:**
  - **Invalid Users:** Requesting a non-existent user MUST return a standard HTTP 404.
  - **Insufficient History:** Users with 0 transactions MUST display a "No history available" empty state.
  - **Currency:** The system MUST rely on the user's `home_currency` field for formatting and avoid hardcoded currency symbols in the backend logic.

## 4. Output Typology Definitions
To ensure analytical clarity, the system output is strictly classified as:
- **OBSERVED FACT:** Historical, mathematical aggregation of past transactions.
- **MODEL PREDICTION:** Statistical or deterministic extrapolation of next month's state.
- **SCENARIO/SIMULATION:** User-defined adjustments to the baseline prediction.
- **RECOMMENDATION:** Hard-coded logical outputs based on simulation constraints (e.g. "Use 3-month installments").
- **EXPECTED IMPACT:** The mathematical delta between Baseline and Scenario.
- **CONFIDENCE:** The system's self-assessed reliability of the prediction based on historical variance.
