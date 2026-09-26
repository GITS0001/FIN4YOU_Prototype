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
} from '../types';

export const usersApi = {
  getProfile: async (userId: string): Promise<FinancialProfile> => {
    const response = await apiClient.get<FinancialProfile>(`/api/users/${userId}/profile`);
    return response.data;
  },

  updateProfile: async (userId: string, profile: FinancialProfile): Promise<FinancialProfile> => {
    const response = await apiClient.put<FinancialProfile>(`/api/users/${userId}/profile`, profile);
    return response.data;
  },

  getState: async (userId: string): Promise<FinancialState> => {
    const response = await apiClient.get<FinancialState>(`/api/users/${userId}/state`);
    return response.data;
  },

  getPrediction: async (userId: string): Promise<PredictionEngineResult> => {
    const response = await apiClient.get<PredictionEngineResult>(`/api/users/${userId}/prediction`);
    return response.data;
  },

  getForecastHistory: async (userId: string): Promise<MonthlyHistoryResponse> => {
    const response = await apiClient.get<MonthlyHistoryResponse>(`/api/users/${userId}/forecast/history`);
    return response.data;
  },

  checkAffordability: async (userId: string, amount: number): Promise<AffordabilityResult> => {
    const response = await apiClient.post<AffordabilityResult>(
      `/api/users/${userId}/affordability`,
      { amount }
    );
    return response.data;
  },

  runWhatIf: async (
    userId: string,
    scenario_type: 'reduce_expense' | 'add_purchase',
    amount: number
  ): Promise<WhatIfResponse> => {
    const response = await apiClient.post<WhatIfResponse>(
      `/api/users/${userId}/what-if`,
      { scenario_type, amount }
    );
    return response.data;
  },

  getGlobalState: async (userId: string, overrides?: FinancialOverrides): Promise<GlobalFinancialState> => {
    const response = await apiClient.post<GlobalFinancialState>(
      `/api/users/${userId}/financial-state`,
      overrides || {}
    );
    return response.data;
  },
};
