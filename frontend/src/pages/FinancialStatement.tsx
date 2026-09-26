import React from 'react';
import {
  FileText,
  TrendingUp,
  TrendingDown,
  PiggyBank,
  Activity,
  AlertTriangle,
  Shield,
  Tag,
  Calendar,
} from 'lucide-react';
import { useFinancialProfile } from '../hooks/useFinancialProfile';
import { useFinancialState } from '../hooks/useFinancialState';
import { usePrediction } from '../hooks/usePrediction';
import { formatCurrency, formatPercent } from '../utils/format';
import { LoadingSkeleton } from '../components/shared/LoadingSkeleton';
import { ErrorState } from '../components/shared/ErrorState';

function formatCategory(s: string) {
  return s.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

export const FinancialStatement: React.FC = () => {
  const { data: profile, status: profileStatus, error: profileError, refetch: refetchProfile } = useFinancialProfile();
  const { data: state, status: stateStatus, error: stateError, refetch: refetchState } = useFinancialState();
  const { data: prediction } = usePrediction();

  const isLoading = profileStatus === 'loading' || stateStatus === 'loading';
  const hasError = profileStatus === 'error' || stateStatus === 'error';
  const error = profileError || stateError;

  if (hasError) {
    return (
      <ErrorState
        type={error?.status === 0 ? 'connection' : 'data'}
        message={error?.message}
        onRetry={() => { refetchProfile(); refetchState(); }}
      />
    );
  }

  const currency = profile?.home_currency || 'EUR';
  const anomalies = state?.anomalies.filter(a => a.is_anomaly) || [];
  const topCategories = state?.category_spending
    .filter(c => c.total_amount > 0)
    .slice(0, 8) || [];

  // Calculate expense ratio status
  const expenseRatioStatus = (state?.expense_ratio || 0) > 1 ? 'Critical' :
    (state?.expense_ratio || 0) > 0.9 ? 'High' :
    (state?.expense_ratio || 0) > 0.7 ? 'Elevated' : 'Normal';

  const savingsRateStatus = (state?.savings_rate || 0) < 0 ? 'Critical' :
    (state?.savings_rate || 0) < 0.05 ? 'Low' :
    (state?.savings_rate || 0) < 0.15 ? 'Moderate' : 'Healthy';

  const emiRatioStatus = (prediction?.projected_cash_flow && (state?.emi_burden || 0) > 0)
    ? (state?.emi_burden || 0) / Math.max(1, state?.income || 1) > 0.5 ? 'High' :
      (state?.emi_burden || 0) / Math.max(1, state?.income || 1) > 0.3 ? 'Elevated' : 'Manageable'
    : 'N/A';

  const statusColor = (s: string) => {
    if (s === 'Critical') return 'text-danger';
    if (s === 'High' || s === 'Elevated' || s === 'Low') return 'text-warning';
    if (s === 'Healthy' || s === 'Normal' || s === 'Manageable') return 'text-positive';
    return 'text-muted';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <FileText size={20} className="text-primary-accent" />
          <h1 className="text-2xl font-bold text-primary-dark">Financial Statement</h1>
        </div>
        <p className="text-muted text-sm">
          Complete financial picture based on observed transaction history · {profile?.user_id || '—'} · {currency}
        </p>
      </div>

      {/* Summary Row */}
      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1,2,3,4].map(i => <LoadingSkeleton key={i} height="h-24" />)}
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="card p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp size={14} className="text-positive" />
              <p className="label-sm">Total Income</p>
            </div>
            <p className="text-xl font-bold text-positive">{formatCurrency(state?.income || 0, currency)}</p>
            <p className="text-xs text-muted mt-1">Observed period total</p>
          </div>
          <div className="card p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingDown size={14} className="text-danger" />
              <p className="label-sm">Total Expenses</p>
            </div>
            <p className="text-xl font-bold text-danger">{formatCurrency(state?.expenses || 0, currency)}</p>
            <p className="text-xs text-muted mt-1">Observed period total</p>
          </div>
          <div className="card p-4">
            <div className="flex items-center gap-2 mb-2">
              <PiggyBank size={14} className={`${(state?.savings || 0) >= 0 ? 'text-positive' : 'text-danger'}`} />
              <p className="label-sm">Net Savings</p>
            </div>
            <p className={`text-xl font-bold ${(state?.savings || 0) >= 0 ? 'text-positive' : 'text-danger'}`}>
              {formatCurrency(state?.savings || 0, currency)}
            </p>
            <p className="text-xs text-muted mt-1">Rate: {formatPercent(state?.savings_rate || 0)}</p>
          </div>
          <div className="card p-4">
            <div className="flex items-center gap-2 mb-2">
              <Activity size={14} className={`${(state?.cash_flow || 0) >= 0 ? 'text-positive' : 'text-danger'}`} />
              <p className="label-sm">Net Cash Flow</p>
            </div>
            <p className={`text-xl font-bold ${(state?.cash_flow || 0) >= 0 ? 'text-positive' : 'text-danger'}`}>
              {formatCurrency(state?.cash_flow || 0, currency)}
            </p>
            <p className="text-xs text-muted mt-1">Income minus expenses</p>
          </div>
        </div>
      )}

      {/* Financial Health Indicators */}
      <section className="card p-5" aria-labelledby="health-indicators-title">
        <h2 id="health-indicators-title" className="section-title mb-4">Financial Health Indicators</h2>
        {isLoading ? (
          <div className="space-y-3">{[1,2,3,4].map(i => <LoadingSkeleton key={i} height="h-12" />)}</div>
        ) : (
          <div className="divide-y divide-border">
            <div className="py-3 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-primary-dark">Savings Rate</p>
                <p className="text-xs text-muted">Percentage of income saved</p>
              </div>
              <div className="text-right">
                <p className="text-base font-bold text-primary-dark">{formatPercent(state?.savings_rate || 0)}</p>
                <p className={`text-xs font-medium ${statusColor(savingsRateStatus)}`}>{savingsRateStatus}</p>
              </div>
            </div>
            <div className="py-3 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-primary-dark">Expense Ratio</p>
                <p className="text-xs text-muted">Expenses as percentage of income</p>
              </div>
              <div className="text-right">
                <p className="text-base font-bold text-primary-dark">{formatPercent(state?.expense_ratio || 0)}</p>
                <p className={`text-xs font-medium ${statusColor(expenseRatioStatus)}`}>{expenseRatioStatus}</p>
              </div>
            </div>
            <div className="py-3 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-primary-dark">EMI / Debt Burden</p>
                <p className="text-xs text-muted">Recurring debt repayments</p>
              </div>
              <div className="text-right">
                <p className="text-base font-bold text-primary-dark">{formatCurrency(state?.emi_burden || 0, currency)}</p>
                <p className={`text-xs font-medium ${statusColor(emiRatioStatus)}`}>{emiRatioStatus}</p>
              </div>
            </div>
            <div className="py-3 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-primary-dark">Recurring Obligations</p>
                <p className="text-xs text-muted">Fixed subscriptions and debt payments</p>
              </div>
              <div className="text-right">
                <p className="text-base font-bold text-primary-dark">{formatCurrency(state?.recurring_obligations || 0, currency)}</p>
              </div>
            </div>
            <div className="py-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Shield size={14} className="text-primary-accent" />
                <div>
                  <p className="text-sm font-medium text-primary-dark">Minimum Balance Buffer</p>
                  <p className="text-xs text-muted">Required safety reserve</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-base font-bold text-primary-dark">{formatCurrency(profile?.minimum_balance_to_keep || 0, currency)}</p>
                <p className={`text-xs font-medium ${(profile?.current_available_balance || 0) >= (profile?.minimum_balance_to_keep || 0) ? 'text-positive' : 'text-danger'}`}>
                  {(profile?.current_available_balance || 0) >= (profile?.minimum_balance_to_keep || 0) ? 'Maintained' : 'Breached'}
                </p>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* Expense Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Expense Categories */}
        <section className="card p-5" aria-labelledby="expense-categories-title">
          <div className="flex items-center gap-2 mb-4">
            <Tag size={14} className="text-muted" />
            <h2 id="expense-categories-title" className="section-title">Expense Categories</h2>
          </div>
          {isLoading ? (
            <div className="space-y-2">{[1,2,3,4,5].map(i => <LoadingSkeleton key={i} height="h-8" />)}</div>
          ) : topCategories.length > 0 ? (
            <div className="space-y-3">
              {topCategories.map((cat) => (
                <div key={cat.category}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-slate-700">{formatCategory(cat.category)}</span>
                    <span className="font-bold text-primary-dark">{formatCurrency(cat.total_amount, currency)}</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2">
                    <div
                      className="bg-primary-accent/70 h-2 rounded-full"
                      style={{ width: `${Math.min(100, (cat.total_amount / (state?.expenses || 1)) * 100)}%` }}
                    />
                  </div>
                  <p className="text-xs text-muted mt-0.5">
                    {((cat.total_amount / (state?.expenses || 1)) * 100).toFixed(1)}% of total expenses
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted">No expense categories available.</p>
          )}
        </section>

        {/* Essential vs Discretionary */}
        <section className="card p-5" aria-labelledby="expense-type-title">
          <h2 id="expense-type-title" className="section-title mb-4">Essential vs Discretionary</h2>
          {isLoading ? (
            <div className="space-y-3">{[1,2,3].map(i => <LoadingSkeleton key={i} height="h-16" />)}</div>
          ) : (
            <div className="space-y-5">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-medium text-slate-700">Essential Expenses</span>
                  <span className="font-bold text-danger">{formatCurrency(state?.essential_expenses || 0, currency)}</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-3">
                  <div
                    className="bg-danger/70 h-3 rounded-full"
                    style={{ width: `${Math.min(100, ((state?.essential_expenses || 0) / (state?.expenses || 1)) * 100)}%` }}
                  />
                </div>
                <p className="text-xs text-muted mt-1">
                  {(((state?.essential_expenses || 0) / (state?.expenses || 1)) * 100).toFixed(1)}% of expenses · Fixed, necessary
                </p>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-medium text-slate-700">Discretionary Expenses</span>
                  <span className="font-bold text-warning">{formatCurrency(state?.discretionary_expenses || 0, currency)}</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-3">
                  <div
                    className="bg-warning/70 h-3 rounded-full"
                    style={{ width: `${Math.min(100, ((state?.discretionary_expenses || 0) / (state?.expenses || 1)) * 100)}%` }}
                  />
                </div>
                <p className="text-xs text-muted mt-1">
                  {(((state?.discretionary_expenses || 0) / (state?.expenses || 1)) * 100).toFixed(1)}% of expenses · Variable, reducible
                </p>
              </div>
              
              {/* Balance Position */}
              <div className="pt-4 border-t border-slate-100">
                <p className="text-sm font-semibold text-primary-dark mb-3">Balance Position</p>
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-slate-50 p-3 rounded-lg">
                    <p className="text-xs text-muted mb-0.5">Current Balance</p>
                    <p className="text-sm font-bold">{formatCurrency(profile?.current_available_balance || 0, currency)}</p>
                  </div>
                  <div className="bg-slate-50 p-3 rounded-lg">
                    <p className="text-xs text-muted mb-0.5">Safety Buffer</p>
                    <p className="text-sm font-bold">{formatCurrency(profile?.minimum_balance_to_keep || 0, currency)}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </section>
      </div>

      {/* Upcoming Obligations */}
      {prediction?.obligations && prediction.obligations.length > 0 && (
        <section className="card p-5" aria-labelledby="obligations-title">
          <div className="flex items-center gap-2 mb-4">
            <Calendar size={14} className="text-muted" />
            <h2 id="obligations-title" className="section-title">
              Upcoming Fixed Obligations
            </h2>
            <span className="badge-neutral">{prediction.obligations.length}</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full" aria-label="Upcoming obligations">
              <thead>
                <tr className="bg-background text-left">
                  <th className="px-4 py-2 text-xs font-semibold text-muted uppercase tracking-wide" scope="col">Description</th>
                  <th className="px-4 py-2 text-xs font-semibold text-muted uppercase tracking-wide" scope="col">Category</th>
                  <th className="px-4 py-2 text-xs font-semibold text-muted uppercase tracking-wide text-right" scope="col">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {prediction.obligations.map((ob, idx) => (
                  <tr key={idx} className="hover:bg-background transition-colors">
                    <td className="px-4 py-3 text-sm text-primary-dark">{ob.description}</td>
                    <td className="px-4 py-3">
                      <span className="badge-neutral text-xs">{formatCategory(ob.category)}</span>
                    </td>
                    <td className="px-4 py-3 text-right text-sm font-semibold text-danger">
                      {formatCurrency(ob.expected_amount, currency)}
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="bg-slate-50">
                  <td className="px-4 py-3 text-sm font-semibold text-primary-dark" colSpan={2}>Total Obligations</td>
                  <td className="px-4 py-3 text-right text-sm font-bold text-danger">
                    {formatCurrency(prediction.obligations.reduce((s, o) => s + o.expected_amount, 0), currency)}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </section>
      )}

      {/* Bottom Grid for Anomalies and Preferences */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Anomalies */}
      {anomalies.length > 0 && (
        <section className="card p-5" aria-labelledby="anomalies-title">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle size={14} className="text-warning" />
            <h2 id="anomalies-title" className="section-title">Unusual Transactions</h2>
            <span className="badge-warning text-xs">{anomalies.length}</span>
          </div>
          <p className="text-xs text-muted mb-4">
            Transactions that deviate significantly from your historical spending patterns (≥2 standard deviations).
            These are signals for review, not fraud accusations.
          </p>
          <div className="space-y-2">
            {anomalies.slice(0, 5).map((a, i) => (
              <div key={i} className="flex items-start gap-3 p-3 bg-amber-50 border border-amber-100 rounded-lg">
                <AlertTriangle size={14} className="text-warning mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-xs font-medium text-slate-700">Transaction ID: {a.transaction_id}</p>
                  <p className="text-xs text-muted">{a.reason}</p>
                </div>
                <span className="text-xs font-medium text-warning whitespace-nowrap">
                  Score: {a.anomaly_score.toFixed(2)}
                </span>
              </div>
            ))}
            {anomalies.length > 5 && (
              <p className="text-xs text-muted text-center pt-1">
                +{anomalies.length - 5} more unusual transactions detected
              </p>
            )}
          </div>
        </section>
      )}

      {/* User Preferences */}
      {profile && (
        <section className="card p-5" aria-labelledby="preferences-title">
          <h2 id="preferences-title" className="section-title mb-4">User Financial Preferences</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { label: 'Financial Priorities', items: profile.financial_priorities, color: 'text-primary-accent' },
              { label: 'Protected Categories', items: profile.expense_categories_to_protect, color: 'text-positive' },
              { label: 'Willing to Reduce', items: profile.expense_categories_user_is_willing_to_reduce, color: 'text-warning' },
              { label: 'Willing to Stop', items: profile.expense_categories_user_is_willing_to_stop, color: 'text-danger' },
            ].map(group => (
              <div key={group.label}>
                <p className="text-xs font-semibold text-muted uppercase tracking-wide mb-2">{group.label}</p>
                {group.items && group.items.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {group.items.map(item => (
                      <span
                        key={item}
                        className="px-2.5 py-1 text-xs bg-slate-100 border border-slate-200 rounded-full font-medium text-slate-700"
                      >
                        {formatCategory(item)}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-muted">None specified</p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
      </div>
    </div>
  );
};
