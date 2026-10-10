import { useState, useEffect, useCallback } from 'react';
import { healthApi } from '../api/health';

export type BackendStatus = 'checking' | 'online' | 'offline';

export function useBackendStatus() {
  const [status, setStatus] = useState<BackendStatus>('checking');

  const check = useCallback(async () => {
    try {
      await healthApi.check();
      setStatus('online');
    } catch {
      setStatus('offline');
    }
  }, []);

  useEffect(() => {
    check();
    // Poll every 30 seconds
    const interval = setInterval(check, 30000);
    return () => clearInterval(interval);
  }, [check]);

  return { status, recheck: check };
}
