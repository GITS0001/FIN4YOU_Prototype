import { useCallback } from 'react';
import { useGlobalState } from '../context/GlobalStateContext';
import { usersApi } from '../api/users';
import type { FinancialProfile } from '../types';

export function useFinancialProfile() {
  const { globalState, status, error, refetch, setOverrides, overrides } = useGlobalState();

  const update = useCallback(async (updatedProfile: FinancialProfile) => {
    // If they change available balance or buffer, we can set overrides
    // Alternatively, update backend in-memory profile
    const profile = await usersApi.updateProfile(updatedProfile.user_id, updatedProfile);
    refetch(); // Trigger global state refresh
    return profile;
  }, [refetch]);

  return { 
    data: globalState?.baseline || null, 
    status, 
    error, 
    refetch, 
    update 
  };
}
