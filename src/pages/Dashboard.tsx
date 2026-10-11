import React from 'react';
import {
  IndianRupee,
  Activity,
  PiggyBank,
  ShieldCheck,
  AlertTriangle,
  ArrowUpRight,
  TrendingUp,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useFinancialProfile } from '../hooks/useFinancialProfile';
import { useFinancialState } from '../hooks/useFinancialState';
import { usePrediction } from '../hooks/usePrediction';
import { KpiCard } from '../components/dashboard/KpiCard';
import { SpendingChart } from '../components/dashboard/SpendingChart';
import { ErrorState } from '../components/shared/ErrorState';
import { getGreeting, formatCurrency, formatCurrencyCompact, formatPercent, getAccountUsername } from '../utils/format';
import { StatementUpload } from '../components/dashboard/StatementUpload';
import { RecentTransactions } from '../components/dashboard/RecentTransactions';
import { NinetyDayPlanCard } from '../components/dashboard/NinetyDayPlanCard';
import { useNavigate } from 'react-router-dom';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
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

  const currency = profile?.home_currency || 'INR';
  const username = getAccountUsername(user, profile);
  const gap = prediction?.gap_detection;
  const pcf = prediction?.projected_cash_flow;

  // Derive runway
  const essentialBurn = (state?.essential_expenses && state.essential_expenses > 0)
    ? state.essential_expenses
    : ((state?.expenses && state.expenses > 0) ? state.expenses * 0.7 : 20000);
  const runway = (profile?.current_available_balance && essentialBurn > 0)
    ? Number((profile.current_available_balance / essentialBurn).toFixed(1))
    : 0;

  const netCashFlow = state?.cash_flow ?? (pcf ? pcf.projected_cash_flow : ((state?.income || 0) - (state?.expenses || 0)));
  const needsAttention = !isLoading && state && ((state.expense_ratio || 0) > 0.8 || gap?.detected || (state.savings ?? 0) < 0);

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-8">
      {/* Executive Clean Header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 pt-1">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="w-2 h-2 rounded-full bg-positive animate-pulse" />
            <span className="text-2xs font-semibold uppercase tracking-wider text-muted">
              Live Financial Overview · Active Ledger
            </span>
          </div>
          <h1 className="font-display text-3xl sm:text-4xl font-bold tracking-tight text-primary-dark">
            {getGreeting()}, <span className="bg-gradient-to-r from-primary-accent to-purple bg-clip-text text-transparent">{username}</span>.
          </h1>
          <p className="text-muted text-xs sm:text-sm mt-1">
            Real-time financial status, spending distribution, and 90-day strategy.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <StatementUpload onUploadSuccess={handleRefresh} />
        </div>
      </div>

      {/* Primary KPI Row - 4 Clear Institutional Cards */}
      <section aria-label="Key Financial Indicators">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
          <KpiCard
            label="Available Balance"
            value={isLoading ? '—' : formatCurrencyCompact(profile?.current_available_balance || 0, currency)}
            icon={IndianRupee}
            iconColor="text-primary-accent"
            subValue={isLoading ? undefined : `Buffer Floor: ${formatCurrencyCompact(profile?.minimum_balance_to_keep || 0, currency)}`}
          />

          <KpiCard
            label="Monthly Cash Flow"
            value={isLoading ? '—' : formatCurrencyCompact(netCashFlow, currency)}
            icon={Activity}
            iconColor="text-primary-dark"
            trend={netCashFlow >= 0 ? 'up' : 'down'}
            trendLabel={netCashFlow >= 0 ? 'Net Surplus' : 'Cash Deficit'}
          />

          <KpiCard
            label="Savings Rate"
            value={isLoading ? '—' : formatPercent(state?.savings_rate || 0)}
            icon={PiggyBank}
            iconColor="text-positive"
            trend={(state?.savings_rate || 0) >= 0.2 ? 'up' : 'neutral'}
            trendLabel={isLoading ? undefined : `Saved: ${formatCurrencyCompact(state?.savings || 0, currency)}`}
          />

          <KpiCard
            label="Liquidity Runway"
            value={isLoading ? '—' : `${runway} Months`}
            icon={ShieldCheck}
            iconColor="text-primary-accent"
            trend={runway >= 3.0 ? 'up' : 'down'}
            trendLabel={runway >= 3.0 ? 'Protected' : 'Fortify Reserve'}
          />
        </div>
      </section>

      {/* Featured 90-Day Strategy Playbook */}
      <section aria-label="90-Day Financial Strategy">
        <NinetyDayPlanCard currency={currency} />
      </section>

      {/* Two-Column Analytics Section: Spending Distribution & Obligations */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Spending Breakdown & Income vs Outflows (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <SpendingChart
            categories={state?.category_spending || []}
            currency={currency}
            isLoading={isLoading}
            totalExpenses={state?.expenses || 0}
          />

          {/* Cash Flow Summary Card */}
          <div className="card p-5 border border-border/80 bg-card-bg shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-muted">Income vs Outflow Efficiency</span>
              <span className="text-xs font-semibold text-primary-dark">
                {((state?.expense_ratio || 0) * 100).toFixed(1)}% Spent
              </span>
            </div>
            <div className="w-full bg-surface-2 rounded-full h-2.5 overflow-hidden border border-border/50 mb-4">
              <div
                className={`h-full rounded-full transition-all duration-700 ${
                  (state?.expense_ratio || 0) >= 1
                    ? 'bg-danger'
                    : (state?.expense_ratio || 0) > 0.8
                    ? 'bg-warning'
                    : 'bg-gradient-to-r from-primary-accent to-purple'
                }`}
                style={{ width: `${Math.min(100, ((state?.expenses || 0) / Math.max(1, state?.income || 1)) * 100)}%` }}
              />
            </div>
            <div className="grid grid-cols-3 gap-3 pt-2 text-center border-t border-border/60">
              <div className="p-2 rounded-lg bg-surface-2/40">
                <p className="text-[10px] text-muted uppercase font-bold">Total Inflow</p>
                <p className="text-sm font-bold text-primary-dark">{isLoading ? '—' : formatCurrencyCompact(state?.income || 0, currency)}</p>
              </div>
              <div className="p-2 rounded-lg bg-surface-2/40">
                <p className="text-[10px] text-muted uppercase font-bold">Total Expenses</p>
                <p className="text-sm font-bold text-danger">{isLoading ? '—' : formatCurrencyCompact(state?.expenses || 0, currency)}</p>
              </div>
              <div className="p-2 rounded-lg bg-surface-2/40">
                <p className="text-[10px] text-muted uppercase font-bold">Net Saved</p>
                <p className="text-sm font-bold text-positive">{isLoading ? '—' : formatCurrencyCompact(state?.savings || 0, currency)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Upcoming Obligations & Action Alerts (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Upcoming Obligations Card */}
          <div className="card p-5 border border-border/80 bg-card-bg shadow-sm">
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-border/70">
              <h3 className="text-sm font-bold text-primary-dark tracking-tight">Scheduled Obligations</h3>
              <span className="text-2xs text-muted font-medium bg-surface-2 px-2 py-0.5 rounded-md">Fixed Bills</span>
            </div>

            {isLoading ? (
              <div className="space-y-2.5">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-10 bg-surface-2/70 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : prediction?.obligations && prediction.obligations.length > 0 ? (
              <div className="space-y-2.5">
                {prediction.obligations.slice(0, 4).map((obs, i) => (
                  <div
                    key={i}
                    className="flex justify-between items-center p-2.5 bg-surface-2/30 border border-border/70 rounded-xl hover:border-primary-accent/40 transition-colors"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="w-7 h-7 rounded-lg bg-primary-accent/10 flex items-center justify-center text-primary-accent flex-shrink-0">
                        <IndianRupee size={13} />
                      </div>
                      <div className="truncate">
                        <p className="text-xs font-bold text-primary-dark capitalize truncate">
                          {obs.category.replace(/_/g, ' ')}
                        </p>
                        <p className="text-[10px] text-muted truncate">{obs.description}</p>
                      </div>
                    </div>
                    <span className="text-xs font-bold text-primary-dark flex-shrink-0 ml-2">
                      {formatCurrency(obs.expected_amount, currency)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <p className="text-xs text-muted">No scheduled obligations detected in this statement.</p>
              </div>
            )}
          </div>

          {/* Attention Alerts / Recommendations (Only when applicable, clean styling) */}
          {needsAttention ? (
            <div className="card p-5 border border-warning/40 bg-warning/5 rounded-2xl space-y-3">
              <div className="flex items-center gap-2">
                <AlertTriangle size={16} className="text-warning flex-shrink-0" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-primary-dark">Financial Attention Items</h3>
              </div>

              {(state?.expense_ratio || 0) > 0.8 && (
                <div className="bg-card-bg border border-border/70 p-3 rounded-xl flex items-center justify-between gap-3 text-xs">
                  <div>
                    <p className="font-bold text-primary-dark">Elevated Expense Ratio</p>
                    <p className="text-muted text-[11px]">Spending {formatPercent(state?.expense_ratio || 0)} of monthly earnings.</p>
                  </div>
                  <button
                    onClick={() => navigate('/what-if')}
                    className="btn-secondary text-2xs py-1 px-2.5 border-warning/40 text-warning-dark hover:bg-warning/10"
                  >
                    Simulate
                  </button>
                </div>
              )}

              {gap?.detected && (
                <div className="bg-card-bg border border-border/70 p-3 rounded-xl flex items-center justify-between gap-3 text-xs">
                  <div>
                    <p className="font-bold text-primary-dark">Buffer Pressure</p>
                    <p className="text-muted text-[11px]">Projected cash flow reaches near safety threshold.</p>
                  </div>
                  <button
                    onClick={() => navigate('/affordability')}
                    className="btn-secondary text-2xs py-1 px-2.5 text-primary-dark"
                  >
                    Check
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="card p-5 border border-border/80 bg-gradient-to-br from-positive/5 via-card-bg to-card-bg rounded-2xl flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-positive">Cash Flow Maintained</p>
                <p className="text-2xs text-muted mt-0.5">Your safety buffer and monthly savings are on track.</p>
              </div>
              <button
                onClick={() => navigate('/copilot')}
                className="btn-ghost flex items-center gap-1 text-xs text-primary-accent hover:text-primary-accent font-semibold"
              >
                <span>Insights</span>
                <ArrowUpRight size={14} />
              </button>
            </div>
          )}
        </div>
      </section>

      {/* Recent Ledger Activity */}
      <section aria-label="Recent Transactions">
        <RecentTransactions />
      </section>
    </div>
  );
};
