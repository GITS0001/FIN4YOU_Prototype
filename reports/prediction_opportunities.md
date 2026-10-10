# Prediction Opportunities & Analytical Task Feasibility: FIN4YOU & Artha AI

**Date:** 2026-10-10  
**Authors:** Senior ML Engineer & Financial AI Researcher  
**Corpus Root:** `c:\Users\Kaustubh\OneDrive\Desktop\HACKMATRIX`

---

## 1. Executive Summary

This report evaluates candidate predictive and analytical tasks against the empirical evidence available in the FIN4YOU repository. Each task is analyzed for data availability, ground-truth label validity, algorithmic viability, business impact, and key technical risks.

We identify three high-value feasible opportunities and contrast them with four unfeasible or data-deficient tasks that must not be attempted without additional ground truth.

---

## 2. High-Value Feasible Prediction Tasks

### Opportunity 1: Transaction Categorization with Calibrated Uncertainty (Supervised Classification)
- **Problem Statement:**  
  Given raw transaction strings (e.g. from bank statement uploads, manual input, or aggregator webhooks), classify each transaction into one of 19 standardized budget categories and output a well-calibrated confidence score to flag ambiguous entries for user review.
- **Target Variable & Horizon:**  
  `category` (19 classes: groceries, transport, dining, salary, utilities, rent, shopping, cloud_storage, entertainment, streaming, education, healthcare, debt_repayment, music_subscription, delivery_membership, housing, insurance, gym, family_support). Prediction horizon is immediate (per-transaction inference).
- **Input Features:**  
  Transaction `description` (n-grams), transaction `direction` (debit vs credit), `event_type` (expense, subscription, debt_payment, income, refund), and normalized amount magnitude ($\log(1 + \text{amount})$).
- **Ground Truth Labels:**  
  882 verified labeled records in `data/prototype/financial_events.csv`.
- **Baseline:**  
  - Baseline 1 (Zero-rule / Majority Class): Groceries (Accuracy: 24.83%, Macro F1: 0.0209).
  - Baseline 2 (Regex / Keyword Rule Matcher): Keyword dictionary lookup (Accuracy: 82.31%, Macro F1: 0.9014).
- **Candidate Algorithms:**  
  - TF-IDF + Multinomial Naive Bayes.
  - TF-IDF + Calibrated Logistic Regression ($L_2$ regularization).
  - Linear Support Vector Classifier with Platt scaling (`CalibratedClassifierCV`).
  - Random Forest Classifier (100 trees).
- **Evaluation Metrics:**  
  Accuracy, Macro Precision, Macro Recall, Macro F1-score, Log-Loss, Expected Calibration Error (ECE), and per-class confusion matrices.
- **Practical Application & User:**  
  Core data ingestion engine for FIN4YOU. Automatically maps statement uploads into `fin4you.db` and populates `ml_confidence`, `ml_status`, and `ml_confidence_level`.
- **Limitations & Data Gaps:**  
  Synthetic descriptions have cleaner token distributions than messy real-world SMS alerts or OCR scans. Continuous fine-tuning with real statement corpora (e.g., AgamiAI Indian Bank Statements) is recommended for production deployment.

---

### Opportunity 2: 90-Day Liquidity Simulation & Affordability Decision Engine (Decision Optimization)
- **Problem Statement:**  
  Given a user's financial profile, snapshot available balance, minimum safe buffer, candidate financing options, and upcoming recurring commitments, simulate forward-looking cash balances across a 90-day trajectory. Determine whether a requested expenditure is affordable now, affordable with an installment plan, affordable at a future date, or unaffordable without breaching minimum liquidity.
- **Target Variables:**  
  `affordability_status` (`affordable_now`, `affordable_with_plan`, `affordable_later`, `not_affordable`), `recommended_payment_method` (`full_payment`, `installments`, `wait`, `not_recommended`), `amount_safe_to_pay`, `earliest_date_for_full_payment`, `payment_plan`.
- **Input Features:**  
  `current_available_balance`, `minimum_balance_to_keep`, request date, requested amount, candidate payment option schedules (`request_payment_options.csv`), recurring income cadence and fixed obligations, and contextual platform updates (`messages.csv`).
- **Ground Truth Labels:**  
  Labeled sample requests in `sample_requests.csv` (requests 01-05) and benchmark ground truth in `output.csv` (requests 26-30).
- **Baseline:**  
  Static Balance Heuristic:  
  $$\text{Affordable Now} \iff (\text{current\_available\_balance} - \text{requested\_amount}) \ge \text{minimum\_balance\_to\_keep}$$
  (Fails on 60% of cases because it ignores upcoming bills, pending float, and installment feasibility).
