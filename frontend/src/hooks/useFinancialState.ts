import { useState, useEffect, useCallback } from 'react';
import { usersApi } from '../api/users';
import { DEMO_USER_ID } from '../api/client';
import type { FinancialState, ApiStatus, ApiError } from '../types';

export function useFinancialState(userId: string = DEMO_USER_ID) {
  const [data, setData] = useState<FinancialState | null>(null);
  const [status, setStatus] = useState<ApiStatus>('idle');
  const [error, setError] = useState<ApiError | null>(null);

  const fetch = useCallback(async () => {
    setStatus('loading');
    setError(null);
    try {
      const state = await usersApi.getState(userId);
      setData(state);
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
