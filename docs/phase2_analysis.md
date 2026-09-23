# Phase 2 Financial Intelligence Analysis

## 1. Available Fields in the Prototype Dataset
From our prototype `financial_events.csv`, the following fields are available:
- `transaction_id`, `user_id`, `event_type` (`expense`, `debt_payment`, `subscription`, `income`), `description`, `category` (`rent`, `utilities`, `education`, `music_subscription`, etc.), `direction` (`debit`, `credit`), `amount`, `currency`, `event_date`, `settlement_date`, `status`, `flexibility` (`fixed`, `stoppable`, `variable`).

## 2. Usable Financial Concepts
The data strictly supports calculating:
- **Total Income & Expenses**: By summing `direction = credit` (income) and `direction = debit` (expenses).
- **Savings & Savings Rate**: (Income - Expenses) and (Savings / Income).
- **Expense Ratio**: (Expenses / Income).
- **Essential vs Discretionary Expenses**: Supported directly by the `flexibility` field. `fixed` implies essential. `variable` or `stoppable` implies discretionary.
- **Recurring Obligations**: Supported by `flexibility = fixed` and `event_type = subscription | debt_payment` or observing frequency.
- **EMI/Debt Burden**: Supported by `event_type = debt_payment` and `category = debt_repayment`.
- **Anomaly Detection**: Can be calculated using mean and standard deviation of amount per category per user.

## 3. Unsupported Concepts
- **Net Worth**: We only have `current_available_balance` and transactions. We lack total assets/liabilities.
- **Credit Score**: Not in the data.
- **Arbitrary "Financial Health Score"**: No methodology provided, so we will not invent one. We will return individual clear metrics.

## 4. Assumptions and Architectural Decisions
- **Categorization ML**: Since `category` labels already exist in the ground truth, our baseline "ML categorizer" will serve as a passthrough for known categories with high confidence (e.g., 0.95+). Unknown categories will be assigned low confidence. The architecture will be kept modular for a real ML model later.
- **Anomaly Detection ML**: A simple Z-score or standard deviation multiplier per category will be used as the baseline ML anomaly detection method. Thresholds will be documented.
- **Pydantic Schemas**: Will strictly enforce separation between `observed` fields and `model_predicted` fields (e.g., confidence).
