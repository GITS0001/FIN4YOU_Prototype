import { apiClient } from './client';

/**
 * FIN4YOU API Service Layer
 * Centralized API calls connecting React frontend components to FastAPI backend services.
 */

// 1. User Profile API
export const getUserProfile = async () => {
  const response = await apiClient.get('/api/users/profile');
  return response.data;
};

export const updateUserProfile = async (profileData) => {
  const response = await apiClient.put('/api/users/profile', profileData);
  return response.data;
};

// 2. Financial State & Summary API
export const getFinancialState = async () => {
  const response = await apiClient.get('/api/users/state');
  return response.data;
};

export const getMonthlyStatement = async () => {
  const response = await apiClient.get('/api/users/monthly-statement');
  return response.data;
};

// 3. Transactions API
export const getTransactions = async (limit = 100) => {
  const response = await apiClient.get('/api/users/transactions', {
    params: { limit },
  });
  return response.data;
};

export const createTransaction = async (transactionData) => {
  const response = await apiClient.post('/api/users/transactions', transactionData);
  return response.data;
};

export const deleteTransaction = async (transactionId) => {
  const response = await apiClient.delete(`/api/users/transactions/${transactionId}`);
  return response.data;
};

// 4. Statement Ingestion / CSV & PDF Upload API
export const parseStatementPreview = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiClient.post('/api/statements/parse', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const confirmStatementImport = async (transactions) => {
  const response = await apiClient.post('/api/statements/confirm', { transactions });
  return response.data;
};

export const uploadStatementCsv = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiClient.post('/api/statements/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};
export const uploadStatement = uploadStatementCsv;

// 5. Forecast & Prediction API
export const getForecastHistory = async () => {
  const response = await apiClient.get('/api/users/forecast/history');
  return response.data;
};

export const getPredictionSummary = async () => {
  const response = await apiClient.get('/api/users/prediction');
  return response.data;
};

export const getProbabilisticForecast = async (options = {}) => {
  const response = await apiClient.post('/api/users/forecast/probabilistic', options);
  return response.data;
};

export const evaluatePlannerPlans = async (planOptions = {}) => {
  const response = await apiClient.post('/api/users/planner/evaluate', planOptions);
  return response.data;
};

// 6. Decision & Simulation API
export const checkAffordability = async (amount) => {
  const response = await apiClient.post('/api/users/affordability', { amount });
  return response.data;
};

export const runWhatIfSimulation = async (scenarioType, amount) => {
  const response = await apiClient.post('/api/users/what-if', {
    scenario_type: scenarioType,
    amount,
  });
  return response.data;
};

// 7. Copilot AI Assistant API
export const queryCopilot = async (message) => {
  const response = await apiClient.post('/api/copilot/query', { message });
  return response.data;
};

// 8. Alerts & Anomalies API
export const getAlerts = async () => {
  const response = await apiClient.get('/api/alerts');
  return response.data;
};
