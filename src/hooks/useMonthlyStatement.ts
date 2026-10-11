import { useQuery } from 'react-query';
import { apiClient } from '../api/client';

export interface MonthlyValueChange {
  current: number;
  previous: number;
  change: number;
}

export interface CategoryChange {
  category: string;
  current: number;
  previous: number;
  change: number;
}

export interface RecurringObligationItem {
  description: string;
  amount: number;
}

export interface MonthlyStatementResponse {
  month: string;
  income: MonthlyValueChange;
  expenses: MonthlyValueChange;
  savings: MonthlyValueChange;
  cash_flow: MonthlyValueChange;
  category_changes: CategoryChange[];
  recurring_obligations: RecurringObligationItem[];
  anomalies: any[];
  forecast: any;
  observations: string[];
  recommendations: string[];
}

export const useMonthlyStatement = () => {
  return useQuery<MonthlyStatementResponse, Error>('monthlyStatement', async () => {
    const response = await apiClient.get('/api/users/monthly-statement');
    return response.data;
  }, {
    retry: false
  });
};
