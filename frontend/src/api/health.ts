import { apiClient } from './client';

// Health check for the backend
export const healthApi = {
  check: async (): Promise<{ status: string; message: string }> => {
    const response = await apiClient.get<{ status: string; message: string }>('/');
    return response.data;
  },
};
