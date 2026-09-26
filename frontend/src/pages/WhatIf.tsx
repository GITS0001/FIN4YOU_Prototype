import React, { useState } from 'react';
import { usePrediction } from '../hooks/usePrediction';
import { useFinancialProfile } from '../hooks/useFinancialProfile';
import { useSelectedUser } from '../context/UserContext';
import { usersApi } from '../api/users';
import { ScenarioComparison } from '../components/whatif/ScenarioComparison';
import { ErrorState, EmptyState } from '../components/shared/ErrorState';
import { formatCurrency } from '../utils/format';
import { GitFork, Loader2, RotateCcw, TrendingUp } from 'lucide-react';
import type { WhatIfResponse } from '../types';

type ScenarioType = 'reduce_expense' | 'add_purchase';

export const WhatIf: React.FC = () => {
  const { selectedUserId } = useSelectedUser();
  const { data: profile, status: profileStatus, error: profileError, refetch: refetchProfile } = useFinancialProfile();
  const { data: prediction, status: predStatus, error: predError, refetch: refetchPred } = usePrediction();

  const [scenarioType, setScenarioType] = useState<ScenarioType>('reduce_expense');
  const [amount, setAmount] = useState('');
  const [result, setResult] = useState<WhatIfResponse | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simError, setSimError] = useState<string | null>(null);

  const isLoading = profileStatus === 'loading' || predStatus === 'loading';
  const hasError = profileStatus === 'error' || predStatus === 'error';

  const handleRefresh = () => { refetchProfile(); refetchPred(); };

  if (hasError) {
    return (
      <ErrorState
        type={(profileError?.status === 0 || predError?.status === 0) ? 'connection' : 'data'}
        message={profileError?.message || predError?.message}
        onRetry={handleRefresh}
      />
    );
  }

  if (!isLoading && prediction && !prediction.available) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-primary-dark">What-If Simulator</h1>
        <EmptyState
          title="Forecast Not Available"
          message={prediction.reason || 'Insufficient historical data to run simulations.'}
        />
      </div>
    );
  }

  const currency = profile?.home_currency || 'EUR';
  const pcf = prediction?.projected_cash_flow;

  const runSimulation = async (overrideAmount?: string) => {
    const valToSimulate = overrideAmount || amount;
    const numAmount = parseFloat(valToSimulate);
    if (isNaN(numAmount) || numAmount <= 0) return;

    if (overrideAmount) {
      setAmount(overrideAmount);
    }

    setIsSimulating(true);
    setSimError(null);
    setResult(null);

    try {
      const res = await usersApi.runWhatIf(selectedUserId, scenarioType, numAmount);
      setResult(res);
    } catch (err: unknown) {
      const e = err as { message?: string };
      setSimError(e?.message || 'Simulation failed. Please try again.');
    } finally {
      setIsSimulating(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setAmount('');
    setSimError(null);
  };

  // Quick suggestion amounts — proportional to projected cash flow
  const baseAmount = pcf ? Math.abs(pcf.projected_cash_flow) : 100;
  const quickAmounts = [
    Math.round(baseAmount * 0.1),
    Math.round(baseAmount * 0.25),
    Math.round(baseAmount * 0.5),
    Math.round(baseAmount),
    Math.round(baseAmount * 2),
  ].filter((v, i, a) => v > 0 && a.indexOf(v) === i);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-primary-dark">What-If Simulator</h1>
        <p className="text-muted text-sm mt-0.5">
          Run deterministic backend simulations to see how financial changes affect your projected balance.
        </p>
      </div>

      {/* Grid container for Baseline and Scenario Builder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {!isLoading && pcf && (
        <section className="card p-5 bg-slate-50 border border-slate-200" aria-labelledby="baseline-title">
          <h2 id="baseline-title" className="section-title mb-4">Current Baseline (Next Month)</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-white p-4 rounded-xl border border-slate-100">
              <p className="text-xs text-muted mb-1">Projected Income</p>
              <p className="text-lg font-bold text-positive">{formatCurrency(pcf.projected_income, currency)}</p>
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-100">
              <p className="text-xs text-muted mb-1">Variable Expenses</p>
              <p className="text-lg font-bold text-warning">{formatCurrency(pcf.projected_expenses, currency)}</p>
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-100">
              <p className="text-xs text-muted mb-1">Known Obligations</p>
              <p className="text-lg font-bold text-danger">{formatCurrency(pcf.known_obligations, currency)}</p>
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-100">
              <p className="text-xs text-muted mb-1">Net Cash Flow</p>
              <p className={`text-lg font-bold ${pcf.projected_cash_flow >= 0 ? 'text-positive' : 'text-danger'}`}>
                {formatCurrency(pcf.projected_cash_flow, currency)}
              </p>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-200 flex items-center gap-2">
            <p className="text-xs text-muted">Simulation applies changes to this baseline via the backend calculation engine.</p>
          </div>
        </section>
      )}

      {/* Scenario builder */}
      <section className="card p-6" aria-labelledby="scenario-builder-title">
        <div className="flex items-center gap-2 mb-5">
          <GitFork size={16} className="text-primary-accent" aria-hidden="true" />
          <h2 id="scenario-builder-title" className="section-title">What happens if...</h2>
        </div>

        {/* Scenario type */}
        <div className="mb-5">
          <p className="label-sm mb-2">Scenario Type</p>
          <div className="grid grid-cols-2 gap-3">
            {[
              { type: 'reduce_expense' as const, label: 'I reduce my expenses by...', sub: 'Discretionary spending reduction' },
              { type: 'add_purchase' as const, label: 'I make a purchase of...', sub: 'One-time additional expense' },
            ].map((opt) => (
              <button
                key={opt.type}
                className={`text-left p-4 rounded-xl border-2 transition-all duration-150 ${
                  scenarioType === opt.type
                    ? 'border-primary-accent bg-blue-50/30'
                    : 'border-border hover:border-muted'
                }`}
                onClick={() => { setScenarioType(opt.type); setResult(null); setSimError(null); }}
                aria-pressed={scenarioType === opt.type}
              >
                <p className="text-sm font-semibold text-primary-dark">{opt.label}</p>
                <p className="text-xs text-muted mt-0.5">{opt.sub}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Amount input */}
        <div className="mb-5">
          <label htmlFor="scenario-amount" className="label-sm block mb-2">
            Amount ({currency})
          </label>
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted text-sm font-medium">
                {currency}
              </span>
              <input
                id="scenario-amount"
                type="number"
                value={amount}
                onChange={(e) => { setAmount(e.target.value); setResult(null); setSimError(null); }}
                placeholder="0"
                min="1"
                className="form-input pl-14"
                aria-label={`Enter amount in ${currency}`}
                onKeyDown={(e) => e.key === 'Enter' && runSimulation()}
              />
            </div>
            <button
              className="btn-primary px-6 flex items-center gap-2"
              onClick={() => runSimulation()}
              disabled={!amount || parseFloat(amount) <= 0 || isSimulating || isLoading}
              aria-label="Run simulation"
            >
              {isSimulating ? (
                <Loader2 size={14} className="animate-spin" aria-hidden="true" />
              ) : (
                <GitFork size={14} aria-hidden="true" />
              )}
              {isSimulating ? 'Simulating...' : 'Simulate'}
            </button>
            {result && (
              <button className="btn-secondary flex items-center gap-2" onClick={handleReset}>
                <RotateCcw size={14} aria-hidden="true" />
                Reset
              </button>
            )}
          </div>
        </div>

        {/* Quick suggestions */}
        {!result && !isLoading && (
          <div>
            <p className="label-sm mb-2">Quick Examples</p>
            <div className="flex flex-wrap gap-2">
              {quickAmounts.map((val) => (
                <button
                  key={val}
                  className="px-3 py-1.5 text-xs border border-border rounded-lg hover:border-primary-accent hover:text-primary-accent transition-colors"
                  onClick={() => runSimulation(String(val))}
                >
                  {formatCurrency(val, currency)}
                </button>
              ))}
            </div>
          </div>
        )}
      </section>
      </div>

      {/* Sim Error */}
      {simError && (
        <div className="card p-4 border-l-4 border-l-danger bg-red-50">
          <p className="text-sm text-danger font-medium">{simError}</p>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="space-y-5 animate-slide-up">
          <div className="flex items-center justify-between">
            <h2 className="section-title">
              Scenario: {scenarioType === 'reduce_expense' ? 'Reduce expenses by' : 'Purchase of'}{' '}
              {formatCurrency(parseFloat(amount), currency)}
            </h2>
            <span className={`text-sm font-semibold px-3 py-1 rounded-full ${
              result.impact.buffer_status_change === 'maintained' || result.impact.buffer_status_change === 'restored'
                ? 'bg-green-50 text-positive border border-green-100'
                : result.impact.buffer_status_change === 'improved_but_still_breached'
                ? 'bg-amber-50 text-warning border border-amber-100'
                : 'bg-red-50 text-danger border border-red-100'
            }`}>
              Buffer: {result.impact.buffer_status_change.replace(/_/g, ' ')}
            </span>
          </div>

          {/* Comparison table */}
          <ScenarioComparison
            baseline={{
              label: 'Current Baseline',
              income: result.baseline.projected_income,
              expenses: result.baseline.projected_expenses + result.baseline.known_obligations,
              cashFlow: result.baseline.projected_cash_flow,
              balance: result.baseline.projected_balance,
              bufferBreached: result.baseline.buffer_breached,
              shortfall: result.baseline.shortfall,
            }}
            scenario={{
              label: scenarioType === 'reduce_expense' ? 'With Reduction' : 'With Purchase',
              income: result.scenario.projected_income,
              expenses: result.scenario.projected_expenses + result.scenario.known_obligations,
              cashFlow: result.scenario.projected_cash_flow,
              balance: result.scenario.projected_balance,
              bufferBreached: result.scenario.buffer_breached,
              shortfall: result.scenario.shortfall,
            }}
            currency={currency}
          />

          {/* Impact summary */}
          <div className="card p-5 mt-6 border-l-4 border-l-primary-accent bg-blue-50/20">
            <h3 className="text-sm font-bold text-primary-dark mb-3 flex items-center gap-2">
              <TrendingUp size={16} className="text-primary-accent" />
              Expected Impact
            </h3>
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div>
                <p className="text-xs text-muted mb-1">Cash Flow Change</p>
                <p className={`text-lg font-bold ${result.impact.cash_flow_difference >= 0 ? 'text-positive' : 'text-danger'}`}>
                  {result.impact.cash_flow_difference >= 0 ? '+' : ''}{formatCurrency(result.impact.cash_flow_difference, currency)}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted mb-1">Balance Change</p>
                <p className={`text-lg font-bold ${result.impact.balance_difference >= 0 ? 'text-positive' : 'text-danger'}`}>
                  {result.impact.balance_difference >= 0 ? '+' : ''}{formatCurrency(result.impact.balance_difference, currency)}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted mb-1">Buffer Status</p>
                <p className={`text-sm font-semibold ${
                  result.impact.buffer_status_change === 'maintained' || result.impact.buffer_status_change === 'restored'
                    ? 'text-positive' : 'text-warning'
                }`}>
                  {result.impact.buffer_status_change.replace(/_/g, ' ')}
                </p>
              </div>
            </div>
            
            <div className="pt-4 border-t border-slate-200">
              <h4 className="text-xs font-bold text-primary-dark uppercase tracking-wider mb-2">Recommendation</h4>
              <p className="text-sm text-primary-dark">
                {result.impact.buffer_status_change === 'breached' || result.impact.buffer_status_change === 'improved_but_still_breached'
                  ? 'Avoid this change if possible. It will place your account balance below your required minimum safety buffer.'
                  : 'This change maintains your financial health and safety buffer.'}
              </p>
            </div>
          </div>

          {/* Methodology note (acting as decision trace info here) */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
            <p className="text-sm text-primary-dark font-medium mb-1">Decision Trace</p>
            <p className="text-xs text-muted">
              Observed baseline income and expenses → Applied scenario delta ({formatCurrency(parseFloat(amount), currency)}) → Simulated resulting cash flow → Compared against minimum buffer limit to generate recommendation.
            </p>
          </div>
        </div>
      )}

      {/* Empty state with copilot tip */}
      {!result && !simError && (
        <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
          <p className="text-sm text-primary-dark font-medium mb-1">💡 Try Artha AI</p>
          <p className="text-xs text-muted">
            You can also ask Artha AI natural-language questions like{' '}
            <em>"What if I spend {formatCurrency(pcf ? Math.round(pcf.projected_expenses * 0.2) : 100, currency)} less on dining?"</em>
          </p>
        </div>
      )}
    </div>
  );
};
