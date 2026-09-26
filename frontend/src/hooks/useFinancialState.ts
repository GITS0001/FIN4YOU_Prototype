import { useGlobalState } from '../context/GlobalStateContext';

export function useFinancialState() {
  const { globalState, status, error, refetch } = useGlobalState();
  return { data: globalState?.current_state || null, status, error, refetch };
}
