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
import { useMonthlyStatement } from '../hooks/useMonthlyStatement';
import { useFinancialState } from '../hooks/useFinancialState';
import { formatCurrency, formatPercent } from '../utils/format';
import { LoadingSkeleton } from '../components/shared/LoadingSkeleton';
import { ErrorState } from '../components/shared/ErrorState';
import { PageHeader } from '../components/shared/PageHeader';

function formatCategory(s: string) {
  return s.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

export const FinancialStatement: React.FC = () => {
  const { data: profile, status: profileStatus, error: profileError, refetch: refetchProfile } = useFinancialProfile();
  const { data: statement, status: statementStatus, error: statementError, refetch: refetchStatement } = useMonthlyStatement();
  const { data: state, status: stateStatus, error: stateError, refetch: refetchState } = useFinancialState();

  const isLoading = profileStatus === 'loading' || statementStatus === 'loading' || stateStatus === 'loading';
  const hasError = profileStatus === 'error' || statementStatus === 'error' || stateStatus === 'error';
  const error: any = profileError || statementError || stateError;

  if (hasError) {
    return (
      <ErrorState
        type={error?.status === 0 ? 'connection' : 'data'}
        message={error?.message}
        onRetry={() => { refetchProfile(); refetchStatement(); refetchState(); }}
      />
    );
  }

  const currency = profile?.home_currency || 'EUR';
  const anomalies = statement?.anomalies || [];

  const statusColor = (s: string) => {
    if (s === 'Critical' || s === 'Low') return 'text-danger';
    if (s === 'High' || s === 'Elevated' || s === 'Warning') return 'text-warning';
    if (s === 'Healthy' || s === 'Normal' || s === 'Manageable') return 'text-positive';
    return 'text-muted';
  };

  const savingsRateStatus = (state?.savings_rate ?? 0) > 0.15 ? 'Healthy' : ((state?.savings_rate ?? 0) > 0 ? 'Warning' : 'Critical');
  const expenseRatioStatus = (state?.expense_ratio ?? 0) > 0.8 ? 'High' : ((state?.expense_ratio ?? 0) > 0.5 ? 'Normal' : 'Healthy');
  const emiRatioStatus = (state?.emi_burden ?? 0) > 0.4 ? 'Critical' : ((state?.emi_burden ?? 0) > 0.2 ? 'Warning' : 'Manageable');

  return (
    <div className="space-y-8">
      <PageHeader
        icon={FileText}
        eyebrow="Analyze"
        title={`Monthly Financial Statement: ${statement?.month || ''}`}
        subtitle={<>Month-over-month financial analysis · <span className="font-medium text-primary-dark">{profile?.user_id || '—'}</span> · {currency}</>}
        actions={<button className="btn-secondary btn-sm" onClick={() => window.print()}>Export</button>}
      />

      {/* Summary Row */}
      {isLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1,2,3,4].map(i => <LoadingSkeleton key={i} height="h-24" />)}
        </div>
      ) : statement ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="card p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <TrendingUp size={14} className="text-positive" />
                <p className="label-sm">Income</p>
              </div>
            </div>
            <p className="text-xl font-bold text-positive">{formatCurrency(statement.income.current, currency)}</p>
            <p className={`text-xs mt-1 ${statement.income.change >= 0 ? 'text-positive' : 'text-danger'}`}>
              {statement.income.change >= 0 ? '+' : ''}{formatCurrency(statement.income.change, currency)} vs prev
            </p>
          </div>
          <div className="card p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <TrendingDown size={14} className="text-danger" />
                <p className="label-sm">Expenses</p>
              </div>
            </div>
            <p className="text-xl font-bold text-danger">{formatCurrency(statement.expenses.current, currency)}</p>
            <p className={`text-xs mt-1 ${statement.expenses.change <= 0 ? 'text-positive' : 'text-danger'}`}>
              {statement.expenses.change >= 0 ? '+' : ''}{formatCurrency(statement.expenses.change, currency)} vs prev
            </p>
          </div>
          <div className="card p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <PiggyBank size={14} className={`${statement.savings.current >= 0 ? 'text-positive' : 'text-danger'}`} />
                <p className="label-sm">Savings</p>
              </div>
            </div>
            <p className={`text-xl font-bold ${statement.savings.current >= 0 ? 'text-positive' : 'text-danger'}`}>
              {formatCurrency(statement.savings.current, currency)}
            </p>
            <p className={`text-xs mt-1 ${statement.savings.change >= 0 ? 'text-positive' : 'text-danger'}`}>
              {statement.savings.change >= 0 ? '+' : ''}{formatCurrency(statement.savings.change, currency)} vs prev
            </p>
          </div>
          <div className="card p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Activity size={14} className={`${statement.cash_flow.current >= 0 ? 'text-positive' : 'text-danger'}`} />
                <p className="label-sm">Cash Flow</p>
              </div>
            </div>
            <p className={`text-xl font-bold ${statement.cash_flow.current >= 0 ? 'text-positive' : 'text-danger'}`}>
              {formatCurrency(statement.cash_flow.current, currency)}
            </p>
            <p className={`text-xs mt-1 ${statement.cash_flow.change >= 0 ? 'text-positive' : 'text-danger'}`}>
              {statement.cash_flow.change >= 0 ? '+' : ''}{formatCurrency(statement.cash_flow.change, currency)} vs prev
            </p>
          </div>
        </div>
      ) : null}

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
            <h2 id="expense-categories-title" className="section-title">Category Changes</h2>
          </div>
          {isLoading ? (
            <div className="space-y-2">{[1,2,3,4,5].map(i => <LoadingSkeleton key={i} height="h-8" />)}</div>
          ) : statement?.category_changes && statement.category_changes.length > 0 ? (
            <div className="space-y-3">
              {statement.category_changes.map((cat: any) => (
                <div key={cat.category}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-primary-dark">{formatCategory(cat.category)}</span>
                    <span className="font-bold text-primary-dark">{formatCurrency(cat.current, currency)}</span>
                  </div>
                  <p className={`text-xs ${cat.change > 0 ? 'text-danger' : 'text-positive'}`}>
                    {cat.change > 0 ? '+' : ''}{formatCurrency(cat.change, currency)} vs previous
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted">No category changes available.</p>
          )}
        </section>

        {/* Observations & Recommendations */}
        <section className="card p-5" aria-labelledby="insights-title">
          <h2 id="insights-title" className="section-title mb-4">Observations & Recommendations</h2>
          {isLoading ? (
            <div className="space-y-3">{[1,2].map(i => <LoadingSkeleton key={i} height="h-16" />)}</div>
          ) : (
            <div className="space-y-5">
              <div>
                <p className="text-sm font-semibold text-primary-dark mb-2">Observations</p>
                <ul className="list-disc pl-4 space-y-1">
                  {statement?.observations.map((obs: string, i: number) => (
                    <li key={i} className="text-sm text-muted">{obs}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-sm font-semibold text-primary-dark mb-2">Recommendations</p>
                <ul className="list-disc pl-4 space-y-1">
                  {statement?.recommendations.map((rec: string, i: number) => (
                    <li key={i} className="text-sm text-muted">{rec}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </section>
      </div>

      {/* Upcoming Obligations */}
      {statement?.recurring_obligations && statement.recurring_obligations.length > 0 && (
        <section className="card p-5" aria-labelledby="obligations-title">
          <div className="flex items-center gap-2 mb-4">
            <Calendar size={14} className="text-muted" />
            <h2 id="obligations-title" className="section-title">
              Recurring Obligations
            </h2>
            <span className="badge-neutral">{statement.recurring_obligations.length}</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full" aria-label="Upcoming obligations">
              <thead>
                <tr className="bg-background text-left">
                  <th className="px-4 py-2 text-xs font-semibold text-muted uppercase tracking-wide" scope="col">Description</th>
                  <th className="px-4 py-2 text-xs font-semibold text-muted uppercase tracking-wide text-right" scope="col">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {statement.recurring_obligations.map((ob: any, idx: number) => (
                  <tr key={idx} className="hover:bg-background transition-colors">
                    <td className="px-4 py-3 text-sm text-primary-dark">{ob.description}</td>
                    <td className="px-4 py-3 text-right text-sm font-semibold text-danger">
                      {formatCurrency(ob.amount, currency)}
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="bg-background font-medium">
                  <td className="px-4 py-3 text-sm font-semibold text-primary-dark">Total Obligations</td>
                  <td className="px-4 py-3 text-right text-sm font-bold text-danger">
                    {formatCurrency(statement.recurring_obligations.reduce((s: number, o: any) => s + o.amount, 0), currency)}
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
            {anomalies.slice(0, 5).map((a: any, i: number) => (
              <div key={i} className="flex items-start gap-3 p-3 bg-warning/10 border border-warning/20 rounded-lg">
                <AlertTriangle size={14} className="text-warning mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-xs font-medium text-primary-dark">Transaction ID: {a.transaction_id}</p>
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
                        className="px-2.5 py-1 text-xs bg-muted/10 border border-border rounded-full font-medium text-primary-dark"
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
