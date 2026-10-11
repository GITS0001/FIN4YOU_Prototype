import { apiClient } from './client';
import type { CopilotRequest, CopilotResponse } from '../types';

export const copilotApi = {
  query: async (request: CopilotRequest): Promise<CopilotResponse> => {
    const response = await apiClient.post<CopilotResponse>('/api/copilot/query', request);
    return response.data;
  },
};
