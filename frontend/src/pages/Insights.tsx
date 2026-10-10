import React from 'react';
import { useFinancialState } from '../hooks/useFinancialState';
import { useFinancialProfile } from '../hooks/useFinancialProfile';
import { SpendingChart } from '../components/dashboard/SpendingChart';
import { ErrorState } from '../components/shared/ErrorState';
import { LoadingSkeleton } from '../components/shared/LoadingSkeleton';
import { formatCurrency, formatCategory, formatPercent, getCategoryColor } from '../utils/format';
import { Activity, AlertTriangle } from 'lucide-react';

export const Insights: React.FC = () => {
  const { data: profile, status: profileStatus, refetch: refetchProfile } = useFinancialProfile();
  const { data: state, status: stateStatus, error, refetch: refetchState } = useFinancialState();

  const isLoading = profileStatus === 'loading' || stateStatus === 'loading';
  const hasError = stateStatus === 'error';

  const handleRefresh = () => {
    refetchProfile();
    refetchState();
  };

  if (hasError) {
    return <ErrorState type="data" message={error?.message} onRetry={handleRefresh} />;
  }

  const currency = profile?.home_currency || 'USD';
  const anomalies = state?.anomalies.filter((a) => a.is_anomaly) || [];
  const topCategories = state?.category_spending.filter((c) => c.total_amount > 0).slice(0, 10) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-primary-dark">Spending Insights</h1>
        <p className="text-muted text-sm mt-0.5">Understand where your money is going.</p>
      </div>

      {/* Spending Summary */}
      <div className="grid grid-cols-3 gap-4">
        {[
          {
            label: 'Total Expenses',
            value: isLoading ? null : state?.expenses,
            color: 'text-danger',
            icon: '↓',
          },
          {
            label: 'Essential',
            value: isLoading ? null : state?.essential_expenses,
            color: 'text-warning',
            icon: '🔒',
          },
          {
            label: 'Discretionary',
            value: isLoading ? null : state?.discretionary_expenses,
            color: 'text-primary-accent',
            icon: '✦',
          },
        ].map((item) => (
          <div key={item.label} className="card p-5">
            <p className="label-sm mb-2">{item.label}</p>
            {item.value === null || item.value === undefined ? (
              <LoadingSkeleton height="h-7" className="w-28" />
            ) : (
              <p className={`text-xl font-bold ${item.color}`}>
                {formatCurrency(item.value, currency)}
              </p>
            )}
          </div>
        ))}
      </div>

      {/* Spending Chart */}
      <SpendingChart
        categories={state?.category_spending || []}
        currency={currency}
        isLoading={isLoading}
        totalExpenses={state?.expenses || 0}
      />

      {/* Category breakdown table */}
      <section className="card overflow-hidden" aria-labelledby="category-breakdown-title">
        <div className="px-5 py-4 border-b border-border">
          <h2 id="category-breakdown-title" className="section-title">Category Breakdown</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full" aria-label="Category spending breakdown">
            <thead>
              <tr className="bg-background text-left">
                <th className="px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wide" scope="col">Category</th>
                <th className="px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wide text-right" scope="col">Amount</th>
                <th className="px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wide text-right" scope="col">% of Expenses</th>
                <th className="px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wide" scope="col">Share</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {isLoading ? (
                [1, 2, 3, 4, 5].map((i) => (
                  <tr key={i} className="animate-pulse">
                    {[1, 2, 3, 4].map((j) => (
                      <td key={j} className="px-5 py-3">
                        <div className="skeleton h-3 w-full rounded" />
                      </td>
                    ))}
                  </tr>
                ))
              ) : (
                topCategories.map((cat, idx) => {
                  const pct = state && state.expenses > 0
                    ? (cat.total_amount / state.expenses) * 100
                    : 0;
                  return (
                    <tr key={cat.category} className="hover:bg-background transition-colors">
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-2.5">
                          <div
                            className="w-2.5 h-2.5 rounded-sm flex-shrink-0"
                            style={{ backgroundColor: getCategoryColor(idx) }}
                            aria-hidden="true"
                          />
                          <span className="text-sm font-medium text-primary-dark">
                            {formatCategory(cat.category)}
                          </span>
                        </div>
                      </td>
                      <td className="px-5 py-3 text-right">
                        <span className="text-sm font-semibold text-primary-dark">
                          {formatCurrency(cat.total_amount, currency)}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-right">
                        <span className="text-sm text-muted">{pct.toFixed(1)}%</span>
                      </td>
                      <td className="px-5 py-3">
                        <div className="progress-bar w-24">
                          <div
                            className="progress-fill"
                            style={{
                              width: `${pct}%`,
                              backgroundColor: getCategoryColor(idx),
                            }}
                          />
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* Anomalies */}
      {!isLoading && anomalies.length > 0 && (
        <section className="card p-5" aria-labelledby="anomalies-title">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle size={16} className="text-warning" aria-hidden="true" />
            <h2 id="anomalies-title" className="section-title">Unusual Transactions</h2>
            <span className="badge-warning">{anomalies.length}</span>
          </div>
          <div className="space-y-2">
            {anomalies.map((anomaly) => (
              <div
                key={anomaly.transaction_id}
                className="flex items-center justify-between p-3 bg-amber-50 rounded-lg border border-amber-100"
              >
                <div className="flex items-center gap-2">
                  <Activity size={13} className="text-warning" aria-hidden="true" />
                  <span className="text-sm text-primary-dark font-medium">{anomaly.transaction_id}</span>
                  <span className="text-xs text-muted">— {anomaly.reason}</span>
                </div>
                <span className="text-xs text-warning font-medium">
                  Score: {anomaly.anomaly_score.toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Essential vs discretionary visualization */}
      {!isLoading && state && state.expenses > 0 && (
        <section className="card p-5" aria-labelledby="expense-breakdown-title">
          <h2 id="expense-breakdown-title" className="section-title mb-4">Essential vs. Discretionary</h2>
          <div className="space-y-3">
            {[
              { label: 'Essential Expenses', amount: state.essential_expenses, color: 'bg-primary-accent' },
              { label: 'Discretionary Expenses', amount: state.discretionary_expenses, color: 'bg-warning' },
            ].map((item) => {
              const pct = (item.amount / state.expenses) * 100;
              return (
                <div key={item.label}>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-sm text-primary-dark">{item.label}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-muted">{formatPercent(item.amount / state.expenses)}</span>
                      <span className="text-sm font-semibold">{formatCurrency(item.amount, currency)}</span>
                    </div>
                  </div>
                  <div className="progress-bar">
                    <div className={`progress-fill ${item.color}`} style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}
      {/* Actionable Observations */}
      {!isLoading && profile && (
        <section className="card p-5" aria-labelledby="observations-title">
          <div className="flex items-center gap-2 mb-4">
            <Activity size={16} className="text-primary-accent" aria-hidden="true" />
            <h2 id="observations-title" className="section-title">Actionable Observations</h2>
          </div>
          <div className="space-y-4">
            {profile.expense_categories_user_is_willing_to_reduce.length > 0 && (
              <div className="p-4 bg-primary-light/10 rounded-lg border border-primary-light/20">
                <h3 className="text-sm font-semibold text-primary-dark mb-1">Observed spending pressure</h3>
                <p className="text-sm text-muted mb-3">
                  Based on your profile, you indicated a willingness to reduce spending in these categories. Consider reallocating these funds to improve your cash flow buffer.
                </p>
                <div className="flex flex-wrap gap-2">
                  {profile.expense_categories_user_is_willing_to_reduce.map(cat => (
                    <span key={cat} className="badge-neutral border border-border">
                      {formatCategory(cat)}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {state && state.expense_ratio > 0.8 && (
              <div className="p-4 bg-warning/10 rounded-lg border border-warning/20">
                <h3 className="text-sm font-semibold text-warning-dark mb-1">High Expense Ratio</h3>
                <p className="text-sm text-warning-dark">
                  Your expenses currently consume {formatPercent(state.expense_ratio)} of your income. This leaves a narrow margin for unexpected costs. Focus on reducing discretionary spending.
                </p>
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  );
};
