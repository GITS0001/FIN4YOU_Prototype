import { apiClient } from './client';
import type { FinancialProfile, FinancialState, PredictionEngineResult } from '../types';

export const usersApi = {
  getProfile: async (userId: string): Promise<FinancialProfile> => {
    const response = await apiClient.get<FinancialProfile>(`/api/users/${userId}/profile`);
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
};
