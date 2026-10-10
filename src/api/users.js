import { apiClient } from './client';

export const usersApi = {
  // 1. User Profile
  getProfile: async () => {
    const response = await apiClient.get('/api/users/profile');
    return response.data;
  },

  updateProfile: async (profileData) => {
    const response = await apiClient.put('/api/users/profile', profileData);
    return response.data;
  },

  // 2. Financial State & Core Ledger Metrics
  getState: async () => {
    const response = await apiClient.get('/api/users/state');
    return response.data;
  },

  getGlobalFinancialState: async (overrides = {}) => {
    const response = await apiClient.post('/api/users/financial-state', overrides);
    return response.data;
  },

  // 3. Transactions & Ledger
  getTransactions: async (limit = 100) => {
    const response = await apiClient.get(`/api/users/transactions?limit=${limit}`);
    return response.data;
  },

  createTransaction: async (txData) => {
    const response = await apiClient.post('/api/users/transactions', txData);
    return response.data;
  },

  deleteTransaction: async (transactionId) => {
    const response = await apiClient.delete(`/api/users/transactions/${transactionId}`);
    return response.data;
  },

  // 4. Prediction Engine & Forecasting
  getPrediction: async () => {
    const response = await apiClient.get('/api/users/prediction');
    return response.data;
  },

  getForecastHistory: async () => {
    const response = await apiClient.get('/api/users/forecast/history');
    return response.data;
  },

  getProbabilisticForecast: async (payload = { months_ahead: 6, num_simulations: 500 }) => {
    const response = await apiClient.post('/api/users/forecast/probabilistic', payload);
    return response.data;
  },

  getFinancialSummaries: async () => {
    const response = await apiClient.get('/api/users/financial-summaries');
    return response.data;
  },

  getMonthlyReports: async () => {
    const response = await apiClient.get('/api/users/monthly-reports');
    return response.data;
  },

  getMonthlyStatement: async () => {
    const response = await apiClient.get('/api/users/monthly-statement');
    return response.data;
  },

  // 5. Decision Engine: Affordability & What-If Simulations
  checkAffordability: async (amount) => {
    const response = await apiClient.post('/api/users/affordability', { amount: Number(amount) });
    return response.data;
  },

  runWhatIf: async (scenarioType, amount) => {
    const response = await apiClient.post('/api/users/what-if', {
      scenario_type: scenarioType,
      amount: Number(amount),
    });
    return response.data;
  },

  evaluatePlanner: async (planPayload) => {
    const response = await apiClient.post('/api/users/planner/evaluate', planPayload);
    return response.data;
  },
};
