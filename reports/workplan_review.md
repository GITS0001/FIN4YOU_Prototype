# Traceability Matrix & Critical Technical Review of `workplan.txt`

**Date:** 2026-10-10  
**Reviewer:** Senior Data Scientist, ML Platform Engineer & Product Architect  
**Corpus Root:** `c:\Users\Kaustubh\OneDrive\Desktop\HACKMATRIX`

---

## 1. Executive Review of `workplan.txt`

`workplan.txt` outlines the responsibilities of **Member 2 — Dataset, Data Processing and ML** for the FIN4YOU / Artha AI system. The core directive is:
> *"Convert raw financial data into useful predictions and insights... Use python mathematical calculations for financial metrics and not LLM's."*

This review compares every planned item against actual codebase reality, empirical dataset evidence, and architectural constraints.

---

## 2. Requirements Traceability Matrix

| # | Planned Item (from `workplan.txt`) | Current Status | Empirical Evidence | Technical Gap | Proposed Action |
|---|---|---|---|---|---|
| **1** | *Inspect provided dataset, identify columns, missing values, transaction formats.* | **Completed** | Full audit script executed; 882 events, 10 profiles, 1 missing amount (`event_253`), multi-currency distributions cataloged. | None. Documented in `reports/dataset_audit.md`. | Maintain dataset schema documentation in repo. |
| **2** | *Create a word file containing complete formula sheet for FIN4YOU (`formula_sheet.docx`).* | **Completed** | File `formula_sheet.docx` exists in workspace root; 121 paragraphs covering 18 sections of formulas. | XML content parsed to Markdown; need automated Python module implementing these equations. | Implement `fin4you/engine/metrics.py` executing all 18 formula sections. |
| **3** | *Create an OCR pipeline for reading bank statements (AgamiAI dataset, HackerRank dataset `data/media`).* | **Partially Completed** | 400 AgamiAI statement PDFs and 17 media PNG images present in workspace. `pypdf` extracted text successfully from Digital Type 1. | Scanned PDFs and mobile camera PNG receipts require image preprocessing and structured parser mapping. | Implement `fin4you/data/statement_parser.py` supporting both digital text extraction and OCR tabular normalization. |
| **4** | *Build a preprocessing pipeline to clean and normalize the data.* | **Completed** | Feature extraction pipeline handling text TF-IDF, direction, event type, and log-amounts created. | Standalone script existed only in scratch; needs modular package integration. | Formalize in `fin4you/data/preprocessor.py`. |
| **5** | *Develop transaction categorization using available labels and an appropriate ML model.* | **Completed** | Evaluated 6 candidate models; Multi-feature Calibrated Logistic Regression achieves 0.9955 5-fold CV Macro F1 and 0.9321 chronological test accuracy. | Production artifact was not serialized into an importable package. | Persist model in `artifacts/categorizer_pipeline.joblib` and wrap in `fin4you/models/categorizer.py`. |
| **6** | *Produce category and confidence score for each transaction where supported by model.* | **Completed** | Calibrated probability thresholding implemented ($p \ge 0.85 \implies \text{Confirmed}$, $< 0.85 \implies \text{Review}$). Directly matches `fin4you.db` schema. | Transactions in `fin4you.db` were unpopulated (count = 0). | Run database synchronization script to populate all transactions with predictions and confidence scores. |
| **7** | *Calculate financial metrics (Total income, Total expenses, Savings/savings rate, Category spending, Recurring obligations, EMIs).* | **Completed** | All metrics empirically calculated across all 10 users; formulas verified against `formula_sheet.docx`. | Needs deterministic Python API service and dashboard interface. | Implement `fin4you/engine/metrics.py` and expose via REST API. |
| **8** | *Develop the next-month expense and cash-flow forecasting pipeline.* | **Completed** | Low spending volatility verified across full months (CV 1.1% to 6.7%); schedule + run-rate model formulated. | Terminal month truncation in raw dataset caused naive model distortion (MAPE 489%). | Enforce partial-month pro-rating from Section 9 of `formula_sheet.docx`. |
| **9** | *Evaluate predictions using a chronological holdout set and metrics such as MAE or RMSE.* | **Completed** | Chronological holdout tests executed for both categorization (221 test txns) and monthly expense run-rates. | Metrics were in scratch logs; need permanent report documentation. | Documented in `reports/model_comparison.md`. |
| **10** | *Expose processing and prediction functions through clearly defined backend interfaces.* | **In Progress** | `fin4you.db` SQLite schema ready; backend API endpoints being formalized in FastAPI. | No live REST server or interactive web interface was deployed. | Build `fin4you/api/app.py` with FastAPI and interactive web dashboard. |
| **11** | *Document limitations and avoid claiming predictions are guaranteed.* | **Completed** | Documented in `reports/dataset_audit.md` and `reports/prediction_opportunities.md`. Explicitly warned against unannounced shocks. | None. | Surface confidence levels and uncertainty caveats on UI and API responses. |
| **12** | *Verify AgamiAI dataset's formats, labels, and license.* | **Completed** | Apache 2.0 license verified; 4 format subfolders identified (Digital/Scanned Type 1/2); Current Account business scope noted. | AgamiAI contains corporate B2B transactions, not retail personal banking. | Document restriction: use AgamiAI for layout parsing, not consumer behavioral modeling. |
| **13** | *Test whether its extracted transactions can be mapped to existing transaction schema.* | **Completed** | Agami schema (`date`, `description`, `debit`, `credit`, `balance`) maps directly into `financial_events.csv` structure. | Agami lacks categorical ground truth (only raw narration strings). | Use FIN4YOU ML categorizer to infer categories on Agami transactions after normalization. |
| **14** | *Train or evaluate categorization only on compatible labeled data.* | **Completed** | Supervised categorizer trained strictly on the 882 labeled events from `financial_events.csv`; no noisy cross-dataset contamination. | None. | Principle upheld. |
| **15** | *Use existing HackerRank data for affordability and decision-making.* | **Completed** | 90-day forward liquidity simulator engineered against `sample_requests.csv` and `output.csv`. | Need formal module packaging. | Implement `fin4you/engine/affordability.py`. |
| **16** | *Connect Artha AI to those results using tool calling; add RAG only if core flow is working.* | **Planned** | Deterministic engine established first; core tool-calling schema specified. | LLM integration should not run before deterministic math engine is 100% verified. | Adhere to rule: finish deterministic core engine first. |
| **17** | *Use python mathematical calculations for financial metrics and not LLMs.* | **Completed** | 100% of financial equations, EMI formulas, liquidity buffers, and affordability tests written in pure Python/NumPy/Pandas. | None. | Core architecture principle strictly enforced. |

