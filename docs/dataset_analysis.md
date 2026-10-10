# Dataset Analysis & Data Dictionary

## Overview
This document provides an analysis of the datasets provided in `data/raw/` for the FIN02 HackMatrix prototype: "Financial Health Copilot: From Transactions to Action".

## Datasets Analyzed

### 1. `financial_events.csv`
- **Description**: The core transactions and financial events.
- **Rows**: 25,342
- **Columns**: `event_id`, `user_id`, `event_type`, `description`, `category`, `direction`, `amount`, `currency`, `event_date`, `settlement_date`, `status`, `linked_event_id`, `flexibility`, `minimum_allowed_amount`.
- **Missing Values**: `amount` (16), `settlement_date` (10), `linked_event_id` (25,284 missing, implying most events aren't linked), `minimum_allowed_amount` (22,435 missing).
- **FIN02 Relevance**: Highly relevant. Supports transaction categorization, anomaly detection, historical spending tracking, cash flow analysis, and forecasting.

### 2. `financial_profiles.csv`
- **Description**: Current state and preferences for users.
- **Rows**: 275
- **Columns**: `user_id`, `home_currency`, `current_available_balance`, `minimum_balance_to_keep`, `financial_priorities`, `expense_categories_to_protect`, `expense_categories_user_is_willing_to_reduce`, `expense_categories_user_is_willing_to_stop`, `payment_methods_user_will_consider`, `max_installment_months`.
- **Missing Values**: `expense_categories_user_is_willing_to_reduce` (39), `expense_categories_user_is_willing_to_stop` (62), `max_installment_months` (119).
- **FIN02 Relevance**: Highly relevant. Supports the Decision Engine, what-if simulations, and affordability checks by providing the current balance and the user's minimum buffer threshold.

### 3. `requests.csv`
- **Description**: Input requests/questions from users regarding financial decisions (e.g., "Can I afford this?").
- **Rows**: 250
- **Columns**: `request_id`, `user_id`, `request_date`, `request_type`, `requested_amount`, `desired_completion_date`, `allows_partial_payment`, `request_text`.
- **FIN02 Relevance**: Essential for testing the Copilot API, Affordability Engine, and intent extraction.

### 4. `request_payment_options.csv`
- **Description**: Available payment strategies for the requests.
- **Rows**: 790
- **Columns**: `payment_option_id`, `request_id`, `payment_method`, `payment_amount`, `number_of_payments`, `first_payment_date`, `payment_frequency_days`, `financing_fee`, `total_payable_amount`.
- **FIN02 Relevance**: Provides realistic scenarios for the What-if and Recommendation engines. 

### 5. `output.csv`
- **Description**: The correct output / ground truth for the 250 requests.
- **Rows**: 250
- **Columns**: `request_id`, `amount_safe_to_pay`, `affordability_status`, `recommended_payment_method`, `payment_plan`, `earliest_date_for_full_payment`, `spending_changes_needed`, `decision_explanation`.
- **FIN02 Relevance**: Useful for evaluation and validating our Decision Engine's recommendations against expected outcomes.

### 6. `sample_requests.csv`
- **Description**: 25 rows representing a joined summary of requests and outputs.
- **FIN02 Relevance**: Handy reference, but redundant given `requests.csv` and `output.csv`.

### 7. `exchange_rates.csv`
- **Description**: Currency exchange rates over time.
- **Rows**: 134
- **Columns**: `rate_date`, `from_currency`, `to_currency`, `rate`.
- **FIN02 Relevance**: Can be used to normalize amounts if multi-currency requests arise, though for MVP we will standardize using the home currency.

### 8. `messages.csv` & `images.csv`
- **Description**: Contextual user messages and image references.
- **FIN02 Relevance**: Auxiliary. Can be used for advanced Copilot LLM features (intent extraction from text), but lower priority for the core calculation engine.

---

## Data Dictionary (Internal Prototype Schema)

For the prototype (Phase 1), we map the raw datasets to a standard internal representation.

### Transaction Schema (from `financial_events.csv`)
- `transaction_id` (str): Mapped from `event_id`.
- `user_id` (str): Profile identifier.
- `date` (date): Mapped from `event_date`.
- `description` (str): Event description.
- `amount` (float): Absolute transaction amount. (Rows with missing amounts dropped).
- `currency` (str): Currency code.
- `type` (str): Derived from `event_type` and `direction` (e.g., 'income', 'expense').
- `category` (str): Extracted from `category`.
- `flexibility` (str): Extracted from `flexibility` ('fixed', 'variable'). Essential vs Discretionary.

### Profile Schema (from `financial_profiles.csv`)
- `user_id` (str)
- `currency` (str)
- `current_balance` (float)
- `minimum_balance` (float)
- `priorities` (list[str])

## Prototype Dataset Selection Strategy
We will select a small subset (e.g., 5 users: `user_01` to `user_05`) and extract all their events, profiles, requests, and outputs into `data/prototype/`. This ensures realistic relationships are maintained without processing 25,000+ rows during rapid testing.
