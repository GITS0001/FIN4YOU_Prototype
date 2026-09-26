import { useState, useEffect, useCallback } from 'react';
import { usersApi } from '../api/users';
import { useSelectedUser } from '../context/UserContext';
import type { FinancialProfile, ApiStatus, ApiError } from '../types';

export function useFinancialProfile() {
  const { selectedUserId } = useSelectedUser();
  const [data, setData] = useState<FinancialProfile | null>(null);
  const [status, setStatus] = useState<ApiStatus>('idle');
  const [error, setError] = useState<ApiError | null>(null);

  const fetch = useCallback(async () => {
    setStatus('loading');
    setError(null);
    try {
      const profile = await usersApi.getProfile(selectedUserId);
      setData(profile);
      setStatus('success');
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError);
      setStatus('error');
    }
  }, [selectedUserId]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { data, status, error, refetch: fetch };
}
