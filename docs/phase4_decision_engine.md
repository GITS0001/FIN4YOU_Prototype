# Phase 4 - Decision Engine

## Problem Solved
FIN02 requires a system that converts transaction history into actionable insights and recommendations. A generic AI wrapper is insufficient because financial calculations must be exact, transparent, and auditable. Phase 4 introduces a deterministic Decision Engine that takes the projected facts from Phase 3 and mathematically simulates potential user decisions (what-if scenarios).

## Architecture
The Decision Engine consists of the following deterministic modules:
- **Simulation Engine (`WhatIfSimulator`)**: Accepts a `PredictionEngineResult` and creates `ScenarioResult`s by adjusting income, expenses, or obligations.
- **Impact Engine (`ImpactEngine`)**: Compares a `ScenarioResult` to the baseline, yielding an `ExpectedImpact` (cash flow diff, balance diff, buffer status).
- **Affordability Engine (`AffordabilityEngine`)**: Evaluates a proposed one-off expense or installment plan against projected cash flows to determine affordability and trade-offs.
- **Recommendation Engine (`DecisionEngine`)**: Uses the simulation and impact engines to produce a fully traceable `DecisionTrace`.

## Formulas and Logic
- **Projected Balance** = `Current Available Balance + Projected Cash Flow`
- **Shortfall** = `MAX(0, Minimum Balance Threshold - Projected Balance)`
- **Buffer Breached** = `Shortfall > 0`
- **Trade-off Required** = `Shortfall` (The amount of discretionary spending that must be reduced to afford an expense or maintain a buffer).

## Assumptions
- Recommendations assume that users can dynamically adjust discretionary spending up to 50% without severely impacting quality of life. 
- Refunds correctly reduce variable expenses, rather than inflating income (fixed in the Phase 1-3 technical audit).

## Scenario Logic
The system supports multiple mathematical scenarios:
1. **Baseline**: No behavioral changes.
2. **Reduce Discretionary Spending**: Modifies the `projected_expenses` downwards.
3. **Add Obligation**: Modifies the `known_obligations` upwards, evaluating if a purchase breaches the minimum balance.

## Affordability Rules
- **AFFORDABLE**: The resulting balance after the purchase remains above the minimum balance threshold.
- **POTENTIALLY AFFORDABLE WITH TRADE-OFF**: The purchase breaches the minimum balance threshold, but the shortfall is less than the projected discretionary spending (i.e., the user can afford it *if* they cut back elsewhere).
- **NOT AFFORDABLE**: The shortfall exceeds projected discretionary spending, or the resulting balance goes below zero.
- **INSUFFICIENT DATA**: Evaluated if Phase 3 lacked 3 months of historical data.

## Why This Approach is Explainable
Every recommendation is grounded in a `DecisionTrace`. The Trace strings together:
`Observed Fact -> Calculation -> Prediction -> Simulation -> Recommendation`.
This guarantees that no recommendation is hallucinated, and every insight traces mathematically back to the user's dataset. 

## Why the LLM Does Not Calculate Financial Values
LLMs are probabilistic token predictors, making them inherently prone to hallucination when computing exact arithmetic across arrays of transactions. The LLM's role in Phase 5 will solely be to parse natural language intent (e.g., "Can I afford this laptop?") and stringify the deterministic `DecisionTrace` into a conversational reply.
