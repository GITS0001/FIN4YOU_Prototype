import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/client';

export interface Alert {
  id: string;
  type: 'warning' | 'danger' | 'info';
  title: string;
  message: string;
  is_read: boolean;
  timestamp: string;
}

export const useAlerts = () => {
  const [data, setData] = useState<Alert[] | null>(null);
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [error, setError] = useState<Error | null>(null);

  const fetchAlerts = useCallback(async () => {
    setStatus('loading');
    try {
      const response = await apiClient.get<Alert[]>('/api/alerts');
      setData(response.data);
      setStatus('success');
      setError(null);
    } catch (err: any) {
      setError(new Error(err.message || 'Failed to fetch alerts'));
      setStatus('error');
    }
  }, []);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  return {
    data,
    status,
    error,
    refetch: fetchAlerts,
  };
};
