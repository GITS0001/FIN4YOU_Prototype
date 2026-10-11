import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/client';
import type { FinancialProfile, ApiStatus, ApiError } from '../types';

export const useFinancialProfile = () => {
  const [data, setData] = useState<FinancialProfile | null>(null);
  const [status, setStatus] = useState<ApiStatus>('idle');
  const [error, setError] = useState<ApiError | null>(null);

  const fetchProfile = useCallback(async () => {
    setStatus('loading');
    try {
      const response = await apiClient.get<FinancialProfile>('/api/users/profile');
      setData(response.data);
      setStatus('success');
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch profile:', err);
      setError({ message: err.message || 'Failed to fetch financial profile' });
      setStatus('error');
    }
  }, []);

  const update = async (profileUpdate: Partial<FinancialProfile>) => {
    setStatus('loading');
    try {
      const response = await apiClient.put<FinancialProfile>('/api/users/profile', profileUpdate);
      setData(response.data);
      setStatus('success');
      setError(null);
    } catch (err: any) {
      console.error('Failed to update profile:', err);
      setError({ message: err.message || 'Failed to update financial profile' });
      setStatus('error');
      throw err;
    }
  };

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  return { data, status, error, isLoading: status === 'loading', refetch: fetchProfile, update };
};
