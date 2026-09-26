import React, { useState } from 'react';
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  CreditCard,
  DollarSign,
  Shield,
  TrendingDown,
  Loader2,
} from 'lucide-react';
import { usersApi } from '../api/users';
import { useFinancialProfile } from '../hooks/useFinancialProfile';
import { usePrediction } from '../hooks/usePrediction';
import { useSelectedUser } from '../context/UserContext';
import { formatCurrency, formatPercent } from '../utils/format';
import { LoadingSkeleton } from '../components/shared/LoadingSkeleton';
import { ErrorState } from '../components/shared/ErrorState';
import type { AffordabilityResult } from '../types';

const STATUS_CONFIG: Record<string, { color: string; bg: string; border: string; icon: React.ElementType; label: string }> = {
  'AFFORDABLE': {
    color: 'text-positive',
    bg: 'bg-green-50',
    border: 'border-positive',
    icon: CheckCircle,
    label: 'Affordable',
  },
  'POTENTIALLY AFFORDABLE WITH TRADE-OFF': {
    color: 'text-warning',
    bg: 'bg-amber-50',
    border: 'border-warning',
    icon: AlertTriangle,
    label: 'Trade-off Required',
  },
  'NOT AFFORDABLE UNDER CURRENT PROJECTION': {
    color: 'text-danger',
    bg: 'bg-red-50',
    border: 'border-danger',
    icon: XCircle,
    label: 'Not Affordable',
  },
  'INSUFFICIENT DATA': {
    color: 'text-muted',
    bg: 'bg-slate-50',
    border: 'border-border',
    icon: AlertTriangle,
    label: 'Insufficient Data',
  },
};

