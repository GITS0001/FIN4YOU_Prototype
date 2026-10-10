# Comprehensive Dataset Usability and Quality Audit: FIN4YOU & Artha AI

**Date:** 2026-10-10  
**Auditor:** Senior Data Scientist & ML Platform Architect  
**Project:** FIN4YOU / Artha AI (Financial Intelligence & Health Copilot)  
**Corpus Root:** `c:\Users\Kaustubh\OneDrive\Desktop\HACKMATRIX`

---

## 1. Executive Summary

This audit evaluates the datasets available within the project repository to assess their technical integrity, internal consistency, statistical properties, and readiness for machine learning and decision-making workloads.

Two primary dataset clusters were audited:
1. **HackerRank Prototype Dataset** (`data/prototype/`): Core multi-entity relational dataset capturing 10 distinct user profiles, 882 historical financial transactions, payment option schedules, affordability evaluation requests, exchange rates, and contextual employer/service provider messages.
2. **AgamiAI Indian Bank Statements Dataset** (`Indian-Bank-Statements/`): 400 synthetic Indian business current account bank statements spanning digital PDFs, scanned PDFs, and structured ground-truth JSON files containing ~64,000 transactions across multiple bank layouts.

**Overall Usability Verdict:**
- **HackerRank Prototype Dataset:** **Usable after preprocessing**. It exhibits high internal consistency, well-defined target variables, and clean relational keys, but has specific edge cases (1 missing salary amount in `event_253` tied to an external receipt, partial final-month truncation, and cross-currency mapping between INR profile and EUR transactions for `user_28`).
- **AgamiAI Bank Statements Dataset:** **Usable for Statement Parsing & Document AI (Digital/OCR)** under Apache 2.0 license. However, because it exclusively represents **Indian B2B current accounts** (vendor payouts, clearing cheques, corporate RTGS) rather than retail/personal accounts, it **must not** be mixed with retail consumer profiling without domain adaptation.

---

## 2. Dataset Inventory & Structural Analysis

| File / Entity | File Path | Format | Record Count | Column Count | File Size | Primary Purpose & Schema Overview |
|---|---|---|---|---|---|---|
| `financial_profiles.csv` | `data/prototype/financial_profiles.csv` | CSV | 10 | 10 | 1.70 KB | User profiles (`user_id`, `home_currency`, `current_available_balance`, `minimum_balance_to_keep`, priorities, protected/stoppable categories, payment methods). |
| `financial_events.csv` | `data/prototype/financial_events.csv` | CSV | 882 (excluding header) | 14 | 100.45 KB | Transaction ledger (`event_id`, `user_id`, `event_type`, `description`, `category`, `direction`, `amount`, `currency`, `event_date`, `settlement_date`, `status`, `linked_event_id`, `flexibility`). |
| `request_payment_options.csv` | `data/prototype/request_payment_options.csv` | CSV | 29 | 9 | 2.58 KB | Candidate payment financing plans (`payment_option_id`, `request_id`, `payment_method`, `payment_amount`, `number_of_payments`, `first_payment_date`, `frequency_days`, `financing_fee`, `total_payable_amount`). |
| `requests.csv` | `data/prototype/requests.csv` | CSV | 5 | 8 | 1.15 KB | Test cohort affordability requests (`request_26` to `request_30`). |
| `sample_requests.csv` | `data/prototype/sample_requests.csv` | CSV | 5 | 15 | 2.22 KB | Labeled training/sample requests (`request_01` to `request_05`) with ground truth decisions (`amount_safe_to_pay`, `affordability_status`, `recommended_payment_method`, `payment_plan`). |
| `output.csv` | `data/prototype/output.csv` | CSV | 5 | 8 | 1.13 KB | Benchmark ground truth evaluation output for test cohort requests `request_26` through `request_30`. |
| `exchange_rates.csv` | `data/prototype/exchange_rates.csv` | CSV | 135 | 4 | 3.41 KB | Monthly foreign exchange conversion rates (`rate_date`, `from_currency`, `to_currency`, `rate`) covering EUR, USD, ZAR, IDR, INR. |
| `messages.csv` | `data/prototype/messages.csv` | CSV | 7 | 7 | 2.30 KB | Contextual notifications from employers, payroll, and platforms (`message_id`, `user_id`, `request_id`, `sent_at`, `source_type`, `message_text`). |
| `images.csv` | `data/prototype/images.csv` | CSV | 1 | 4 | 83 B | Metadata mapping document images to events (`image_01`, `user_03`, `request_03`, `event_253`). |
| `media/images/` | `data/media/images/` | PNG | 17 files | N/A (Image) | ~5.7 MB total | High-resolution receipts, pay slips, and statement snippets. |
| `fin4you.db` | `data/fin4you.db` | SQLite3 | 6 tables | Variable | 73.7 KB | SQLite production schema (`users`, `otps`, `profiles`, `transactions`, `copilot_requests`, `plaid_items`). |
| AgamiAI Statements | `Indian-Bank-Statements/train/` | JSON + PDF | 400 statements (~64k txns) | 18 metadata keys | ~120 MB | Synthetic Indian corporate bank statements across 4 layout classes (Digital Type 1/2, Scanned Type 1/2). |

---

## 3. Data Quality & Integrity Audit

