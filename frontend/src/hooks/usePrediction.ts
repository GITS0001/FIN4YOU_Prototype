import { useGlobalState } from '../context/GlobalStateContext';

export function usePrediction() {
  const { globalState, status, error, refetch } = useGlobalState();
  return { data: globalState?.prediction || null, status, error, refetch };
}
