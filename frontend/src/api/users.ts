import { apiClient } from './client';
import type {
  FinancialProfile,
  FinancialState,
  PredictionEngineResult,
  MonthlyHistoryResponse,
  AffordabilityResult,
  WhatIfResponse,
  GlobalFinancialState,
  FinancialOverrides,
  Transaction
} from '../types';

export const usersApi = {
  getProfile: async (): Promise<FinancialProfile> => {
    const response = await apiClient.get<FinancialProfile>(`/api/users/profile`);
    return response.data;
  },

  updateProfile: async (profile: FinancialProfile): Promise<FinancialProfile> => {
    const response = await apiClient.put<FinancialProfile>(`/api/users/profile`, profile);
    return response.data;
  },

  getState: async (): Promise<FinancialState> => {
    const response = await apiClient.get<FinancialState>(`/api/users/state`);
    return response.data;
  },

  getPrediction: async (): Promise<PredictionEngineResult> => {
    const response = await apiClient.get<PredictionEngineResult>(`/api/users/prediction`);
    return response.data;
  },

  getForecastHistory: async (): Promise<MonthlyHistoryResponse> => {
    const response = await apiClient.get<MonthlyHistoryResponse>(`/api/users/forecast/history`);
    return response.data;
  },

  checkAffordability: async (amount: number): Promise<AffordabilityResult> => {
    const response = await apiClient.post<AffordabilityResult>(
      `/api/users/affordability`,
      { amount }
    );
    return response.data;
  },

  runWhatIf: async (
    scenario_type: 'reduce_expense' | 'add_purchase',
    amount: number
  ): Promise<WhatIfResponse> => {
    const response = await apiClient.post<WhatIfResponse>(
      `/api/users/what-if`,
      { scenario_type, amount }
    );
    return response.data;
  },

  getGlobalState: async (overrides?: FinancialOverrides): Promise<GlobalFinancialState> => {
    const response = await apiClient.post<GlobalFinancialState>(
      `/api/users/financial-state`,
      overrides || {}
    );
    return response.data;
  },

  getTransactions: async (limit: number = 5): Promise<Transaction[]> => {
    const response = await apiClient.get<Transaction[]>(`/api/users/transactions?limit=${limit}`);
    return response.data;
  },
};
