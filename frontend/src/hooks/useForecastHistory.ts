import { useState, useEffect, useCallback } from 'react';
import { usersApi } from '../api/users';
import { useSelectedUser } from '../context/UserContext';
import type { MonthlyHistoryResponse } from '../types';

export const useForecastHistory = () => {
  const { selectedUserId } = useSelectedUser();
  const [data, setData] = useState<MonthlyHistoryResponse | null>(null);
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [error, setError] = useState<Error | null>(null);

  const fetchHistory = useCallback(async () => {
    if (!selectedUserId) return;
    setStatus('loading');
    try {
      const result = await usersApi.getForecastHistory(selectedUserId);
      setData(result);
      setStatus('success');
      setError(null);
    } catch (err: any) {
      setError(new Error(err.message || 'Failed to fetch forecast history'));
      setStatus('error');
    }
  }, [selectedUserId]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return {
    data,
    status,
    error,
    refetch: fetchHistory,
  };
};
