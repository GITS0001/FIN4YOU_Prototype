# Phase 5A: Copilot API & Natural-Language Intent Routing

## Architecture
The Phase 5A Copilot layer serves as a natural-language bridge between the user and the deterministic financial intelligence developed in Phases 1–4. The system is designed according to the principle:
**LLM understands. Python calculates. Decision Engine decides. LLM explains.**

1. **User Request**: The user submits a natural-language query.
2. **Intent Parser**: The orchestrator parses the query into a structured `ParsedIntent` containing the identified intent and extracted values (e.g., amounts, categories) using a deterministic fallback parsing method, which isolates logic and ensures reliability.
3. **Orchestrator**: The query is routed to the correct deterministic Phase 1–4 engine (e.g., `AffordabilityEngine`, `WhatIfSimulator`).
4. **Deterministic Calculation**: The engines calculate exact mathematical outcomes and structured responses.
5. **Response Generator**: The result is translated back into natural language.

## LLM vs. Deterministic Responsibilities
**LLM Responsibilities:**
- Parsing intents from natural language.
- Extracting exact numeric values or categories from user prompts.
- Explaining structured output arrays, strings, and Decision Traces in conversational language.

**Deterministic Engine Responsibilities:**
- Performing ALL calculations (balance, income, expenses, cash flow, shortfalls).
- Determining affordability and buffer breaches.
- Generating trade-off required amounts.
- Determining confidence bounds based on historical data volume.

## Intent List
- `FINANCIAL_SUMMARY`: Summarizes current balance and cash flow.
- `SPENDING_ANALYSIS`: Retrieves categorized spending intelligence.
- `CASH_FLOW_FORECAST`: Calculates projected balances and future cash flow.
- `AFFORDABILITY_CHECK`: Checks if a specific amount breaches the safety buffer.
- `WHAT_IF`: Simulates changes to discretionary spending.
- `RECOMMENDATION`: Identifies gaps and proposes trade-offs.
- `PAYMENT_OPTION_ANALYSIS`: Checks the affordability of financing plans/installments.
- `UNKNOWN`: Fallback for unrecognized or unsupported queries (e.g., investment advice).

## Request / Response Schema
**Request Payload:**
```json
{
    "user_id": "user_28",
    "message": "Can I afford to spend 1302.4 in installments?"
}
```

**Response Payload:**
```json
{
    "intent": "PAYMENT_OPTION_ANALYSIS",
    "response": "While paying upfront might be tight, you can afford these installment options:\nOption payment_option_79: 24 payments of 66.21...",
    "decision_trace": null,
    "structured_result": {
        "affordability_status": "NOT AFFORDABLE UNDER CURRENT PROJECTION",
        "viable_options": [ ... ]
    },
    "confidence": "HIGH",
    "status": "SUCCESS",
    "data_sources": ["financial_profiles", "financial_events", "PredictionEngine", "DecisionEngine"]
}
```

## Error & Fallback Behavior
- **Unsupported Query**: If a query falls outside the financial guardrails (e.g., stock market advice), the parser assigns the `UNKNOWN` intent, and the response generator explicitly refuses to hallucinate financial advice, returning `status: UNSUPPORTED`.
- **Insufficient Data**: If the user lacks 3 months of history, the `PredictionEngine` flags it. The API respects this flag and returns `status: INSUFFICIENT_DATA` rather than guessing a forecast.
- **LLM Failure**: For this MVP, a robust regex/heuristic parser and response generator act as the fallback. This proves the deterministic pipeline can operate completely independently of an LLM.

## User 28 Demo Flow
**Action**: User 28 wants to purchase an item for 1,302.4.
1. The parser extracts the intent `PAYMENT_OPTION_ANALYSIS` and amount `1302.4`.
2. The orchestrator triggers the `AffordabilityEngine`.
3. The engine mathematically determines that an upfront payment breaches the safety buffer by 294.66.
4. However, the engine evaluates available installment options from `request_payment_options.csv` and verifies that Options 79 (24 mo) and 80 (21 mo) *can* be mathematically afforded without breaching the buffer.
5. The generator returns a natural-language response highlighting the viable options and the underlying structural outcome.