### A. Missing Values and Structural Gaps
- **`financial_events.csv` Amount Null:** Exactly 1 record has a missing amount: `event_253` (`user_03`, `2019-08-31`, category `salary`, description `August 2019 net salary`). This is directly explained by `images.csv` and `image_01.png` which contain the corresponding salary pay slip. Preprocessing pipelines must impute or extract this value from document intelligence.
- **Settlement Date vs Event Date:** 3 transactions have a pending status (`event_102`, `event_185`, `event_254`) where `settlement_date` is 3 to 5 days ahead of `event_date`. This reflects real banking float and must be respected in cash-flow projections.
- **Linked Events:** 4 transactions have non-null `linked_event_id` representing authorizations and corresponding reversals/refunds (e.g. `event_99` reversing `event_98`).
- **Flexibility Field:** Discretionary transactions (shopping, dining, streaming) are labeled `stoppable`, `flexible`, or empty, while contractual expenses (rent, utilities, debt repayment) are labeled `fixed`.

### B. Currencies & Multi-Currency Nuances
- Transactions span 5 currencies: `ZAR`, `IDR`, `INR`, `EUR`, `USD`.
- **User 28 Currency Anomaly:** `financial_profiles.csv` lists `home_currency = INR` (balance = 1,789.4 INR, min = 1,100 INR), while `financial_events.csv` records all user_28 transactions in `EUR` (~1,220 EUR/month salary), and `requests.csv` states an investment request in `EUR 1,302.40`. Preprocessing must handle FX normalization via `exchange_rates.csv` where 1 EUR ≈ 21.7 ZAR or 90.5 INR.

### C. Class Imbalance (Transaction Categories)
Across 882 labeled events, category distribution is:
- High frequency: `groceries` (219, 24.8%), `transport` (170, 19.3%), `dining` (97, 11.0%), `salary` (74, 8.4%).
- Medium frequency: `utilities` (52), `rent` (46), `shopping` (35), `cloud_storage` (35), `entertainment` (20), `streaming` (20).
- Rare events: `education` (16), `healthcare` (16), `debt_repayment` (15), `music_subscription` (15), `delivery_membership` (15), `housing` (12), `insurance` (10), `gym` (10), `family_support` (5).
*Mitigation:* Stratified splitting and class weighting are required to ensure rare categories (e.g., family support, gym) are not ignored.

### D. Temporal Properties & Truncation
- Each of the 10 users possesses 6 to 7 months of continuous daily financial history (69 to 114 transactions per user).
- **Incomplete Final Month:** In all 10 profiles, the data concludes on the exact day of the user's evaluation request (e.g., `2024-03-03` for `user_01`, `2025-08-05` for `user_02`). Raw monthly aggregation of the final month yields an incomplete partial month, requiring pro-rated run-rate formulas as specified in `formula_sheet.docx`.

---

## 4. Dataset Usability Scorecard

| Dimension | Score (1-10) | Justification & Supporting Evidence | Limitations & Caveats |
|---|---|---|---|
| **1. Completeness** | 9/10 | Complete user metadata, transaction logs, exchange rates, and ground-truth decisions. Only 1 deliberate missing salary amount (`event_253`). | Document image OCR is required to extract the exact missing salary amount for `user_03`. |
| **2. Internal Consistency** | 9/10 | Relational IDs (`user_id`, `request_id`, `payment_option_id`) link with 100% referential integrity across all CSVs. | `user_28` currency discrepancy between profile (INR) and event transactions (EUR). |
| **3. Relevance to Objectives** | 10/10 | Directly matches the hackathon problem statement and `workplan.txt` deliverables for FIN4YOU. | None. Exactly designed for this challenge. |
| **4. Representativeness** | 7/10 | Synthetic transaction patterns mirror realistic banking cadences (salaries, EMIs, grocery schedules). | Highly structured synthetic cadences; lacks erratic real-world consumer behavior or messy OCR noise. |
| **5. Temporal Coverage** | 8/10 | 6-7 months of daily granularity per user is sufficient for 90-day forward projections and recurring cadence identification. | Insufficient for multi-year macroeconomic seasonality modeling. |
| **6. Supervised Learning Suitability** | 9/10 | 882 clean text descriptions with 19 distinct categories. 5-fold CV achieves >0.99 Macro F1. | Rare classes have fewer than 15 examples; requires careful regularized models. |
| **7. Unsupervised Learning Suitability** | 7/10 | User spending vectors cluster cleanly into lifestyle tiers (high-income vs tight-budget). | Small sample size of users (N=10) limits deep latent customer segmentation. |
| **8. Forecasting Suitability** | 8/10 | Complete-month expense volatility is low (Coefficient of Variation 1.1% to 6.7%), making run-rate forecasting reliable. | Must handle partial-month cutoff at request boundaries. |
| **9. Anomaly Detection Suitability** | 8/10 | Clear historical baselines allow robust Z-score calculation for transaction amounts per category. | No labeled fraud records; suitable for budget outlier detection, not AML/fraud. |
| **10. Real-World Deployment Readiness** | 7/10 | Production SQLite schema (`fin4you.db`) is already architected with ML confidence columns. | Real-world bank statements will feature noisier raw narration strings than the synthetic prototype. |

**Mean Usability Score: 8.2 / 10**

---

## 5. Usability Decision

**DECISION: USABLE AFTER PREPROCESSING.**  
The HackerRank prototype dataset is fully equipped to support:
1. Supervised Machine Learning for transaction categorization with calibrated confidence estimation.
2. Next-month expense and cash-flow run-rate forecasting.
3. 90-day forward liquidity simulation and affordability decision intelligence.
4. Python mathematical execution of all formulas from `formula_sheet.docx`.
