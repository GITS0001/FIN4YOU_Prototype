FIN02 Financial Health Copilot – Complete Formula Sheet

Calculation reference for the Financial Decision Engine. Python should perform all financial calculations; ML handles classification, anomaly detection and forecasting; the LLM should explain results rather than calculate them.

1. Basic Financial State

Total Income: Total Income = Σ Income Transactions

Total Expenses: Total Expenses = Σ Expense Transactions

Net Cash Flow / Monthly Surplus: Net Cash Flow = Total Income − Total Expenses

Savings: Monthly Savings = Monthly Income − Monthly Expenses

Savings Rate: Savings Rate (%) = (Monthly Savings / Monthly Income) × 100

Expense-to-Income Ratio: Expense Ratio (%) = (Total Expenses / Total Income) × 100

2. Category & Food Spending

Category Spend: Category Spend = Σ transactions belonging to the category

Category Percentage: Category % = (Category Spend / Total Expenses) × 100

Average Daily Spend: Average Daily Spend = Category Spend / Number of Days

Average Transaction: Average Transaction = Category Spend / Number of Category Transactions

Monthly Average: Monthly Average = Average of monthly category spending values

Spending Change: Percentage Change (%) = ((Current Value − Previous Value) / Previous Value) × 100

3. Fixed, Variable & Recurring Expenses

Fixed Expenses: Fixed Expenses = Σ fixed obligations

Variable Expenses: Variable Expenses = Σ variable expenses

Total Expenses: Total Expenses = Fixed Expenses + Variable Expenses

Monthly Recurring Cost: Monthly Recurring Cost = Σ monthly recurring payments

Annual Payment → Monthly Equivalent: Monthly Equivalent = Annual Payment / 12

Quarterly Payment → Monthly Equivalent: Monthly Equivalent = Quarterly Payment / 3

Annual Recurring Cost: Annual Recurring Cost = Monthly Recurring Cost × 12

Subscription Burden: Subscription Burden (%) = (Monthly Subscriptions / Monthly Income) × 100

Recurring Obligation Ratio: Recurring Obligation Ratio (%) = (Fixed Recurring Expenses / Monthly Income) × 100

4. Loan & EMI Calculations

Monthly Interest Rate: r = Annual Interest Rate / (12 × 100)

Number of Monthly Payments: n = Loan Tenure in Years × 12

EMI: EMI = P × [r(1+r)^n] / [(1+r)^n − 1]

Total Loan Payment: Total Loan Payment = EMI × n

Total Interest: Total Interest = Total Loan Payment − Principal

Remaining Loan Balance: Bₖ = P(1+r)^k − EMI × [(1+r)^k − 1] / r

Meaning of k: k = Number of EMI payments already made

EMI Burden: EMI Burden (%) = (Total Monthly EMI / Monthly Income) × 100

Debt-to-Income Ratio (DTI): DTI (%) = (Monthly Debt Payments / Gross Monthly Income) × 100

Total Debt: Total Debt = Σ outstanding loan balances

Debt-to-Asset Ratio: Debt-to-Asset Ratio (%) = (Total Debt / Total Assets) × 100

5. Insurance

Monthly Insurance Equivalent: Monthly Insurance Cost = Annual Premium / 12

Total Insurance Premium: Total Insurance Premium = Σ insurance premiums

Insurance Burden: Insurance Burden (%) = (Annual Insurance Premium / Annual Income) × 100

6. Savings & Financial Goals

Goal Gap: Goal Gap = Target Amount − Current Savings

Required Monthly Savings: Required Monthly Savings = Goal Gap / Months Remaining

Monthly Savings Gap: Savings Gap = Required Monthly Savings − Current Monthly Savings

Emergency Fund Coverage: Emergency Fund Months = Liquid Savings / Average Monthly Essential Expenses

7. Essential & Discretionary Expenses

Essential Expenses: Essential Expenses = Rent + Food + Utilities + EMI + Insurance + Healthcare + Other Essential Expenses

Discretionary Spending: Discretionary Spending = Total Expenses − Essential Expenses

Discretionary Ratio: Discretionary Ratio (%) = (Discretionary Spending / Monthly Income) × 100

Free Cash Flow: Free Cash Flow = Income − Essential Expenses − Debt Payments

8. Cash Flow & Future Cash Flow

Ending Balance: Ending Balance = Beginning Balance + Income − Expenses

Expected Expenses: Expected Expenses = Expected Fixed Expenses + Expected Variable Expenses + Expected Debt Payments

Projected Ending Balance: Projected Ending Balance = Current Balance + Expected Income − Expected Expenses

Upcoming Obligations: Upcoming Obligations = Σ upcoming Rent + EMI + Insurance + Subscriptions + Other Obligations

