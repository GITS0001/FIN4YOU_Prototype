# Product Requirements Document (PRD)
**FIN4YOU — Financial Health Copilot**

## 1. Product Overview
FIN4YOU is a smart, interactive prototype that empowers users to make data-driven financial decisions. Powered by deterministic financial engines and an AI intent router (Artha AI), the prototype allows users to track observed financial health, forecast upcoming cash flow, simulate the impact of purchases or expense reductions, and check the affordability of new obligations.

## 2. Problem Statement
**Problem Context:** Most personal finance tools are backward-looking (tracking past spending) or overly simplistic (budgeting spreadsheets). They fail to answer complex, forward-looking questions like "Can I afford this?" or "What happens if I change my spending habits?"
**Target Users:** Individuals seeking better control over their cash flow, looking to understand their financial standing, and requiring assistance in making safe spending decisions.
**User Pain Points:**
- Anxiety around large purchases and their impact on future stability.
- Lack of visibility into short-term (next month) cash-flow bottlenecks.
- Disconnected tools: transaction tracking is separate from decision modeling.

## 3. Product Vision & Goals
**Vision:** To build a proactive "Financial Decision Copilot" that replaces guesswork with deterministic math and easy-to-understand conversational guidance.
**Goals:**
- Provide clear visibility into observed and projected financial states.
- Enable safe scenario testing (What-If and Affordability analysis).
- Make financial analysis conversational via Artha AI.

## 4. Core Value Proposition
By combining real financial transaction data with a deterministic prediction and decision engine, FIN4YOU provides objective, mathematical answers to complex financial questions, explained through a natural language copilot.

## 5. MVP Scope (Implemented Features)
- **Financial State Engine:** Aggregates raw transactions into income, expenses, savings, and expense ratios.
- **Forecasting Engine:** Projects next month's cash flow based on observed historical averages and known upcoming obligations.
- **Decision Engine (Affordability):** Evaluates if a user can afford a purchase based on current balance, minimum buffer, and projected cash flow. Recommends payment options (e.g., installments).
- **Decision Engine (What-If Simulator):** Simulates modifications to the baseline financial state (reducing expenses or adding purchases) and computes the delta/impact.
- **Artha AI (Copilot Layer):** Parses natural language intents, invokes the appropriate deterministic backend engine, and presents structured financial results.
- **UI/UX Dashboard:** A responsive React-based interface presenting insights, anomalies, and financial statements.

## 6. User Stories & Journeys
- **Story 1:** As a user, I want to see my current financial health so I know if I'm spending too much.
- **Story 2:** As a user, I want to ask Artha AI if I can afford an iPhone for ₹80,000, so I know if it will break my minimum balance buffer.
- **Story 3:** As a user, I want to simulate spending 20% less on dining to see how it improves my cash flow.
- **Journey (Affordability Check):** User navigates to Copilot → Asks "Can I afford a ₹1,302 purchase?" → Intent is parsed → Affordability Engine runs → User sees structured breakdown of cash flow impact and a recommendation.

## 7. Assumptions & Risks
- **Assumptions:** Data provided (prototype CSVs) is accurate and standardized. Next-month projections assume recent historical averages remain relatively constant.
- **Risks:** Users might mistake deterministic short-term projections for guaranteed long-term outcomes.
- **Limitations:** Only supports 1-month forward projections. Does not include investment tracking or long-term wealth modeling. 

## 8. Out-of-Scope Features
- Live bank feeds (Plaid/Yodlee integration).
- Multi-month or multi-year retirement forecasting.
- Generative AI providing arbitrary financial advice (all advice is strictly bound to deterministic engine outputs).
- User authentication, PostgreSQL database, or cloud state persistence (currently operates in-memory for the prototype).

## 9. Success Metrics / Acceptance Criteria
- [x] Copilot correctly maps natural language to correct financial engine endpoints.
- [x] Affordability engine accurately flags purchases that violate the minimum balance buffer.
- [x] What-If engine accurately calculates the impact of modified spending.
- [x] The UI successfully reflects global state changes (e.g., changing profile settings updates the dashboard instantly).
- [x] Financial math is performed strictly on the backend and is deterministic.