- **Candidate Algorithms:**  
  Deterministic day-by-day discrete event cash-flow simulator executing formulas from `formula_sheet.docx` combined with constraint-satisfaction plan selection.
- **Evaluation Metrics:**  
  Classification accuracy on `affordability_status` and `recommended_payment_method`, Mean Absolute Error on `amount_safe_to_pay`, exact match on `payment_plan` schedule strings.
- **Practical Application & User:**  
  Primary consumer-facing copilot for FIN4YOU / Artha AI. Answers user financial dilemma queries ("Can I afford this laptop/trip/investment?") with safe mathematical guarantees.
- **Limitations & Data Gaps:**  
  Relies on predictable forward schedules; unannounced sudden shocks are modeled as sensitivity buffers rather than deterministic forecasts.

---

### Opportunity 3: Run-Rate & Recurring Next-Month Expense Forecasting (Regression / Time Series)
- **Problem Statement:**  
  Predict total expenditures and discretionary category spend for the upcoming 30-day period per user to provide proactive budget headroom warnings.
- **Target Variable & Horizon:**  
  Next-month total debit spending ($Expenses_{t+1}$) and category-level discretionary spending ($Dining_{t+1}, Transport_{t+1}, Shopping_{t+1}$). Prediction horizon: 30 days ahead.
- **Input Features:**  
  Historical 30-day and 60-day moving averages, known active subscriptions and contractual obligations, current month-to-date elapsed spending, and run-rate velocity.
- **Ground Truth Labels:**  
  Sequential monthly aggregates across the 50 complete user-months in `financial_events.csv`.
- **Baseline:**  
  - Baseline 1: Naive (previous month's total expense).
  - Baseline 2: Historical All-Time Mean (`formula_sheet.docx` MVP forecast).
- **Candidate Algorithms:**  
  - Decomposed Schedule + Run-Rate Engine ($Fixed + Daily\_Variable\_Rate \times Days$).
  - Ridge Regression with lag features ($\tau=1, 2, 3$).
  - Holt-Winters Exponential Smoothing.
- **Evaluation Metrics:**  
  Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), Mean Absolute Percentage Error (MAPE).
- **Practical Application & User:**  
  Proactive early-warning budget alerts: "You are currently pacing to exceed your discretionary dining limit by 18% this month."
- **Limitations & Data Gaps:**  
  6-7 months of history per user limits deep neural time-series architectures (e.g. Temporal Fusion Transformers or LSTMs); lightweight interpretable models perform best.

---

## 3. Tasks Not Feasible With Current Data (Data-Deficient)

| Proposed Task | Why Feasibility Fails | Minimum Required Additional Data |
|---|---|---|
| **Credit Scoring & Default Prediction (PD/LGD)** | Dataset contains **zero default events**, delinquencies, bureau scores, or charge-offs. Predicting creditworthiness would fabricate non-existent risk labels. | Historical credit bureau files with 12-month default performance tags (e.g. 90+ DPD flags). |
| **Fraud & AML Detection** | AgamiAI dataset README explicitly notes: *"Contains only legitimate transactions (no fraud patterns)"*. Prototype dataset has only legitimate transactions and standard reversals. | Labeled AML alert databases with SAR (Suspicious Activity Report) filings and confirmed fraud cases. |
| **Deep Personalization / Collaborative Filtering** | Only 10 distinct user profiles exist in the prototype dataset. Collaborative filtering requires thousands of users to discover latent interaction matrices. | User-merchant interaction matrix with $\ge 10,000$ users and catalog items. |
| **Multi-Year Macroeconomic Forecasting** | Time series spans at most 7 months per user. Capturing multi-year inflation, seasonal holidays (Diwali, Eid, Christmas), or interest rate shifts is mathematically impossible. | Multi-year historical ledgers spanning $\ge 3$ consecutive annual cycles. |

---

## 4. Prioritization Matrix

```
   High Impact │   [Opp 2: Liquidity Simulation & Affordability]
               │   
               │   [Opp 1: ML Transaction Categorization]
               │   
   Med  Impact │   [Opp 3: Expense Run-Rate Forecaster]
               │   
               │   [Document AI Statement Parser]
   Low  Impact └───────────────────────────────────────────────
                 Low Effort             Med Effort       High Effort
```

**Strategic Recommendation:**
1. **Immediate Core ML Execution:** Build, validate, and persist the **Supervised Transaction Categorization Pipeline** (Opportunity 1) with calibrated confidence scoring.
2. **Immediate Analytical Execution:** Build the **90-Day Liquidity Simulation & Affordability Engine** (Opportunity 2) and verify 100% agreement against benchmark outputs.
3. **Integration:** Combine both engines into a unified, modular Python backend exposing REST endpoints and an interactive user application.