export const Affordability: React.FC = () => {
  const { selectedUserId } = useSelectedUser();
  const { data: profile, status: profileStatus } = useFinancialProfile();
  const { data: prediction } = usePrediction();

  const [amount, setAmount] = useState('');
  const [result, setResult] = useState<AffordabilityResult | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [checkError, setCheckError] = useState<string | null>(null);

  const isLoading = profileStatus === 'loading';
  const currency = profile?.home_currency || 'EUR';

  const handleCheck = async (overrideAmount?: string) => {
    const valToCheck = overrideAmount || amount;
    const numAmount = parseFloat(valToCheck.replace(/,/g, ''));
    if (isNaN(numAmount) || numAmount <= 0) return;

    if (overrideAmount) {
      setAmount(overrideAmount);
    }

    setIsChecking(true);
    setCheckError(null);
    setResult(null);

    try {
      const res = await usersApi.checkAffordability(selectedUserId, numAmount);
      setResult(res);
    } catch (err: unknown) {
      const e = err as { message?: string };
      setCheckError(e?.message || 'Failed to check affordability. Please try again.');
    } finally {
      setIsChecking(false);
    }
  };

  const statusConfig = result ? (STATUS_CONFIG[result.status] || STATUS_CONFIG['INSUFFICIENT DATA']) : null;
  const StatusIcon = statusConfig?.icon || AlertTriangle;

  // Pre-compute quick check amounts relevant to user balance
  const quickAmounts = profile
    ? [
        Math.round(profile.current_available_balance * 0.1),
        Math.round(profile.current_available_balance * 0.25),
        Math.round(profile.current_available_balance * 0.5),
        Math.round(profile.current_available_balance * 0.75),
        Math.round(profile.current_available_balance * 1.0),
      ]
    : [100, 500, 1000, 5000, 10000];

  const pcf = prediction?.projected_cash_flow;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-primary-dark">Affordability Check</h1>
        <p className="text-muted text-sm mt-0.5">
          Evaluate whether you can afford a purchase based on your projected cash flow and minimum buffer.
        </p>
      </div>

      {/* Top Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Current Position */}
      <section className="card p-5" aria-labelledby="current-position-title">
        <h2 id="current-position-title" className="section-title mb-4">Your Current Financial Position</h2>
        {isLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[1,2,3,4].map(i => <LoadingSkeleton key={i} height="h-16" />)}
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-blue-50 rounded-xl p-4 border border-blue-100">
              <div className="flex items-center gap-2 mb-2">
                <DollarSign size={14} className="text-primary-accent" />
                <p className="text-xs text-muted">Available Balance</p>
              </div>
              <p className="text-xl font-bold text-primary-dark">
                {formatCurrency(profile?.current_available_balance || 0, currency)}
              </p>
            </div>
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
              <div className="flex items-center gap-2 mb-2">
                <Shield size={14} className="text-warning" />
                <p className="text-xs text-muted">Min. Buffer Required</p>
              </div>
              <p className="text-xl font-bold text-primary-dark">
                {formatCurrency(profile?.minimum_balance_to_keep || 0, currency)}
              </p>
            </div>
            <div className={`rounded-xl p-4 border ${pcf && pcf.projected_cash_flow >= 0 ? 'bg-green-50 border-green-100' : 'bg-red-50 border-red-100'}`}>
              <div className="flex items-center gap-2 mb-2">
                <TrendingDown size={14} className={pcf && pcf.projected_cash_flow >= 0 ? 'text-positive' : 'text-danger'} />
                <p className="text-xs text-muted">Proj. Cash Flow</p>
              </div>
              <p className={`text-xl font-bold ${pcf && pcf.projected_cash_flow >= 0 ? 'text-positive' : 'text-danger'}`}>
                {pcf ? formatCurrency(pcf.projected_cash_flow, currency) : '—'}
              </p>
            </div>
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
              <div className="flex items-center gap-2 mb-2">
                <CreditCard size={14} className="text-muted" />
                <p className="text-xs text-muted">Available Headroom</p>
              </div>
              <p className="text-xl font-bold text-primary-dark">
                {formatCurrency(
                  Math.max(0, (profile?.current_available_balance || 0) - (profile?.minimum_balance_to_keep || 0)),
                  currency
                )}
              </p>
            </div>
          </div>
        )}
      </section>

      {/* Check Input */}
      <section className="card p-6" aria-labelledby="check-title">
        <div className="flex items-center gap-2 mb-5">
          <CreditCard size={16} className="text-primary-accent" />
          <h2 id="check-title" className="section-title">Can I Afford This?</h2>
        </div>

        <div className="mb-5">
          <label htmlFor="affordability-amount" className="label-sm block mb-2">
            Purchase Amount ({currency})
          </label>
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted text-sm font-medium">
                {currency}
              </span>
              <input
                id="affordability-amount"
                type="number"
                value={amount}
                onChange={(e) => { setAmount(e.target.value); setResult(null); }}
                placeholder="0.00"
                min="0.01"
                step="0.01"
                className="form-input pl-14"
                aria-label={`Enter purchase amount in ${currency}`}
                onKeyDown={(e) => e.key === 'Enter' && handleCheck()}
              />
            </div>
            <button
              className="btn-primary px-6 flex items-center gap-2"
              onClick={() => handleCheck()}
              disabled={!amount || parseFloat(amount) <= 0 || isChecking || isLoading}
              aria-label="Check affordability"
            >
              {isChecking ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <CheckCircle size={14} />
              )}
              {isChecking ? 'Checking...' : 'Check Affordability'}
            </button>
          </div>
        </div>

        {/* Quick amounts */}
        <div>
          <p className="label-sm mb-2">Quick Check</p>
          <div className="flex flex-wrap gap-2">
            {quickAmounts.map((val) => (
              <button
                key={val}
                className="px-3 py-1.5 text-xs border border-border rounded-lg hover:border-primary-accent hover:text-primary-accent transition-colors"
                onClick={() => handleCheck(String(val))}
              >
                {formatCurrency(val, currency)}
              </button>
            ))}
          </div>
        </div>
      </section>
      </div>

      {/* Error state */}
      {checkError && (
        <div className="card p-4 border-l-4 border-l-danger bg-red-50">
          <div className="flex items-center gap-2">
            <XCircle size={16} className="text-danger" />
            <p className="text-sm text-danger font-medium">{checkError}</p>
          </div>
        </div>
      )}

      {/* Result */}
      {result && statusConfig && (
        <div className="space-y-5 animate-slide-up">
          {/* Status Banner */}
          <div className={`card p-5 border-l-4 ${statusConfig.border} ${statusConfig.bg}`}>
            <div className="flex items-start gap-3">
              <StatusIcon size={22} className={`${statusConfig.color} flex-shrink-0 mt-0.5`} aria-hidden="true" />
              <div>
                <h2 className={`text-lg font-bold ${statusConfig.color}`}>
                  {statusConfig.label}
                </h2>
                <p className="text-sm text-slate-600 mt-1">
                  {result.status === 'AFFORDABLE' && (
                    <>
                      Purchasing {formatCurrency(result.proposed_expense_amount, currency)} would leave your balance at{' '}
                      <strong>{formatCurrency(result.resulting_balance, currency)}</strong>, above your{' '}
                      {formatCurrency(profile?.minimum_balance_to_keep || 0, currency)} buffer.
                    </>
                  )}
                  {result.status === 'POTENTIALLY AFFORDABLE WITH TRADE-OFF' && (
                    <>
                      Purchasing {formatCurrency(result.proposed_expense_amount, currency)} would breach your buffer by{' '}
                      <strong>{formatCurrency(result.shortfall, currency)}</strong>. You would need to reduce discretionary spending by{' '}
                      <strong>{formatCurrency(result.trade_off_required, currency)}</strong> to compensate.
                    </>
                  )}
                  {result.status === 'NOT AFFORDABLE UNDER CURRENT PROJECTION' && (
                    <>
                      Purchasing {formatCurrency(result.proposed_expense_amount, currency)} would drop your balance to{' '}
                      <strong>{formatCurrency(result.resulting_balance, currency)}</strong>, creating a shortfall of{' '}
                      <strong>{formatCurrency(result.shortfall, currency)}</strong> below your buffer.
                    </>
                  )}
                  {result.status === 'INSUFFICIENT DATA' && (
                    <>Not enough historical data to make a reliable affordability assessment.</>
                  )}
                </p>
              </div>
            </div>
          </div>

          {/* Impact Breakdown */}
          <section className="card p-5" aria-labelledby="impact-title">
            <h3 id="impact-title" className="section-title mb-4">Financial Impact Breakdown</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                <p className="text-xs text-muted mb-1">Purchase Amount</p>
                <p className="text-base font-bold text-primary-dark">
                  {formatCurrency(result.proposed_expense_amount, currency)}
                </p>
              </div>
              <div className={`p-3 rounded-xl border ${result.resulting_balance >= 0 ? 'bg-green-50 border-green-100' : 'bg-red-50 border-red-100'}`}>
                <p className="text-xs text-muted mb-1">Resulting Balance</p>
                <p className={`text-base font-bold ${result.resulting_balance >= 0 ? 'text-positive' : 'text-danger'}`}>
                  {formatCurrency(result.resulting_balance, currency)}
                </p>
              </div>
              <div className={`p-3 rounded-xl border ${result.shortfall <= 0 ? 'bg-green-50 border-green-100' : 'bg-red-50 border-red-100'}`}>
                <p className="text-xs text-muted mb-1">Buffer Shortfall</p>
                <p className={`text-base font-bold ${result.shortfall <= 0 ? 'text-positive' : 'text-danger'}`}>
                  {result.shortfall <= 0 ? 'None' : formatCurrency(result.shortfall, currency)}
                </p>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                <p className="text-xs text-muted mb-1">Trade-off Needed</p>
                <p className="text-base font-bold text-primary-dark">
                  {result.trade_off_required > 0 ? formatCurrency(result.trade_off_required, currency) : 'None'}
                </p>
              </div>
            </div>
          </section>

          {/* Payment Options */}
          {result.viable_payment_options && result.viable_payment_options.length > 0 && (
            <section className="card p-5" aria-labelledby="payment-options-title">
              <h3 id="payment-options-title" className="section-title mb-1">Viable Payment Options</h3>
              <p className="text-xs text-muted mb-4">
                These installment options keep your balance above your minimum buffer.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {result.viable_payment_options.map((opt) => (
                  <div
                    key={opt.payment_option_id}
                    className="border border-border rounded-xl p-4 hover:border-primary-accent hover:bg-blue-50/20 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-semibold uppercase tracking-wide text-primary-accent">
                        {opt.payment_method.replace(/_/g, ' ')}
                      </span>
                      <span className="badge-neutral text-xs">
                        {opt.number_of_payments === 1 ? 'Full' : `${opt.number_of_payments}x`}
                      </span>
                    </div>
                    <p className="text-2xl font-bold text-primary-dark mb-1">
                      {formatCurrency(opt.payment_amount, currency)}
                    </p>
                    <p className="text-xs text-muted mb-3">
                      {opt.number_of_payments === 1 ? 'One-time payment' : `per installment`}
                    </p>
                    <div className="space-y-1.5 pt-3 border-t border-slate-100">
                      <div className="flex justify-between text-xs">
                        <span className="text-muted">Total payable</span>
                        <span className="font-medium">{formatCurrency(opt.total_payable_amount, currency)}</span>
                      </div>
                      {opt.financing_fee > 0 && (
                        <div className="flex justify-between text-xs">
                          <span className="text-muted">Financing fee</span>
                          <span className="font-medium text-warning">{formatCurrency(opt.financing_fee, currency)}</span>
                        </div>
                      )}
                      <div className="flex justify-between text-xs">
                        <span className="text-muted">First payment</span>
                        <span className="font-medium">{opt.first_payment_date}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* No payment options note */}
          {result.viable_payment_options && result.viable_payment_options.length === 0 && result.status !== 'AFFORDABLE' && (
            <div className="card p-4 bg-amber-50 border border-amber-100">
              <div className="flex items-center gap-2">
                <AlertTriangle size={16} className="text-warning" />
                <p className="text-sm text-amber-800">
                  No affordable installment plans found for this amount. All available options would breach your minimum buffer.
                </p>
              </div>
            </div>
          )}

          {/* Decision Trace */}
          <div className="text-xs text-muted bg-slate-50 rounded-xl p-4 border border-slate-100">
            <p className="font-medium text-primary-dark mb-1">Decision Trace</p>
            <p>
              Observed current available balance and projected cash flow → Evaluated upfront purchase affordability against minimum buffer constraint → Simulated installment alternatives (if upfront not affordable) → Ranked viable options to generate recommendation.
            </p>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!result && !isChecking && !checkError && (
        <div className="card p-8 text-center">
          <CreditCard size={32} className="text-muted mx-auto mb-3" />
          <h3 className="text-base font-semibold text-primary-dark mb-1">Enter a purchase amount</h3>
          <p className="text-sm text-muted max-w-md mx-auto">
            Enter any purchase amount above to see whether it's affordable, what the impact on your balance would be,
            and whether installment options are available.
          </p>
        </div>
      )}
    </div>
  );
};
