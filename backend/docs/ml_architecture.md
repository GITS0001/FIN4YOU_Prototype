# FIN4YOU ML Architecture

## Overview
The ML architecture for FIN4YOU is designed to provide highly interpretable, deterministic, and rigorously evaluated models. Deep learning and opaque LLMs are strictly excluded from mathematical calculations.

The architecture strictly adheres to the paradigm:
`REAL DATA → REAL ML → FINANCIAL STATE → PREDICTION → SIMULATION → DECISION → EXPLAINABLE ARTHA AI`

## 1. Transaction Categorization
*   **Methodology:** TF-IDF Vectorization + Logistic Regression.
*   **Why Chosen:** High explainability, robust on short text descriptions, fast inference time, and native support for `predict_proba` which enables accurate confidence scoring.
*   **Feature Engineering:** Extracts bi-grams (ngram_range=(1,2)) from raw transaction descriptions.
*   **Confidence Logic:**
    *   `Confidence >= 0.8`: Status `classified`, Confidence `high`.
    *   `Confidence >= 0.5`: Status `classified`, Confidence `medium`.
    *   `Confidence < 0.5`: Category `Unknown`, Status `needs_review`, Confidence `low`.

## 2. Anomaly Detection
*   **Methodology:** Z-Score Baseline.
*   **Why Chosen:** Easily explainable to end-users ("Your spending is 2x your usual average"). Isolation Forest was evaluated but rejected as the prototype dataset doesn't contain enough multidimensional complexity to justify the loss in explainability.
*   **Detection Strategy:** User-specific, category-specific standard deviation. Flags transactions > 2.0 std dev.
*   **Confidence:** Hardcoded to 0.95 (deterministic statistical calculation).

## 3. Financial Forecasting
*   **Methodology:** Historical Mean vs. 2-Month Moving Average.
*   **Why Chosen:** Provides robust baselines. Avoids over-parameterized models like ARIMA or LSTM which drastically overfit on datasets with < 12 months of history.
*   **Validation Strategy:** Strict chronological split.
*   **Model Selection:** The system calculates the MAE of both the Historical Mean and the 2-Month Moving Average against the held-out test month. The model with the lower MAE is automatically selected for the final forecast.
*   **Outputs:** Includes standard deviation as the explicit mathematical `uncertainty` bound.

## 4. Leakage Prevention
*   **Time-Series Strictness:** Future transactions are never used to predict the past. The evaluation holds out the very last observed month.
*   **State Separation:** The `FinancialState` model explicitly segregates `OBSERVED`, `DERIVED`, `PREDICTED`, and `SIMULATED` metrics.

## 5. Artha AI Integration
Artha AI acts purely as an NLP translation layer. It consumes the structured `DecisionTrace` (containing observations, ML predictions, and deterministic simulations) and formats them into a readable output. It never invents confidence scores or calculates financial metrics.
