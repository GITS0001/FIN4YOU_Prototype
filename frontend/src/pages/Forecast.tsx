import React from 'react';
import { usePrediction } from '../hooks/usePrediction';
import { useFinancialProfile } from '../hooks/useFinancialProfile';
import { useFinancialState } from '../hooks/useFinancialState';
import { useForecastHistory } from '../hooks/useForecastHistory';
import { ForecastChart } from '../components/forecast/ForecastChart';
import { ErrorState, EmptyState } from '../components/shared/ErrorState';
import { LoadingSkeleton } from '../components/shared/LoadingSkeleton';
import { formatCurrency, formatCategory, formatDate } from '../utils/format';
import { AlertTriangle, CheckCircle, Calendar, TrendingDown } from 'lucide-react';

export const Forecast: React.FC = () => {
  const { data: profile, status: profileStatus, refetch: refetchProfile } = useFinancialProfile();
  const { data: state, status: stateStatus, refetch: refetchState } = useFinancialState();
  const { data: prediction, status: predStatus, error: predError, refetch: refetchPred } = usePrediction();
  const { data: history, status: histStatus, refetch: refetchHist } = useForecastHistory();

  const isLoading = profileStatus === 'loading' || stateStatus === 'loading' || predStatus === 'loading' || histStatus === 'loading';
  const hasError = predStatus === 'error' || histStatus === 'error';

  const handleRefresh = () => {
    refetchProfile();
    refetchState();
    refetchPred();
    refetchHist();
  };

  if (hasError) {
    return <ErrorState type="data" message={predError?.message || 'Error loading forecast'} onRetry={handleRefresh} />;
  }

  const currency = profile?.home_currency || 'USD';
  const pcf = prediction?.projected_cash_flow;
  const gap = prediction?.gap_detection;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-primary-dark">Financial Forecast</h1>
        <p className="text-muted text-sm mt-0.5">Projected income, expenses, and cash flow for next month.</p>
      </div>

      {/* Availability check */}
      {!isLoading && prediction && !prediction.available && (
        <EmptyState
          title="Forecast Not Available"
          message={prediction.reason || 'Insufficient historical data to generate a forecast.'}
        />
      )}

      {/* Forecast KPIs */}
      {(isLoading || (prediction?.available && pcf)) && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: 'Projected Income', value: pcf?.projected_income, color: 'text-positive' },
            { label: 'Variable Expenses', value: pcf?.projected_expenses, color: 'text-warning' },
            { label: 'Known Obligations', value: pcf?.known_obligations, color: 'text-danger' },
            { label: 'Net Cash Flow', value: pcf?.projected_cash_flow, color: pcf && pcf.projected_cash_flow >= 0 ? 'text-positive' : 'text-danger' },
          ].map((item) => (
            <div key={item.label} className="card p-5">
              <p className="label-sm mb-2">{item.label}</p>
              {isLoading ? (
                <LoadingSkeleton height="h-7" className="w-28" />
              ) : (
                <p className={`text-xl font-bold ${item.color}`}>
                  {formatCurrency(item.value || 0, currency)}
                </p>
              )}
              <p className="text-xs text-muted mt-1">Next month estimate</p>
            </div>
          ))}
        </div>
      )}

      {/* Forecast Chart */}
      <ForecastChart
        history={history}
        profile={profile}
        isLoading={isLoading}
      />

      {/* Gap Detection */}
      {!isLoading && gap && (
        <section
          className={`card p-5 border-l-4 ${gap.detected ? 'border-l-danger' : 'border-l-positive'}`}
          aria-labelledby="gap-detection-title"
        >
          <div className="flex items-start gap-3">
            {gap.detected ? (
              <AlertTriangle size={20} className="text-danger flex-shrink-0 mt-0.5" aria-hidden="true" />
            ) : (
              <CheckCircle size={20} className="text-positive flex-shrink-0 mt-0.5" aria-hidden="true" />
            )}
            <div className="flex-1">
              <h2 id="gap-detection-title" className="section-title mb-1">
                {gap.detected ? 'Potential Cash Flow Gap Detected' : 'Cash Flow is Healthy'}
              </h2>
              {gap.detected ? (
                <p className="text-sm text-muted mb-4">
                  Your projected balance may fall below your required buffer next month.
                </p>
              ) : (
                <p className="text-sm text-muted">
                  Your projected cash flow remains above your required buffer. No action needed.
                </p>
              )}

              {gap.detected && (
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-xs text-muted">Projected Balance</p>
                    <p className="text-base font-semibold text-danger">
                      {formatCurrency(gap.projected_balance, currency)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted">Required Buffer</p>
                    <p className="text-base font-semibold text-primary-dark">
                      {formatCurrency(gap.required_buffer, currency)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted">Shortfall</p>
                    <p className="text-base font-semibold text-danger">
                      {formatCurrency(gap.shortfall, currency)}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      {/* Future Obligations */}
      {(isLoading || (prediction?.obligations && prediction.obligations.length > 0)) && (
        <section className="card overflow-hidden" aria-labelledby="obligations-title">
          <div className="px-5 py-4 border-b border-border flex items-center gap-2">
            <Calendar size={16} className="text-muted" aria-hidden="true" />
            <h2 id="obligations-title" className="section-title">Future Obligations</h2>
            {!isLoading && (
              <span className="badge-neutral">{prediction?.obligations.length}</span>
            )}
          </div>
          <div className="overflow-x-auto">
            <table className="w-full" aria-label="Future financial obligations">
              <thead>
                <tr className="bg-background text-left">
                  <th className="px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wide" scope="col">Description</th>
                  <th className="px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wide" scope="col">Category</th>
                  <th className="px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wide text-right" scope="col">Expected Amount</th>
                  <th className="px-5 py-3 text-xs font-semibold text-muted uppercase tracking-wide" scope="col">Period</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {isLoading ? (
                  [1, 2, 3].map((i) => (
                    <tr key={i} className="animate-pulse">
                      {[1, 2, 3, 4].map((j) => (
                        <td key={j} className="px-5 py-3.5">
                          <div className="skeleton h-3 w-full rounded" />
                        </td>
                      ))}
                    </tr>
                  ))
                ) : (
                  prediction?.obligations.map((ob, idx) => (
                    <tr key={idx} className="hover:bg-background transition-colors">
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-2">
                          <TrendingDown size={13} className="text-muted flex-shrink-0" aria-hidden="true" />
                          <span className="text-sm text-primary-dark">{ob.description}</span>
                        </div>
                      </td>
                      <td className="px-5 py-3.5">
                        <span className="badge-neutral">{formatCategory(ob.category)}</span>
                      </td>
                      <td className="px-5 py-3.5 text-right">
                        <span className="text-sm font-semibold text-danger">
                          {formatCurrency(ob.expected_amount, currency)}
                        </span>
                      </td>
                      <td className="px-5 py-3.5">
                        <span className="text-sm text-muted capitalize">
                          {ob.expected_period.replace(/_/g, ' ')}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Model info */}
      {!isLoading && prediction?.available && prediction.forecasts.length > 0 && (
        <div className="text-xs text-muted text-center space-y-1">
          <p>
            Forecasts generated using{' '}
            <span className="font-medium">{prediction.forecasts[0].model.replace(/_/g, ' ')}</span>
            {' '}model based on historical transaction averages.
          </p>
          <p>
            Uncertainty: Income ±{formatCurrency(prediction.forecasts.find(f => f.target === 'total_income')?.uncertainty || 0, currency)}{' '}
            | Expenses ±{formatCurrency(prediction.forecasts.find(f => f.target === 'variable_expenses')?.uncertainty || 0, currency)}
          </p>
        </div>
      )}
    </div>
  );
};
