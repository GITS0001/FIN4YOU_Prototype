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
      <div className="card p-6">
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

  // Calculate composite health score (0-100)
  const savingsScore = Math.min(30, (state.savings_rate / 0.2) * 30);
  const expenseScore = Math.min(30, Math.max(0, (1 - state.expense_ratio / 1) * 30));
  const bufferScore = profile.current_available_balance >= profile.minimum_balance_to_keep ? 40 : 15;
  const totalScore = Math.round(savingsScore + expenseScore + bufferScore);

  const metrics: HealthMetric[] = [
    {
      label: 'Savings Rate',
      value: formatPercent(state.savings_rate),
      percent: clamp(state.savings_rate, 0, 1) * 100,
      statusClass: state.savings_rate >= 0.2 ? 'bg-emerald-500' : state.savings_rate >= 0.1 ? 'bg-amber-500' : 'bg-rose-500',
      description: state.savings_rate >= 0.2 ? 'Healthy' : state.savings_rate >= 0.1 ? 'Moderate' : 'Low',
    },
    {
      label: 'Expense Ratio',
      value: formatPercent(state.expense_ratio),
      percent: clamp(state.expense_ratio, 0, 1) * 100,
      statusClass: state.expense_ratio <= 0.7 ? 'bg-emerald-500' : state.expense_ratio <= 0.85 ? 'bg-amber-500' : 'bg-rose-500',
      description: state.expense_ratio <= 0.7 ? 'Under control' : state.expense_ratio <= 0.85 ? 'Monitor closely' : 'High',
    },
    {
      label: 'EMI Burden',
      value: formatCurrency(state.emi_burden, currency),
      percent: state.income > 0 ? clamp(state.emi_burden / state.income, 0, 1) * 100 : 0,
      statusClass: state.income > 0 && state.emi_burden / state.income <= 0.3 ? 'bg-emerald-500' : 'bg-amber-500',
      description: state.income > 0 ? `${formatPercent(state.emi_burden / state.income)} of income` : 'N/A',
    },
    {
      label: 'Min. Buffer Security',
      value: formatCurrency(profile.minimum_balance_to_keep, currency),
      percent: clamp(
        (profile.current_available_balance / Math.max(profile.minimum_balance_to_keep, 1)) * 100,
        0,
        100
      ),
      statusClass:
        profile.current_available_balance >= profile.minimum_balance_to_keep * 2
          ? 'bg-emerald-500'
          : profile.current_available_balance >= profile.minimum_balance_to_keep
          ? 'bg-amber-500'
          : 'bg-rose-500',
      description:
        profile.current_available_balance >= profile.minimum_balance_to_keep
          ? 'Buffer maintained'
          : 'Below buffer',
    },
  ];

  return (
    <section className="card p-6 animate-fade-in flex flex-col justify-between" aria-labelledby="financial-health-title">
      <div>
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 id="financial-health-title" className="section-title">Financial Health Index</h2>
            <p className="text-2xs text-muted mt-0.5">Real-time solvency &amp; buffer safety</p>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1 badge-positive">
            <span className="w-2 h-2 rounded-full bg-positive animate-pulse" />
            <span className="text-xs font-medium text-positive">{totalScore} / 100</span>
          </div>
        </div>

        <div className="space-y-4">
          {metrics.map((metric) => (
            <div key={metric.label}>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-medium text-primary-dark">{metric.label}</span>
                <div className="flex items-center gap-2">
                  <span className="text-2xs text-muted font-medium">{metric.description}</span>
                  <span className="text-xs font-medium text-primary-dark">{metric.value}</span>
                </div>
              </div>
              <div className="w-full bg-border rounded-full h-1.5 overflow-hidden" role="progressbar" aria-valuenow={metric.percent} aria-valuemin={0} aria-valuemax={100} aria-label={metric.label}>
                <div
                  className={`h-full rounded-full transition-all duration-500 ${metric.statusClass}`}
                  style={{ width: `${Math.min(metric.percent, 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
