# Phase 3 Prediction Engine Analysis

## 1. Temporal Coverage and Granularity
- **Total Users in Prototype**: 10 users
- **Date Range**: 2019-03 to 2026-07 across different users.
- **Data per User**: Each user has exactly 6 to 7 months of continuous historical data.
- **Granularity**: Daily transaction logs, which aggregate perfectly into monthly time series.

## 2. Forecasting Limitations
- 6-7 months of data is **insufficient** for complex seasonal modeling (e.g., ARIMA with yearly seasonality) or deep learning approaches (e.g., LSTMs).
- Attempting to forecast 12 months ahead based on 6 months of history is statistically invalid and highly uncertain.
- We cannot safely predict exact day-to-day spending spikes.

## 3. What Can Safely Be Predicted
- **Next Month's Total Expenses / Income**: Using a moving average or historical mean over the available 6 months.
- **Category-Level Future Spending**: Simple averages for non-fixed categories.
- **Future Obligations (Known)**: Fixed subscriptions and debt payments can be carried forward as absolute deterministic obligations rather than "forecasted" probabilistically.
- **Projected Cash Flow**: `Projected Income - (Projected Expenses + Known Obligations)`.
- **Projected Balance**: `Current Available Balance + Projected Cash Flow`.
- **Cash-Flow Gap Detection**: Safely computable by comparing Projected Balance against `minimum_balance_to_keep`.

## 4. Baseline Model Selection
- **Target**: Next month's spending and income.
- **Baseline Algorithm**: 3-month or all-available-month Moving Average. This is explainable, transparent, and defensible for 6 months of data. 
- **Evaluation**: Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE) on chronological train/test split. (e.g., Train on months 1-5, Predict month 6, compare to actual month 6).
- **Uncertainty Approach**: Statistical variance over the historical months. If a user's spending swings wildly, uncertainty is high.

## 5. Insufficient Data Behavior
- If a user has less than 2 months of history, forecasting will abort safely and return a structured `{"available": false, "reason": "Insufficient historical observations"}` instead of throwing errors or guessing.
