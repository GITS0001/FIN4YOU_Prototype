import React from 'react';
import type { FinancialState, FinancialProfile } from '../../types';
import { formatPercent, formatCurrency, clamp } from '../../utils/format';
import { LoadingSkeleton } from '../shared/LoadingSkeleton';

interface FinancialHealthCardProps {
  state: FinancialState | null;
  profile: FinancialProfile | null;
  isLoading: boolean;
}

interface HealthMetric {
  label: string;
  value: string;
  percent: number;
  statusClass: string;
  description: string;
}

export const FinancialHealthCard: React.FC<FinancialHealthCardProps> = ({
  state,
  profile,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div className="card p-5">
        <LoadingSkeleton className="mb-4" height="h-5" />
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i}>
              <div className="flex justify-between mb-1">
                <LoadingSkeleton height="h-3" className="w-24" />
                <LoadingSkeleton height="h-3" className="w-12" />
              </div>
              <div className="progress-bar">
                <div className="skeleton h-1.5 w-2/3 rounded-full" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!state || !profile) return null;

  const currency = profile.home_currency;

  const metrics: HealthMetric[] = [
    {
      label: 'Savings Rate',
      value: formatPercent(state.savings_rate),
      percent: clamp(state.savings_rate, 0, 1) * 100,
      statusClass: state.savings_rate >= 0.2 ? 'bg-positive' : state.savings_rate >= 0.1 ? 'bg-warning' : 'bg-danger',
      description: state.savings_rate >= 0.2 ? 'Healthy' : state.savings_rate >= 0.1 ? 'Moderate' : 'Low',
    },
    {
      label: 'Expense Ratio',
      value: formatPercent(state.expense_ratio),
      percent: clamp(state.expense_ratio, 0, 1) * 100,
      statusClass: state.expense_ratio <= 0.7 ? 'bg-positive' : state.expense_ratio <= 0.85 ? 'bg-warning' : 'bg-danger',
      description: state.expense_ratio <= 0.7 ? 'Under control' : state.expense_ratio <= 0.85 ? 'Monitor closely' : 'High',
    },
    {
      label: 'EMI Burden',
      value: formatCurrency(state.emi_burden, currency),
      percent: state.income > 0 ? clamp(state.emi_burden / state.income, 0, 1) * 100 : 0,
      statusClass: state.income > 0 && state.emi_burden / state.income <= 0.3 ? 'bg-positive' : 'bg-warning',
      description: state.income > 0 ? `${formatPercent(state.emi_burden / state.income)} of income` : 'N/A',
    },
    {
      label: 'Min. Balance',
      value: formatCurrency(profile.minimum_balance_to_keep, currency),
      percent: clamp(
        (profile.current_available_balance / Math.max(profile.minimum_balance_to_keep, 1)) * 100,
        0,
        100
      ),
      statusClass:
        profile.current_available_balance >= profile.minimum_balance_to_keep * 2
          ? 'bg-positive'
          : profile.current_available_balance >= profile.minimum_balance_to_keep
          ? 'bg-warning'
          : 'bg-danger',
      description:
        profile.current_available_balance >= profile.minimum_balance_to_keep
          ? 'Buffer maintained'
          : 'Below buffer',
    },
  ];

  return (
    <section className="card p-5 animate-fade-in" aria-labelledby="financial-health-title">
      <h2 id="financial-health-title" className="section-title mb-4">Financial Health</h2>
      <div className="space-y-4">
        {metrics.map((metric) => (
          <div key={metric.label}>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-sm text-primary-dark font-medium">{metric.label}</span>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted">{metric.description}</span>
                <span className="text-sm font-semibold text-primary-dark">{metric.value}</span>
              </div>
            </div>
            <div className="progress-bar" role="progressbar" aria-valuenow={metric.percent} aria-valuemin={0} aria-valuemax={100} aria-label={metric.label}>
              <div
                className={`progress-fill ${metric.statusClass}`}
                style={{ width: `${Math.min(metric.percent, 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
