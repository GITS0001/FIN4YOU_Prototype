import { apiClient } from './client';

export const alertsApi = {
  getAlerts: async () => {
    const response = await apiClient.get('/api/alerts');
    return response.data;
  },
};

export const statementsApi = {
  uploadStatement: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/api/statements/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};
