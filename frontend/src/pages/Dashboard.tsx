import React from 'react';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  PiggyBank,
  Activity,
  ArrowUpRight,
} from 'lucide-react';
import { useFinancialProfile } from '../hooks/useFinancialProfile';
import { useFinancialState } from '../hooks/useFinancialState';
import { usePrediction } from '../hooks/usePrediction';
import { KpiCard } from '../components/dashboard/KpiCard';
import { FinancialHealthCard } from '../components/dashboard/FinancialHealthCard';
import { SpendingChart } from '../components/dashboard/SpendingChart';
import { InsightCard } from '../components/dashboard/InsightCard';
import { ErrorState } from '../components/shared/ErrorState';
import { formatCurrency, formatPercent, getGreeting } from '../utils/format';
import { useNavigate } from 'react-router-dom';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { data: profile, status: profileStatus, error: profileError, refetch: refetchProfile } = useFinancialProfile();
  const { data: state, status: stateStatus, error: stateError, refetch: refetchState } = useFinancialState();
  const { data: prediction, status: predStatus, refetch: refetchPred } = usePrediction();

  const isLoading = profileStatus === 'loading' || stateStatus === 'loading';
  const hasError = profileStatus === 'error' || stateStatus === 'error';
  const error = profileError || stateError;

  const handleRefresh = () => {
    refetchProfile();
    refetchState();
    refetchPred();
  };

  if (hasError) {
    return (
      <ErrorState
        type={error?.status === 0 ? 'connection' : 'data'}
        message={error?.message}
        onRetry={handleRefresh}
      />
    );
  }

  const currency = profile?.home_currency || 'USD';

  const kpiCards = [
    {
      label: 'Available Balance',
      value: isLoading ? '—' : formatCurrency(profile?.current_available_balance || 0, currency),
      icon: DollarSign,
      iconColor: 'text-primary-accent bg-blue-50',
      trend: (profile?.current_available_balance || 0) >= (profile?.minimum_balance_to_keep || 0) ? 'up' as const : 'down' as const,
      trendLabel: isLoading ? undefined : profile ? `Buffer: ${formatCurrency(profile.minimum_balance_to_keep, currency)}` : undefined,
    },
    {
      label: 'Income',
      value: isLoading ? '—' : formatCurrency(state?.income || 0, currency),
      icon: TrendingUp,
      iconColor: 'text-positive bg-green-50',
      subValue: 'Total recorded',
    },
    {
      label: 'Expenses',
      value: isLoading ? '—' : formatCurrency(state?.expenses || 0, currency),
      icon: TrendingDown,
      iconColor: 'text-danger bg-red-50',
      subValue: 'Total recorded',
    },
    {
      label: 'Savings',
      value: isLoading ? '—' : formatCurrency(state?.savings || 0, currency),
      icon: PiggyBank,
      iconColor: 'text-positive bg-green-50',
      trend: (state?.savings || 0) >= 0 ? 'up' as const : 'down' as const,
      trendLabel: isLoading ? undefined : state ? `Rate: ${formatPercent(state.savings_rate)}` : undefined,
    },
    {
      label: 'Cash Flow',
      value: isLoading ? '—' : formatCurrency(state?.cash_flow || 0, currency),
      icon: Activity,
      iconColor: (state?.cash_flow || 0) >= 0 ? 'text-positive bg-green-50' : 'text-danger bg-red-50',
      trend: (state?.cash_flow || 0) >= 0 ? 'up' as const : 'down' as const,
      trendLabel: isLoading ? undefined : (state?.cash_flow || 0) >= 0 ? 'Positive' : 'Negative',
    },
    {
      label: 'Expense Ratio',
      value: isLoading ? '—' : formatPercent(state?.expense_ratio || 0),
      icon: ArrowUpRight,
      iconColor: (state?.expense_ratio || 0) <= 0.8 ? 'text-warning bg-amber-50' : 'text-danger bg-red-50',
      subValue: 'of income spent',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Greeting header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-primary-dark">
            {getGreeting()}, Yash
          </h1>
          <p className="text-muted text-sm mt-0.5">Here's your financial picture today.</p>
        </div>
        <button
          className="btn-primary flex items-center gap-2 text-sm"
          onClick={() => navigate('/copilot')}
        >
          <Activity size={15} aria-hidden="true" />
          Ask AI Copilot
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        {kpiCards.map((card) => (
          <KpiCard
            key={card.label}
            label={card.label}
            value={card.value}
            icon={card.icon}
            iconColor={card.iconColor}
            trend={card.trend}
            trendLabel={card.trendLabel}
            subValue={'subValue' in card ? card.subValue : undefined}
            isLoading={isLoading}
          />
        ))}
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Financial Health + Insights (left 2/3) */}
        <div className="lg:col-span-2 space-y-5">
          <FinancialHealthCard
            state={state}
            profile={profile}
            isLoading={isLoading}
          />

          <SpendingChart
            categories={state?.category_spending || []}
            currency={currency}
            isLoading={isLoading}
            totalExpenses={state?.expenses || 0}
          />
        </div>

        {/* Insights (right 1/3) */}
        <div>
          <InsightCard
            state={state}
            prediction={prediction}
            profile={profile}
            isLoading={isLoading || predStatus === 'loading'}
          />
        </div>
      </div>

      {/* Forecast teaser */}
      {prediction?.projected_cash_flow && (
        <div
          className="card p-5 border-l-4 border-l-primary-accent cursor-pointer hover:shadow-card-hover transition-shadow"
          onClick={() => navigate('/forecast')}
          role="link"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && navigate('/forecast')}
          aria-label="View financial forecast"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="label-sm mb-1">Next Month Forecast</p>
              <div className="flex items-center gap-4">
                <div>
                  <p className="text-xs text-muted">Projected Income</p>
                  <p className="text-base font-semibold text-positive">
                    {formatCurrency(prediction.projected_cash_flow.projected_income, currency)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted">Projected Expenses</p>
                  <p className="text-base font-semibold text-danger">
                    {formatCurrency(prediction.projected_cash_flow.projected_expenses + prediction.projected_cash_flow.known_obligations, currency)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-muted">Net Cash Flow</p>
                  <p className={`text-base font-semibold ${prediction.projected_cash_flow.projected_cash_flow >= 0 ? 'text-positive' : 'text-danger'}`}>
                    {formatCurrency(prediction.projected_cash_flow.projected_cash_flow, currency)}
                  </p>
                </div>
              </div>
            </div>
            <ArrowUpRight size={18} className="text-muted" aria-hidden="true" />
          </div>
        </div>
      )}
    </div>
  );
};
