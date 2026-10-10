import { apiClient } from './client';

export const copilotApi = {
  query: async (message) => {
    const response = await apiClient.post('/api/copilot/query', { message });
    return response.data;
  },
};
