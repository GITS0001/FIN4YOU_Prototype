# FIN4YOU Model Evaluation

This document outlines the evaluation strategy, metrics, and limitations of the ML models deployed in FIN4YOU.

## 1. Transaction Categorization

*   **Model:** TF-IDF + Logistic Regression (balanced class weights).
*   **Evaluation Strategy:** 80/20 train/test split (stratified by category, random_state=42).
*   **Metrics:** Accuracy, Macro F1, Per-class Precision/Recall/F1, Confusion Matrix.
*   **Results (Prototype Dataset):** 1.00 Macro F1.
*   **Limitations:** **WARNING.** The prototype dataset `financial_events.csv` is highly synthetic and repetitive. The perfect 1.00 evaluation metrics **DO NOT** represent real-world accuracy. The model functions as a strong mapping engine for this dataset, but in a production environment with highly noisy merchant descriptions, this would likely drop to 0.70-0.85 F1.

## 2. Anomaly Detection

*   **Model:** Category-specific Z-Score statistical baseline.
*   **Evaluation Strategy:** Qualitative validation via explanation plausibility.
*   **Results:** Successfully detects and explains variations $> 2.0 \sigma$.
*   **Limitations:** Struggles if a user has fewer than 3 transactions in a specific category (fallback gracefully ignores the check). It is explicitly **not fraud detection**; it only measures deviation from historical routine.

## 3. Financial Forecasting (Income and Variable Expenses)

*   **Models Evaluated:**
    1.  Historical Mean (All prior months)
    2.  2-Month Moving Average
*   **Evaluation Strategy:** Strict Chronological Split. Train on $Month_1 ... Month_{N-1}$, test on $Month_N$.
*   **Metrics:** Mean Absolute Error (MAE).
*   **Selection Logic:** The prediction engine evaluates both MAEs on the fly for a given user. It automatically selects the model with the lower MAE for that specific user's latest data points.
*   **Limitations:** Inherently struggles with heavy seasonality (e.g., holiday spending spikes) since it lacks seasonal components (like SARIMA). However, given that users frequently only link 3-6 months of data, attempting to fit seasonal models would lead to catastrophic overfitting. The baseline approach is the most technically defensible given the data constraints.