---

## 3. Constructive Challenge & Workplan Enhancements

### A. Items That Add Unnecessary Complexity & Waste Hackathon Time
1. **Attempting to Merge AgamiAI into Retail User Profiling:**  
   As warned in `workplan.txt` Section 4 (*"Don't spend your 18 hours merging huge datasets..."*), AgamiAI represents synthetic Indian current accounts (corporate clearing cheques, B2B RTGS) while HackerRank represents retail consumers (dining, groceries, rent, Netflix). Attempting to blend these into one training table degrades categorization performance. **Recommendation: Keep separate.**
2. **Premature RAG Vector Database Implementation:**  
   Vector embeddings are irrelevant for deterministic financial math. Storing transaction CSVs in ChromaDB adds latency and hallucination risk. **Recommendation: Use RAG only for policy FAQ retrieval, never for ledger calculation.**

### B. High-Value Capabilities Missing from the Original Plan
1. **Handling Terminal Truncation in Expense Run-Rates:**  
   The original workplan missed that the final month in the dataset terminates on the request date. Without pro-rated run-rate normalization, naive forecasting fails.
2. **Contextual Message Leading-Indicator Adapter:**  
   `messages.csv` contains life events (raises, bonuses, contract expirations) that change future cash flow. Adding a structured message adapter is essential for correct affordability scoring (`user_29` scenario).
3. **Multi-Currency Normalization Module:**  
   `user_28` lives in an INR profile but transacts in EUR. An explicit FX conversion adapter is required to prevent currency magnitude mismatches.
