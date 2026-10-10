import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { usersApi } from '../api/users';
import { useSelectedUser } from './UserContext';
import type { GlobalFinancialState, FinancialOverrides, ApiStatus, ApiError } from '../types';

interface GlobalStateContextValue {
  globalState: GlobalFinancialState | null;
  overrides: FinancialOverrides;
  setOverrides: (overrides: FinancialOverrides) => void;
  status: ApiStatus;
  error: ApiError | null;
  refetch: () => void;
}

const GlobalStateContext = createContext<GlobalStateContextValue | undefined>(undefined);

export const GlobalStateProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { selectedUserId } = useSelectedUser();
  const [globalState, setGlobalState] = useState<GlobalFinancialState | null>(null);
  const [overrides, setOverrides] = useState<FinancialOverrides>({});
  const [status, setStatus] = useState<ApiStatus>('idle');
  const [error, setError] = useState<ApiError | null>(null);

  const fetchGlobalState = useCallback(async () => {
    if (!selectedUserId) return;
    setStatus('loading');
    setError(null);
    try {
      const state = await usersApi.getGlobalState(selectedUserId, overrides);
      setGlobalState(state);
      setStatus('success');
    } catch (err) {
      setError(err as ApiError);
      setStatus('error');
    }
  }, [selectedUserId, overrides]);

  useEffect(() => {
    fetchGlobalState();
  }, [fetchGlobalState]);

  // When selected user changes, clear overrides
  useEffect(() => {
    setOverrides({});
  }, [selectedUserId]);

  const value = {
    globalState,
    overrides,
    setOverrides,
    status,
    error,
    refetch: fetchGlobalState
  };

  return (
    <GlobalStateContext.Provider value={value}>
      {children}
    </GlobalStateContext.Provider>
  );
};

export const useGlobalState = () => {
  const context = useContext(GlobalStateContext);
  if (context === undefined) {
    throw new Error('useGlobalState must be used within a GlobalStateProvider');
  }
  return context;
};
