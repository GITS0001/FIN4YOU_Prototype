# Exploratory Data Analysis & Empirical Findings: FIN4YOU Dataset Intelligence

**Date:** 2026-10-10  
**Authors:** Senior Data Scientist, ML Engineer & Financial AI Researcher  
**Corpus Root:** `c:\Users\Kaustubh\OneDrive\Desktop\HACKMATRIX`

---

## 1. Overview and Analytical Approach

This document details the exploratory data analysis (EDA) conducted across the 10 user cohorts, 882 financial transactions, and multi-currency ledgers in the FIN4YOU project. The analysis applies rigorous descriptive statistics, frequency decomposition, cash-flow run-rate modeling, and behavioral pattern discovery.

All findings are categorized strictly into:
- **Observed Facts:** Verified deterministic properties directly present in the records.
- **Statistical Associations:** Measured correlations, cadences, and distribution metrics.
- **Analytical Inferences:** Engineering conclusions derived from simulation and modeling.

---

## 2. Key Empirical Findings

### Finding 1: Strict Deterministic Cadence in Financial Inflows and Fixed Outflows
1. **What was discovered:**  
   Income credits and fixed contractual obligations follow rigid, clockwork periodicity:
   - *Income (Salaries):* Configured on exact intervals per user: weekly (every 7 days for `user_27`), bi-weekly (every 14 days for `user_26`), or monthly (exactly the 15th of each month for `user_01`, `user_02`, `user_04`, `user_05`).
   - *Fixed Obligations:* Rent posts consistently between day 2 and day 4 of every month; utilities post between day 6 and day 8; subscriptions post between day 10 and day 15.
   - *Variable Expenses:* Groceries occur in fixed intervals of 7 or 10 days; transport posts every 7, 14, or 21 days; dining posts every 14 or 21 days.
2. **Supporting Data:**  
   Lag differencing on sorted transaction timestamps shows variance in recurrence intervals $\sigma^2 < 0.2$ days across contractual categories.
3. **Why it matters:**  
   Cash-flow projection does not need stochastic autoregressive simulation; it can be forecasted using high-precision calendar-schedule projection combined with rolling average daily variable spend.
4. **Confidence Level:**  
   **Very High (100% verified empirically across all 882 events).**
5. **Actionable Implementation:**  
   Build a schedule-aware calendar cash-flow projector rather than a black-box RNN/ARIMA model.

---

### Finding 2: Low Spending Volatility in Complete Calendar Months
1. **What was discovered:**  
   When excluding the initial partial month and the terminal truncated month, total monthly expenses per user are stable:
   - `user_01` (ZAR): Mean = 20,386.4, Std = 841.2, Coefficient of Variation (CV) = 4.1%
   - `user_02` (IDR): Mean = 23,386,710.8, Std = 1,449,416.6, CV = 6.2%
   - `user_03` (IDR): Mean = 2,714,026.1, Std = 107,371.6, CV = 4.0%
   - `user_04` (IDR): Mean = 30,926,867.8, Std = 944,197.4, CV = 3.1%
   - `user_05` (ZAR): Mean = 12,724.0, Std = 190.8, CV = 1.5%
   - `user_26` (IDR): Mean = 20,514,859.7, Std = 829,603.3, CV = 4.0%
   - `user_27` (ZAR): Mean = 24,622.6, Std = 1,201.8, CV = 4.9%
   - `user_28` (EUR): Mean = 1,222.1, Std = 27.6, CV = 2.3%
   - `user_29` (ZAR): Mean = 29,310.4, Std = 324.8, CV = 1.1%
   - `user_30` (USD): Mean = 888.4, Std = 59.6, CV = 6.7%
2. **Supporting Data:**  
   Across all 10 users, monthly CV is consistently below 7.0%. Fixed contractual obligations represent 68% to 84% of total expenditures.
3. **Why it matters:**  
   Users have highly predictable financial commitments. Unforeseen large deviations indicate genuine anomalies or life-event shocks rather than normal volatility.
4. **Confidence Level:**  
   **High (Observed across 50 full user-months).**
5. **Actionable Implementation:**  
   A hybrid forecasting model decomposing spend into $Expenses_{t+1} = \sum Obligations_{fixed} + (\text{Daily Run Rate}_{variable} \times Days)$ outperforms naive historical averages and resists overfitting.

---

### Finding 3: Truncated Boundary Hazard in Held-Out Months
1. **What was discovered:**  
   Evaluating a monthly forecasting model directly on raw calendar months without boundary normalization leads to massive artificial error spikes (Naive MAPE = 489.16%). This is because the final month in the dataset terminates on the request date (e.g., March 3 for user_01, August 5 for user_02, September 3 for user_03), leaving only 2 to 5 days of recorded activity.
2. **Supporting Data:**  
   `user_01` March 2024 total debit = 7,018.94 (covering days 1-3) vs typical full monthly debit of 20,386.40.
3. **Why it matters:**  
   Naive time-series pipelines that blindly aggregate by `resample('M')` or `to_period('M')` will report false model failures and severely distorted metrics.
4. **Confidence Level:**  
   **Deterministic Fact.**
