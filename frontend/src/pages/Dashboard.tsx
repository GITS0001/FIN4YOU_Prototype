import React from 'react';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  PiggyBank,
  Activity,
  ArrowUpRight,
  AlertTriangle,
  CheckCircle,
} from 'lucide-react';
import { useFinancialProfile } from '../hooks/useFinancialProfile';
import { useFinancialState } from '../hooks/useFinancialState';
import { usePrediction } from '../hooks/usePrediction';
import { KpiCard } from '../components/dashboard/KpiCard';
import { FinancialHealthCard } from '../components/dashboard/FinancialHealthCard';
import { SpendingChart } from '../components/dashboard/SpendingChart';
import { ErrorState } from '../components/shared/ErrorState';
import { formatCurrency, formatPercent, getGreeting } from '../utils/format';
import { useNavigate } from 'react-router-dom';
import { useSelectedUser } from '../context/UserContext';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { selectedUserId } = useSelectedUser();
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

  const currency = profile?.home_currency || 'EUR';

  // Determine observed period info from state
  const periodLabel = 'Observed total';

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
      subValue: periodLabel,
    },
    {
      label: 'Expenses',
      value: isLoading ? '—' : formatCurrency(state?.expenses || 0, currency),
      icon: TrendingDown,
      iconColor: 'text-danger bg-red-50',
      subValue: periodLabel,
    },
    {
      label: 'Net Savings',
      value: isLoading ? '—' : formatCurrency(state?.savings || 0, currency),
      icon: PiggyBank,
      iconColor: (state?.savings || 0) >= 0 ? 'text-positive bg-green-50' : 'text-danger bg-red-50',
      trend: (state?.savings || 0) >= 0 ? 'up' as const : 'down' as const,
      trendLabel: isLoading ? undefined : state ? `Rate: ${formatPercent(state.savings_rate)}` : undefined,
    },
    {
      label: 'Hist. Cash Flow',
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

  const gap = prediction?.gap_detection;
  const pcf = prediction?.projected_cash_flow;

  return (
    <div className="space-y-6">
      {/* Greeting header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-primary-dark">
            {getGreeting()} — <span className="text-primary-accent">{selectedUserId}</span>
          </h1>
          <p className="text-muted text-sm mt-0.5">
            Financial decision intelligence · {currency} · Observed period analysis
          </p>
        </div>
        <button
          className="btn-primary flex items-center gap-2 text-sm"
          onClick={() => navigate('/copilot')}
        >
          <Activity size={15} aria-hidden="true" />
          Ask Artha AI
        </button>
      </div>

      {/* KPI Cards — all show "Observed total" period label */}
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
      <div className="flex flex-col gap-5 mt-5">
        
        {/* ROW 2: Financial Health Indicators + Upcoming Cash Flow / Risk */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <FinancialHealthCard
            state={state}
            profile={profile}
            isLoading={isLoading}
          />
          {/* Upcoming Cash Flow Risk - next month projection */}
          <div className={`card p-5 border-l-4 ${gap?.detected ? 'border-l-danger' : 'border-l-positive'} flex flex-col justify-between`}>
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="section-title">Next Month Projection</h2>
                  <p className="text-xs text-muted mt-0.5">
                    {gap?.detected ? '⚠ Cash flow gap detected' : '✓ Buffer maintained'}
                  </p>
                </div>
                {gap?.detected ? (
                  <AlertTriangle size={18} className="text-danger" aria-hidden="true" />
                ) : (
                  <CheckCircle size={18} className="text-positive" aria-hidden="true" />
                )}
              </div>

              {!isLoading && pcf && (
                <div className="grid grid-cols-2 gap-3 mb-4">
                  <div className="bg-background p-3 rounded-xl border border-border">
                    <p className="text-xs text-muted mb-1">Projected Income</p>
                    <p className="text-base font-semibold text-positive">
                      {formatCurrency(pcf.projected_income, currency)}
                    </p>
                  </div>
                  <div className="bg-background p-3 rounded-xl border border-border">
                    <p className="text-xs text-muted mb-1">Total Outflows</p>
                    <p className="text-base font-semibold text-danger">
                      {formatCurrency(pcf.projected_expenses + pcf.known_obligations, currency)}
                    </p>
                  </div>
                </div>
              )}

              {!isLoading && pcf && (
                <div className="flex items-center justify-between p-3 bg-primary-accent/10 rounded-xl border border-primary-accent/20">
                  <div>
                    <p className="text-xs text-muted mb-1">Net Cash Flow</p>
                    <p className={`text-lg font-bold ${pcf.projected_cash_flow >= 0 ? 'text-positive' : 'text-danger'}`}>
                      {formatCurrency(pcf.projected_cash_flow, currency)}
                    </p>
                  </div>
                  {gap && (
                    <div className="text-right">
                      <p className="text-xs text-muted mb-1">Proj. Balance</p>
                      <p className={`text-sm font-semibold ${gap.projected_balance >= gap.required_buffer ? 'text-positive' : 'text-danger'}`}>
                        {formatCurrency(gap.projected_balance, currency)}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {isLoading && <div className="skeleton h-28 w-full rounded-xl" />}
            </div>

            <button
              className="btn-secondary text-sm w-full mt-4"
              onClick={() => navigate('/forecast')}
            >
              View Full Forecast
            </button>
          </div>
        </div>

        {/* ROW 3: Income vs Expenses proportion + Spending breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card p-6 flex flex-col">
            <div className="flex items-center justify-between mb-1">
              <h2 className="section-title">Income vs Expenses</h2>
              <span className="text-xs text-muted px-2 py-0.5 bg-slate-100 rounded-full">Observed period total</span>
            </div>
            <p className="text-xs text-muted mb-4">
              All figures represent the full observed transaction history, not a single month.
            </p>
            {isLoading ? (
               <div className="flex-1 flex items-center justify-center"><div className="skeleton h-40 w-full" /></div>
            ) : (
              <div className="flex-1 flex items-center justify-center">
                <div className="w-full space-y-5">
                  <div>
                    <div className="flex justify-between text-sm mb-1.5">
                      <span className="font-medium text-slate-700">Total Income</span>
                      <span className="font-bold text-positive">{formatCurrency(state?.income || 0, currency)}</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2.5">
                      <div className="bg-positive h-2.5 rounded-full" style={{ width: '100%' }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1.5">
                      <span className="font-medium text-slate-700">Total Expenses</span>
                      <span className="font-bold text-danger">{formatCurrency(state?.expenses || 0, currency)}</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2.5">
                      <div className="bg-danger h-2.5 rounded-full" style={{ width: `${Math.min(100, ((state?.expenses || 0) / (state?.income || 1)) * 100)}%` }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1.5">
                      <span className="font-medium text-slate-700">Net Savings</span>
                      <span className={`font-bold ${(state?.savings || 0) >= 0 ? 'text-primary-accent' : 'text-danger'}`}>
                        {formatCurrency(state?.savings || 0, currency)}
                      </span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2.5">
                      <div
                        className={`h-2.5 rounded-full ${(state?.savings || 0) >= 0 ? 'bg-primary-accent' : 'bg-danger'}`}
                        style={{ width: `${Math.max(0, Math.min(100, Math.abs((state?.savings || 0) / (state?.income || 1)) * 100))}%` }}
                      ></div>
                    </div>
                  </div>
                  {/* Essential vs Discretionary */}
                  <div className="pt-3 border-t border-slate-100 grid grid-cols-2 gap-3">
                    <div className="bg-slate-50 rounded-lg p-2.5">
                      <p className="text-xs text-muted mb-0.5">Essential</p>
                      <p className="text-sm font-semibold text-slate-700">{formatCurrency(state?.essential_expenses || 0, currency)}</p>
                    </div>
                    <div className="bg-slate-50 rounded-lg p-2.5">
                      <p className="text-xs text-muted mb-0.5">Discretionary</p>
                      <p className="text-sm font-semibold text-slate-700">{formatCurrency(state?.discretionary_expenses || 0, currency)}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
          <SpendingChart
            categories={state?.category_spending || []}
            currency={currency}
            isLoading={isLoading}
            totalExpenses={state?.expenses || 0}
          />
        </div>

        {/* ROW 4: What Needs Attention + Obligations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* What Needs Attention Section */}
          <div className="card p-6 border-t-4 border-t-warning flex flex-col justify-start bg-amber-50/20 self-start">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle size={18} className="text-warning" />
              <h2 className="section-title">What Needs Attention</h2>
            </div>
            
            {isLoading ? (
              <div className="skeleton h-32 w-full" />
            ) : state && ((state.expense_ratio || 0) > 0.8 || gap?.detected || (state.savings ?? 0) < 0) ? (
              <div className="flex flex-col gap-3">
                {(state.expense_ratio || 0) > 0.8 && (
                  <div className="bg-white p-4 rounded-xl shadow-sm border border-amber-100">
                    <p className="text-sm font-semibold text-amber-900 mb-1">High Expense Ratio</p>
                    <p className="text-sm text-muted">You are spending {formatPercent(state.expense_ratio!)} of your income. Consider reducing discretionary expenses.</p>
                  </div>
                )}
                {gap?.detected && (
                  <div className="bg-white p-4 rounded-xl shadow-sm border border-amber-100">
                    <p className="text-sm font-semibold text-amber-900 mb-1">Cash Flow Pressure</p>
                    <p className="text-sm text-muted">Next month's projected cash flow puts you below your minimum buffer constraint.</p>
                  </div>
                )}
                {(state?.savings ?? 0) < 0 && (
                  <div className="bg-white p-4 rounded-xl shadow-sm border border-amber-100">
                    <p className="text-sm font-semibold text-amber-900 mb-1">Negative Net Savings</p>
                    <p className="text-sm text-muted">Your observed total expenses exceed your income. You are drawing down on your reserves.</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center bg-white rounded-xl border border-slate-100 p-6">
                <p className="text-sm text-muted">No immediate attention required. Finances are stable.</p>
              </div>
            )}
          </div>

          <div className="card p-6 flex flex-col justify-start">
            <h2 className="section-title mb-1">Upcoming Obligations</h2>
            <p className="text-xs text-muted mb-4">Fixed recurring commitments projected for next month</p>
            {isLoading ? (
               <div className="skeleton h-32 w-full" />
            ) : (
              <div className="space-y-2">
                {prediction?.obligations && prediction.obligations.length > 0 ? (
                  <>
                    {prediction.obligations.slice(0, 6).map((obs, i) => (
                      <div key={i} className="flex justify-between items-center p-2.5 border border-slate-100 rounded-lg bg-slate-50">
                        <div>
                          <p className="text-sm font-medium text-slate-800 capitalize">{obs.category.replace(/_/g, ' ')}</p>
                          <p className="text-xs text-muted truncate max-w-[160px]">{obs.description}</p>
                        </div>
                        <p className="text-sm font-bold text-danger flex-shrink-0">{formatCurrency(obs.expected_amount, currency)}</p>
                      </div>
                    ))}
                    {prediction.obligations.length > 6 && (
                      <p className="text-xs text-muted text-center pt-1">
                        +{prediction.obligations.length - 6} more obligations
                      </p>
                    )}
                    <div className="mt-3 pt-3 border-t border-slate-100 flex justify-between items-center">
                      <p className="text-sm font-semibold text-slate-700">Total Obligations</p>
                      <p className="text-sm font-bold text-danger">
                        {formatCurrency(prediction.obligations.reduce((s, o) => s + o.expected_amount, 0), currency)}
                      </p>
                    </div>
                  </>
                ) : (
                  <p className="text-sm text-muted">No upcoming fixed obligations detected.</p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* ROW 5: AI Copilot entry with scenario chips */}
        <div className="card p-6 bg-gradient-to-br from-primary-dark to-[#1e274a] text-white">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 mb-6">
            <div>
              <h2 className="text-xl font-bold mb-1">Financial Intelligence with Artha AI</h2>
              <p className="text-white/80 text-sm">
                Ask natural-language questions. Get structured, evidence-backed financial answers.
              </p>
            </div>
            <button
              className="bg-primary-accent text-white hover:bg-accent-hover px-5 py-2.5 rounded-lg font-medium text-sm transition-colors flex items-center gap-2 whitespace-nowrap shadow-md"
              onClick={() => navigate('/copilot')}
            >
              <Activity size={16} />
              Open Artha AI
            </button>
          </div>
          
          <div className="pt-4 border-t border-white/10">
            <p className="text-sm text-white/70 mb-3 font-medium tracking-wide">TRY A SCENARIO</p>
            <div className="flex flex-wrap gap-2">
              {[
                'Can I afford a purchase in installments?',
                'What is my cash flow next month?',
                'Give me a financial summary',
                'What if I spend less on dining?',
                'How can I improve my finances?',
              ].map((q) => (
                <button
                  key={q}
                  onClick={() => navigate('/copilot')}
                  className="px-3 py-1.5 bg-white/10 hover:bg-white/20 border border-white/20 rounded-full text-xs transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
