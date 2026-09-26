// ─── Financial Types (mirror FastAPI schemas) ────────────────────────────────

export interface Transaction {
  transaction_id: string;
  user_id: string;
  event_type: string;
  description: string;
  category: string;
  direction: string;
  amount: number;
  currency: string;
  event_date: string;
  settlement_date?: string;
  status: string;
  flexibility: string;
}

export interface FinancialProfile {
  user_id: string;
  home_currency: string;
  current_available_balance: number;
  minimum_balance_to_keep: number;
  financial_priorities: string[];
  expense_categories_to_protect: string[];
  expense_categories_user_is_willing_to_reduce: string[];
  expense_categories_user_is_willing_to_stop: string[];
  payment_methods_user_will_consider: string[];
  max_installment_months?: number;
}

export interface CategorySpending {
  category: string;
  total_amount: number;
}

export interface AnomalySignal {
  transaction_id: string;
  is_anomaly: boolean;
  anomaly_score: number;
  reason: string;
}

export interface FinancialState {
  user_id: string;
  income: number;
  expenses: number;
  savings: number;
  savings_rate: number;
  expense_ratio: number;
  essential_expenses: number;
  discretionary_expenses: number;
  recurring_obligations: number;
  emi_burden: number;
  cash_flow: number;
  category_spending: CategorySpending[];
  anomalies: AnomalySignal[];
  data_quality_confidence: number;
}

export interface ForecastEvaluation {
  mae?: number;
  rmse?: number;
}

export interface ForecastResult {
  target: string;
  period: string;
  predicted_value: number;
  model: string;
  uncertainty: number;
  evaluation?: ForecastEvaluation;
}

export interface FutureObligation {
  description: string;
  category: string;
  expected_amount: number;
  expected_period: string;
}

export interface ProjectedCashFlow {
  period: string;
  projected_income: number;
  projected_expenses: number;
  known_obligations: number;
  projected_cash_flow: number;
}

export interface CashFlowGap {
  detected: boolean;
  period: string;
  projected_balance: number;
  required_buffer: number;
  shortfall: number;
}

export interface PredictionEngineResult {
  available: boolean;
  reason?: string;
  forecasts: ForecastResult[];
  obligations: FutureObligation[];
  projected_cash_flow?: ProjectedCashFlow;
  gap_detection?: CashFlowGap;
}

// ─── Monthly History (new endpoint) ──────────────────────────────────────────

export interface MonthlyDataPoint {
  month: string;
  income: number;
  variable_expenses: number;
  known_obligations: number;
  cash_flow: number;
  is_projected: boolean;
}

export interface MonthlyHistoryResponse {
  user_id: string;
  observed_months: number;
  period_start?: string;
  period_end?: string;
  history: MonthlyDataPoint[];
  projected?: MonthlyDataPoint;
}

// ─── Decision / Copilot Types ─────────────────────────────────────────────────

export interface PaymentOption {
  payment_option_id: string;
  request_id: string;
  payment_method: string;
  payment_amount: number;
  number_of_payments: number;
  first_payment_date: string;
  payment_frequency_days?: number;
  financing_fee: number;
  total_payable_amount: number;
}

export interface AffordabilityResult {
  status: string;
  proposed_expense_amount: number;
  resulting_balance: number;
  shortfall: number;
  viable_payment_options: PaymentOption[];
  trade_off_required: number;
}

export interface ExpectedImpact {
  cash_flow_difference: number;
  balance_difference: number;
  buffer_status_change: string;
}

export interface Recommendation {
  recommendation_type: string;
  actionable_text: string;
  expected_impact: ExpectedImpact;
  confidence_level: string;
  confidence_reason: string;
}

export interface DecisionTrace {
  observed_fact: string;
  calculation: string;
  prediction: string;
  simulation: string;
  recommendation: Recommendation;
  supporting_data: Record<string, number>;
}

export interface ScenarioResult {
  scenario_name: string;
  projected_income: number;
  projected_expenses: number;
  known_obligations: number;
  projected_cash_flow: number;
  projected_balance: number;
  shortfall: number;
  buffer_breached: boolean;
}

export interface WhatIfResponse {
  baseline: ScenarioResult;
  scenario: ScenarioResult;
  impact: ExpectedImpact;
  currency: string;
}

export type IntentType =
  | 'FINANCIAL_SUMMARY'
  | 'SPENDING_ANALYSIS'
  | 'CASH_FLOW_FORECAST'
  | 'AFFORDABILITY_CHECK'
  | 'WHAT_IF'
  | 'RECOMMENDATION'
  | 'PAYMENT_OPTION_ANALYSIS'
  | 'UNKNOWN';

export interface CopilotRequest {
  user_id: string;
  message: string;
}

export interface CopilotResponse {
  intent: IntentType;
  response: string;
  decision_trace?: DecisionTrace;
  structured_result?: Record<string, unknown>;
  confidence: string;
  status: string;
  data_sources: string[];
}

// ─── UI-specific types ────────────────────────────────────────────────────────

export interface ChatMessage {
  id: string;
  role: 'user' | 'ai';
  content: string;
  response?: CopilotResponse;
  timestamp: Date;
}

export type ApiStatus = 'idle' | 'loading' | 'success' | 'error';

export interface ApiError {
  message: string;
  status?: number;
}