Post-Obligation Balance: Post-Obligation Balance = Current Balance − Upcoming Obligations

Projected Buffer: Projected Buffer = Projected Ending Balance − Minimum Safe Buffer

Minimum Safe Buffer: Minimum Safe Buffer can be defined as expected essential expenses for the selected safety period

9. Month-End Forecast

Daily Variable Spend: Daily Spend = Current Variable Spend / Days Elapsed

Remaining Spend: Remaining Spend = Daily Spend × Remaining Days

Projected Monthly Variable Spend: Projected Monthly Variable Spend = Current Spend + Remaining Spend

MVP Forecast: For an MVP, historical average spending can be used as the baseline forecast.

10. Affordability

Post-Purchase Balance: Post-Purchase Balance = Projected Balance − Purchase Price

Post-Purchase Buffer: Post-Purchase Buffer = Post-Purchase Balance − Expected Essential Expenses

Purchase Impact: Purchase Impact = Post-Purchase Buffer − Current/Pre-Purchase Buffer

11. What-If Scenario Engine

Expense Reduction: New Surplus = Current Surplus + Expense Reduction

Monthly Impact: Monthly Impact = New Surplus − Current Surplus

Cumulative Impact: Cumulative Impact = Monthly Impact × Number of Months

Income Change: New Income = Current Income ± Income Change

New Surplus After Income Change: New Surplus = New Income − Expected Expenses

EMI Increase: EMI Increase = New EMI − Current EMI

Surplus After EMI Increase: New Surplus = Current Surplus − EMI Increase

Subscription Cancellation: New Monthly Expense = Current Monthly Expense − Subscription Cost

Surplus After Subscription Cancellation: New Monthly Surplus = Current Monthly Surplus + Subscription Cost

Annual Subscription Impact: Annual Impact = Monthly Subscription Cost × 12

Food Spending Reduction: New Surplus = Current Surplus + Food Spending Reduction

Multiple Changes: Total Impact = Σ individual monthly impacts; New Surplus = Current Surplus + Total Impact

12. Unknown Transactions & Uncertainty

Known Expenses: Known Expenses = Total Expenses − Unknown Expenses

Unknown Expense Ratio: Unknown Ratio (%) = (Unknown Expenses / Total Expenses) × 100

Transaction Confidence: ML outputs predicted category + confidence/probability. Low-confidence transactions should be flagged for confirmation.

User Correction: After a user changes a category, recalculate category totals, financial state, forecast and recommendations.

13. Anomaly Detection

Mean: μ = Σx / N

Standard Deviation: σ = sqrt(Σ(x − μ)^2 / N)  [population form]

Z-Score: Z = (x − μ) / σ

Interpretation: A large absolute Z-score indicates that a transaction is unusual relative to the chosen historical baseline. Thresholds should be validated on the dataset.

14. Recommendation Expected Impact

Before Action: Current Surplus = Income − Expenses

After Action: New Surplus = Income − New Expenses

Recommendation Impact: Impact = New Surplus − Current Surplus

Monthly Improvement: Monthly Improvement = New Surplus − Current Surplus

Cumulative Improvement: Cumulative Improvement = Monthly Improvement × Number of Months

15. Financial Health Metrics to Display

Savings Rate: Savings Rate (%) = Savings / Income × 100

Expense Ratio: Expense Ratio (%) = Expenses / Income × 100

EMI Burden: EMI Burden (%) = EMI / Income × 100

Emergency Coverage: Emergency Fund Months = Liquid Savings / Essential Monthly Expenses

Recurring Obligation Ratio: Recurring Obligation Ratio (%) = Fixed Recurring Expenses / Income × 100

Important Design Rule: Display these metrics separately rather than hiding them inside an arbitrary single health score.

16. Important Variable Definitions

P — Original loan principal

r — Monthly interest rate in decimal form

n — Total number of monthly EMI payments

k — Number of EMI payments already made

EMI — Monthly loan installment

Bₖ — Remaining loan balance after k payments

Income — Money received during the selected period

Expenses — Money spent during the selected period

Current Balance — Available/current account balance used by the model

Monthly Surplus — Income minus expenses for the selected month

Liquid Savings — Savings that can reasonably be accessed for emergencies

17. Recommended Calculation Architecture

Python = financial calculationsPandas/NumPy = aggregation and numerical processingML = transaction categorization, anomaly detection and forecastingRules/validation = sanity checks and safety constraintsLLM = natural-language question understanding and explanationFrontend = evidence, confidence and expected-impact visualization

18. Core Principle for FIN02

Do not let the LLM directly calculate EMI, remaining loan balance, savings, debt, affordability or cash-flow values. The calculation engine should produce the numerical result, and the LLM should explain that result using the structured financial state.