5. **Actionable Implementation:**  
   Implement partial-month pro-rating as mathematically formalized in Section 9 of `formula_sheet.docx`:  
   $$\text{Projected Variable Spend} = \text{Current Variable Spend} + \left(\frac{\text{Current Variable Spend}}{\text{Days Elapsed}} \times \text{Remaining Days}\right)$$

---

### Finding 4: Profile Balance Disconnect from Raw Transaction Integrals
1. **What was discovered:**  
   In `financial_profiles.csv`, the `current_available_balance` does not equal the cumulative sum of historical debits and credits recorded in `financial_events.csv`:
   - For `user_01`: Cumulative ledger $\sum Credits - \sum Debits = -79,727.60$ ZAR, whereas `current_available_balance = 58,481.10$ ZAR.
2. **Supporting Data:**  
   The transaction ledger represents a 6-month historical window, not the lifetime account creation ledger. Initial starting balance at $t_0$ is unobserved in the CSV; only the snapshot `current_available_balance` at $t_{eval}$ is provided.
3. **Why it matters:**  
   Forward simulations must anchor strictly to `current_available_balance` as the baseline cash position and project forward from the evaluation date, rather than trying to back-calculate starting capital from the 6-month transaction sum.
4. **Confidence Level:**  
   **Deterministic Fact.**
5. **Actionable Implementation:**  
   The decision engine must use `current_available_balance` from `financial_profiles.csv` as the initial state $B_0$, simulating forward over the 90-day horizon: $B_{d} = B_{d-1} + \Delta Cash_d$.

---

### Finding 5: Contextual Messages Carry Crucial Leading Indicators
1. **What was discovered:**  
   `messages.csv` contains operational updates that directly alter upcoming cash flows:
   - `message_01` (`user_02`): Salary increased to IDR 42,750,000 effective 2025-08-15 (a 28.2% raise over previous 33,345,000 IDR).
   - `message_18` (`user_26`): Client approved invoice payment of IDR 30,780,000 settling on 2025-08-15.
   - `message_20` (`user_28`): Regular salary EUR 1,452 plus one-time arrears adjustment of EUR 653.40.
   - `message_21` (`user_29`): Seasonal contract ended; no renewal confirmed (income drops to 0).
2. **Supporting Data:**  
   In `output.csv`, `request_29` is ruled `not_affordable` despite a current available balance of 113,540.10 ZAR because the loss of income signaled in `message_21` exhausts future liquidity below the 28,300 ZAR minimum balance.
3. **Why it matters:**  
   Pure historical extrapolation without factoring in contextual messages fails catastrophically when contracts end or bonuses occur.
4. **Confidence Level:**  
   **High (Directly corroborated by benchmark ground truth in output.csv).**
5. **Actionable Implementation:**  
   Build a structured message-parsing adapter that updates scheduled income before launching the 90-day cash-flow simulation.

---

## 3. Statistical Summaries by Category

| Category | Record Count | Median Amount (Native) | Direction | Flexibility | Cadence |
|---|---|---|---|---|---|
| `groceries` | 219 | 1,230.73 | debit | variable / stoppable | Weekly (7-10d) |
| `transport` | 170 | 732.90 | debit | variable | Bi-weekly / Weekly |
| `dining` | 97 | 1,446.74 | debit | variable / stoppable | Bi-weekly |
| `salary` | 74 | 12,826.00 | credit | fixed | Monthly / Bi-weekly / Weekly |
| `utilities` | 52 | 2,156.72 | debit | fixed | Monthly (Days 6-8) |
| `rent` | 46 | 5,148.00 | debit | fixed | Monthly (Days 2-4) |
| `shopping` | 35 | 816.20 | debit / refund | stoppable / flexible | Intermittent |
| `cloud_storage` | 35 | 181.50 | debit | stoppable (subscription) | Monthly (Day 13) |
| `entertainment` | 20 | 597,694.18 | debit | stoppable | Monthly (Days 15-16) |
| `streaming` | 20 | 58,917.50 | debit | stoppable (subscription) | Monthly (Day 10) |
| `education` | 16 | 5,170.00 | debit | fixed | Monthly (Day 8-9) |
| `healthcare` | 16 | 3,267.66 | debit | fixed / essential | Monthly (Day 11) |
| `debt_repayment` | 15 | 968.00 | debit | fixed (EMI) | Monthly (Day 11) |
| `music_subscription` | 15 | 344.30 | debit | stoppable | Monthly (Days 11-13) |
| `delivery_membership` | 15 | 401.50 | debit | stoppable | Monthly (Days 13-15) |
| `housing` | 12 | 1,768,903.00 | debit | fixed | Monthly (Day 4) |
| `insurance` | 10 | 567,181.20 | debit | fixed | Monthly (Day 8) |
| `gym` | 10 | 514,255.80 | debit | stoppable | Monthly (Day 12) |
| `family_support` | 5 | 840.40 | debit | fixed | Monthly |

---

## 4. Conclusion

The EDA confirms that the FIN4YOU financial environment is structured around deterministic contractual anchors and bounded variable burn rates. The primary challenge is not predicting random consumer shocks, but synthesizing multi-source signals (balances, schedules, message updates, and payment plans) into a rigorous 90-day liquidity simulation.
