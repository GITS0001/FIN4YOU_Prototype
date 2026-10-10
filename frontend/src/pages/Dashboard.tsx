import React from 'react';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  PiggyBank,
  AlertTriangle,
  CheckCircle,
  Activity,
} from 'lucide-react';
import { useFinancialProfile } from '../hooks/useFinancialProfile';
import { useFinancialState } from '../hooks/useFinancialState';
import { usePrediction } from '../hooks/usePrediction';
import { KpiCard } from '../components/dashboard/KpiCard';
import { SpendingChart } from '../components/dashboard/SpendingChart';
import { ErrorState } from '../components/shared/ErrorState';
import { formatCurrency, formatPercent } from '../utils/format';
import { useSelectedUser } from '../context/UserContext';
import { StatementUpload } from '../components/dashboard/StatementUpload';
import { RecentTransactions } from '../components/dashboard/RecentTransactions';

export const Dashboard: React.FC = () => {
  const { selectedUserId } = useSelectedUser();
  const selectedUser = { id: selectedUserId, label: 'Aditya', currency: 'INR' };
  const { data: profile, status: profileStatus, error: profileError, refetch: refetchProfile } = useFinancialProfile();
  const { data: state, status: stateStatus, error: stateError, refetch: refetchState } = useFinancialState();
  const { data: prediction, status: predStatus, refetch: refetchPred } = usePrediction();

  const isLoading = profileStatus === 'loading' || stateStatus === 'loading' || predStatus === 'loading';
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

  const currency = profile?.home_currency || 'EUR';
  const gap = prediction?.gap_detection;
  const pcf = prediction?.projected_cash_flow;

  const needsAttention = !isLoading && state && ((state.expense_ratio || 0) > 0.8 || gap?.detected || (state.savings ?? 0) < 0);

  return (
    <div className="space-y-12 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-4xl font-semibold tracking-tight text-primary-dark mb-2">
            Good morning, <span className="bg-gradient-to-r from-primary-accent to-purple bg-clip-text text-transparent">{selectedUser.label.split(' ')[0]}</span>.
          </h1>
          <p className="text-muted text-base">Here's what your money looks like right now.</p>
        </div>
        <StatementUpload onUploadSuccess={handleRefresh} />
      </div>

      {/* Primary Financial State */}
      <section>
        <h2 className="text-lg font-semibold text-primary-dark mb-4">Current Position</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          <KpiCard
            label="Available Balance"
            value={isLoading ? '—' : formatCurrency(profile?.current_available_balance || 0, currency)}
            icon={DollarSign}
            iconColor="text-primary-accent"
          />
          <KpiCard
            label="Projected EOM Balance"
            value={isLoading ? '—' : (gap ? formatCurrency(gap.projected_balance, currency) : '—')}
            icon={TrendingUp}
            iconColor="text-primary-dark"
            trend={gap && gap.projected_balance >= gap.required_buffer ? 'up' : 'down'}
            trendLabel={isLoading ? undefined : (gap && gap.projected_balance !== undefined && gap.required_buffer !== undefined ? (gap.projected_balance >= gap.required_buffer ? 'Above Buffer' : 'Below Buffer') : undefined)}
          />
          <KpiCard
            label="Projected Cash Flow"
            value={isLoading ? '—' : (pcf ? formatCurrency(pcf.projected_cash_flow, currency) : '—')}
            icon={Activity}
            iconColor="text-primary-dark"
            trend={pcf && pcf.projected_cash_flow >= 0 ? 'up' : 'down'}
            trendLabel={pcf && pcf.projected_cash_flow >= 0 ? 'Positive' : 'Negative'}
          />
          <KpiCard
            label="Safety Buffer"
            value={isLoading ? '—' : (gap?.detected ? 'At Risk' : 'Maintained')}
            icon={gap?.detected ? AlertTriangle : CheckCircle}
            iconColor={gap?.detected ? 'text-warning' : 'text-positive'}
            subValue={isLoading ? undefined : `Min: ${formatCurrency(profile?.minimum_balance_to_keep || 0, currency)}`}
          />
        </div>
      </section>

    {/* Financial Overview */}
      <section>
        <h2 className="text-lg font-semibold text-primary-dark mb-4">Observed Behavior</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card p-6 flex flex-col justify-center gap-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-background shadow-sm border border-border p-4 rounded-xl">
                <p className="text-xs text-muted font-medium mb-1">Income</p>
                <p className="text-xl font-bold text-primary-dark">{isLoading ? '—' : formatCurrency(state?.income || 0, currency)}</p>
              </div>
              <div className="bg-background shadow-sm border border-border p-4 rounded-xl">
                <p className="text-xs text-muted font-medium mb-1">Expenses</p>
                <p className="text-xl font-bold text-danger">{isLoading ? '—' : formatCurrency(state?.expenses || 0, currency)}</p>
              </div>
              <div className="bg-background shadow-sm border border-border p-4 rounded-xl">
                <p className="text-xs text-muted font-medium mb-1">Net Savings</p>
                <p className="text-xl font-bold text-positive">{isLoading ? '—' : formatCurrency(state?.savings || 0, currency)}</p>
              </div>
              <div className="bg-background shadow-sm border border-border p-4 rounded-xl">
                <p className="text-xs text-muted font-medium mb-1">Savings Rate</p>
                <p className="text-xl font-bold text-primary-dark">{isLoading ? '—' : formatPercent(state?.savings_rate || 0)}</p>
              </div>
            </div>

            <div className="pt-6 border-t border-border">
               <div className="flex justify-between text-sm mb-2">
                 <span className="text-muted">Income vs Expenses</span>
               </div>
               <div className="w-full bg-border rounded-full h-2">
                 <div className={`h-2 rounded-full transition-all duration-500 ${
                   (state?.expense_ratio || 0) >= 1 ? 'bg-danger' :
                   (state?.expense_ratio || 0) > 0.8 ? 'bg-warning' : 'bg-primary-accent'
                 }`} style={{ width: `${Math.min(100, ((state?.expenses || 0) / (state?.income || 1)) * 100)}%` }}></div>
               </div>
            </div>
          </div>

          <SpendingChart
            categories={state?.category_spending || []}
            currency={currency}
            isLoading={isLoading}
            totalExpenses={state?.expenses || 0}
          />
        </div>
      </section>

      {/* Upcoming Obligations & Needs Attention */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-primary-dark mb-5">Upcoming Obligations</h2>
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex justify-between items-center py-3 border-b border-border last:border-0">
                  <div className="flex flex-col gap-2">
                    <div className="skeleton h-4 w-24 rounded"></div>
                    <div className="skeleton h-3 w-32 rounded"></div>
                  </div>
                  <div className="skeleton h-4 w-16 rounded"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {prediction?.obligations && prediction.obligations.length > 0 ? (
                prediction.obligations.slice(0, 5).map((obs, i) => (
                  <div key={i} className="flex justify-between items-center p-3 bg-background border border-border shadow-sm hover:border-muted rounded-xl cursor-pointer transition-all duration-200">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-primary-accent/10 flex items-center justify-center text-primary-accent shrink-0">
                        <DollarSign size={18} />
                      </div>
                      <div>
                        <p className="text-sm font-bold text-primary-dark capitalize">{obs.category.replace(/_/g, ' ')}</p>
                        <p className="text-xs text-muted truncate">{obs.description}</p>
                      </div>
                    </div>
                    <p className="text-sm font-bold text-primary-dark">{formatCurrency(obs.expected_amount, currency)}</p>
                  </div>
                ))
              ) : (
                <div className="flex flex-col items-center justify-center py-6 text-center">
                  <div className="w-12 h-12 bg-border/50 rounded-full flex items-center justify-center mb-3">
                    <PiggyBank size={24} className="text-muted" />
                  </div>
                  <p className="text-sm font-medium text-primary-dark">No upcoming obligations</p>
                  <p className="text-xs text-muted mb-3">You don't have any fixed bills detected.</p>
                  <button className="btn-secondary text-xs py-1.5">Add manually</button>
                </div>
              )}
            </div>
          )}
        </div>

        {needsAttention && (
          <div className="card p-6 border-l-4 border-l-warning bg-warning/5 relative overflow-hidden">
             <div className="flex items-center gap-2 mb-5">
               <AlertTriangle size={20} className="text-warning" />
               <h2 className="text-lg font-bold text-primary-dark">Needs Attention</h2>
             </div>

             <div className="flex flex-col gap-3">
                {(state.expense_ratio || 0) > 0.8 && (
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-card-bg shadow-sm border border-border p-4 rounded-xl">
                    <div>
                      <p className="text-sm font-bold text-primary-dark mb-1">High Expense Ratio</p>
                      <p className="text-xs text-muted">You are spending {formatPercent(state.expense_ratio!)} of your income.</p>
                    </div>
                    <button className="btn-primary bg-danger shrink-0 text-xs py-1.5 shadow-none hover:shadow-lg hover:shadow-danger/20">Review Budget</button>
                  </div>
                )}
                {gap?.detected && (
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-card-bg shadow-sm border border-border p-4 rounded-xl">
                    <div>
                      <p className="text-sm font-bold text-primary-dark mb-1">Cash Flow Pressure</p>
                      <p className="text-xs text-muted">Projected cash flow is below your minimum buffer.</p>
                    </div>
                    <button className="btn-secondary shrink-0 text-xs py-1.5 border-warning/30 text-warning-dark hover:bg-warning/10">Transfer Funds</button>
                  </div>
                )}
                {(state?.savings ?? 0) < 0 && (
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-card-bg shadow-sm border border-border p-4 rounded-xl">
                    <div>
                      <p className="text-sm font-bold text-primary-dark mb-1">Negative Net Savings</p>
                      <p className="text-xs text-muted">Observed expenses exceed your income.</p>
                    </div>
                    <button className="btn-secondary shrink-0 text-xs py-1.5 border-danger/30 text-danger-dark hover:bg-danger/10">Analyze</button>
                  </div>
                )}
              </div>
          </div>
        )}
      </section>

      {/* Recent Transactions */}
      <RecentTransactions />
    </div>
  );
};
