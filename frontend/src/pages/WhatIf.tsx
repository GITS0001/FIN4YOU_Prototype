import React, { useState } from 'react';
import { usePrediction } from '../hooks/usePrediction';
import { useFinancialProfile } from '../hooks/useFinancialProfile';
import { ScenarioComparison } from '../components/whatif/ScenarioComparison';
import { ErrorState, EmptyState } from '../components/shared/ErrorState';
import { formatCurrency } from '../utils/format';
import { GitFork, Loader2, RotateCcw } from 'lucide-react';

type ScenarioType = 'reduce_expense' | 'add_purchase';

interface SimulationResult {
  scenarioName: string;
  baseline: {
    label: string;
    income: number;
    expenses: number;
    cashFlow: number;
    balance: number;
    bufferBreached: boolean;
    shortfall: number;
  };
  scenario: {
    label: string;
    income: number;
    expenses: number;
    cashFlow: number;
    balance: number;
    bufferBreached: boolean;
    shortfall: number;
  };
}

export const WhatIf: React.FC = () => {
  const { data: profile, status: profileStatus, refetch: refetchProfile } = useFinancialProfile();
  const { data: prediction, status: predStatus, error: predError, refetch: refetchPred } = usePrediction();

  const [scenarioType, setScenarioType] = useState<ScenarioType>('reduce_expense');
  const [amount, setAmount] = useState('');
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  const isLoading = profileStatus === 'loading' || predStatus === 'loading';
  const hasError = predStatus === 'error';

  const handleRefresh = () => {
    refetchProfile();
    refetchPred();
  };

  if (hasError) {
    return <ErrorState type="data" message={predError?.message} onRetry={handleRefresh} />;
  }

  if (!isLoading && (!prediction?.available || !prediction?.projected_cash_flow)) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-primary-dark">What-If Simulator</h1>
        <EmptyState
          title="Forecast Not Available"
          message={prediction?.reason || 'Insufficient historical data to run simulations.'}
        />
      </div>
    );
  }

  const currency = profile?.home_currency || 'USD';
  const pcf = prediction?.projected_cash_flow;

  const runSimulation = () => {
    if (!pcf || !profile) return;
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount) || numAmount <= 0) return;

    setIsSimulating(true);

    // Deterministic simulation on the frontend using the projected cash flow data
    const baselineIncome = pcf.projected_income;
    const baselineExpenses = pcf.projected_expenses + pcf.known_obligations;
    const baselineCashFlow = pcf.projected_cash_flow;
    const baselineBalance = profile.current_available_balance + baselineCashFlow;
    const baselineShortfall = Math.max(0, profile.minimum_balance_to_keep - baselineBalance);

    let scenarioIncome = baselineIncome;
    let scenarioExpenses = baselineExpenses;
    let scenarioName = '';

    if (scenarioType === 'reduce_expense') {
      scenarioExpenses = Math.max(0, baselineExpenses - numAmount);
      scenarioName = `Reduce expenses by ${formatCurrency(numAmount, currency)}`;
    } else {
      // One-time purchase hits the balance directly
      scenarioExpenses = baselineExpenses + numAmount;
      scenarioName = `Purchase of ${formatCurrency(numAmount, currency)}`;
    }

    const scenarioCashFlow = scenarioIncome - scenarioExpenses;
    const scenarioBalance = profile.current_available_balance + scenarioCashFlow;
    const scenarioShortfall = Math.max(0, profile.minimum_balance_to_keep - scenarioBalance);

    setTimeout(() => {
      setResult({
        scenarioName,
        baseline: {
          label: 'Current',
          income: baselineIncome,
          expenses: baselineExpenses,
          cashFlow: baselineCashFlow,
          balance: baselineBalance,
          bufferBreached: baselineShortfall > 0,
          shortfall: baselineShortfall,
        },
        scenario: {
          label: 'Scenario',
          income: scenarioIncome,
          expenses: scenarioExpenses,
          cashFlow: scenarioCashFlow,
          balance: scenarioBalance,
          bufferBreached: scenarioShortfall > 0,
          shortfall: scenarioShortfall,
        },
      });
      setIsSimulating(false);
    }, 400); // Small artificial delay for UX
  };

  const handleReset = () => {
    setResult(null);
    setAmount('');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-primary-dark">What-If Simulator</h1>
        <p className="text-muted text-sm mt-0.5">
          Simulate financial scenarios and see how they affect your projected balance.
        </p>
      </div>

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
              { type: 'reduce_expense' as const, label: 'I reduce my expenses by...', sub: 'Spending reduction simulation' },
              { type: 'add_purchase' as const, label: 'I make a purchase of...', sub: 'One-time expense simulation' },
            ].map((opt) => (
              <button
                key={opt.type}
                className={`text-left p-4 rounded-xl border-2 transition-all duration-150 ${
                  scenarioType === opt.type
                    ? 'border-primary-accent bg-blue-50/30'
                    : 'border-border hover:border-muted'
                }`}
                onClick={() => { setScenarioType(opt.type); setResult(null); }}
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
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted text-sm" aria-hidden="true">
                {currency === 'EUR' ? '€' : currency === 'IDR' ? 'Rp' : currency === 'USD' ? '$' : '₹'}
              </span>
              <input
                id="scenario-amount"
                type="number"
                value={amount}
                onChange={(e) => { setAmount(e.target.value); setResult(null); }}
                placeholder="0"
                min="1"
                className="form-input pl-8"
                aria-label={`Enter amount in ${currency}`}
              />
            </div>
            <button
              className="btn-primary px-6 flex items-center gap-2"
              onClick={runSimulation}
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
        {!result && (
          <div>
            <p className="label-sm mb-2">Quick Examples</p>
            <div className="flex flex-wrap gap-2">
              {['1000', '5000', '10000', '25000', '50000'].map((val) => (
                <button
                  key={val}
                  className="px-3 py-1.5 text-xs border border-border rounded-lg hover:border-primary-accent hover:text-primary-accent transition-colors"
                  onClick={() => setAmount(val)}
                >
                  {formatCurrency(parseFloat(val), currency)}
                </button>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* Result */}
      {result && (
        <div className="animate-slide-up">
          <div className="flex items-center justify-between mb-4">
            <h2 className="section-title">Scenario: {result.scenarioName}</h2>
          </div>
          <ScenarioComparison
            baseline={result.baseline}
            scenario={result.scenario}
            currency={currency}
          />
        </div>
      )}

      {/* Copilot tip */}
      {!result && (
        <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
          <p className="text-sm text-primary-dark font-medium mb-1">💡 Try the AI Copilot</p>
          <p className="text-xs text-muted">
            You can also ask the AI Copilot natural language questions like{' '}
            <em>"What if I spend {formatCurrency(5000, currency)} less on dining?"</em>
          </p>
        </div>
      )}
    </div>
  );
};
