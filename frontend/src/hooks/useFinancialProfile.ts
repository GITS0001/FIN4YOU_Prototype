import { useState, useEffect, useCallback } from 'react';
import { usersApi } from '../api/users';
import { DEMO_USER_ID } from '../api/client';
import type { FinancialProfile, ApiStatus, ApiError } from '../types';

export function useFinancialProfile(userId: string = DEMO_USER_ID) {
  const [data, setData] = useState<FinancialProfile | null>(null);
  const [status, setStatus] = useState<ApiStatus>('idle');
  const [error, setError] = useState<ApiError | null>(null);

  const fetch = useCallback(async () => {
    setStatus('loading');
    setError(null);
    try {
      const profile = await usersApi.getProfile(userId);
      setData(profile);
      setStatus('success');
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError);
      setStatus('error');
    }
  }, [userId]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { data, status, error, refetch: fetch };
}
