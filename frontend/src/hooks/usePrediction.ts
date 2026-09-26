import { useState, useEffect, useCallback } from 'react';
import { usersApi } from '../api/users';
import { useSelectedUser } from '../context/UserContext';
import type { PredictionEngineResult, ApiStatus, ApiError } from '../types';

export function usePrediction() {
  const { selectedUserId } = useSelectedUser();
  const [data, setData] = useState<PredictionEngineResult | null>(null);
  const [status, setStatus] = useState<ApiStatus>('idle');
  const [error, setError] = useState<ApiError | null>(null);

  const fetch = useCallback(async () => {
    setStatus('loading');
    setError(null);
    try {
      const prediction = await usersApi.getPrediction(selectedUserId);
      setData(prediction);
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
