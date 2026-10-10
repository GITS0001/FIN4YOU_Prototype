import { useState, useEffect, useCallback } from 'react';
import { SlidersHorizontal, ShieldCheck, Activity } from 'lucide-react';
import { checkAffordability, runWhatIfSimulation } from '../../api/fin4youApi';

export default function WhatIfTab({ profile }) {
  const currencySymbol = profile?.currencySymbol || '₹';
  const baselineIncome = profile?.income || 75000;
  const baselineExpenses = profile?.expenses || 42200;
  const currentBalance = profile?.balance || 58480;
  const bufferFloor = profile?.buffer || 18000;

  // Simulator controls
  const [purchaseAmount, setPurchaseAmount] = useState(35000);
  const [purchaseType, setPurchaseType] = useState('full'); // 'full' or 'installment'
  const [installmentMonths, setInstallmentMonths] = useState(6);
  const [monthlyAdjustment, setMonthlyAdjustment] = useState(0);

  // Backend simulation state
  const [backendAffordability, setBackendAffordability] = useState(null);
  const [backendWhatIf, setBackendWhatIf] = useState(null);
  const [loading, setLoading] = useState(false);

  // Execute backend simulation on input change (debounced)
  const triggerSimulation = useCallback(async (amt) => {
    try {
      setLoading(true);
      const [aff, wif] = await Promise.allSettled([
        checkAffordability(amt),
        runWhatIfSimulation('add_purchase', amt),
      ]);
      if (aff.status === 'fulfilled') setBackendAffordability(aff.value);
      if (wif.status === 'fulfilled') setBackendWhatIf(wif.value);
    } catch (err) {
      console.warn('Simulation fallback mode:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      triggerSimulation(purchaseAmount);
    }, 400);
    return () => clearTimeout(timer);
  }, [purchaseAmount, triggerSimulation]);

  // Fallback local calculations if backend offline
  const effectiveMonthlyIncome = baselineIncome + monthlyAdjustment;
  const monthlyInstallmentCost = purchaseType === 'installment' ? Math.round(purchaseAmount / installmentMonths) : 0;
  const immediateCost = purchaseType === 'full' ? purchaseAmount : 0;

  const postPurchaseBalance = currentBalance - immediateCost;
  const newMonthlyExpenses = baselineExpenses + monthlyInstallmentCost;
  const newMonthlySavings = effectiveMonthlyIncome - newMonthlyExpenses;
  const newSavingsRate = effectiveMonthlyIncome > 0 ? ((newMonthlySavings / effectiveMonthlyIncome) * 100).toFixed(1) : '0.0';

  const isBufferSafe = postPurchaseBalance >= bufferFloor;
  const isMonthlyPositive = newMonthlySavings > 0;

  let decisionBadge = 'Safely Affordable';
  let decisionColor = 'text-emerald-700 bg-emerald-50 border-emerald-200/60';

  if (!isBufferSafe && purchaseType === 'full') {
    decisionColor = 'text-amber-800 bg-amber-50 border-amber-200/60';
    decisionBadge = 'Recommend Installments';
  } else if (!isMonthlyPositive) {
    decisionColor = 'text-rose-700 bg-rose-50 border-rose-200/60';
    decisionBadge = 'Not Recommended';
  }

  // Override status from backend if available
  if (backendAffordability && purchaseType === 'full') {
    if (backendAffordability.affordable_without_credit) {
      decisionBadge = 'Safely Affordable (Backend Verified)';
      decisionColor = 'text-emerald-700 bg-emerald-50 border-emerald-200/60';
    } else {
      decisionBadge = `Shortfall: ${currencySymbol}${Math.round(backendAffordability.shortfall_amount || 0)}`;
      decisionColor = 'text-amber-800 bg-amber-50 border-amber-200/60';
    }
  }

  return (
    <div className="space-y-6 sm:space-y-8 animate-fade-in pb-16 md:pb-6">
      {/* Header */}
      <div className="bg-white rounded-2xl p-5 sm:p-6 border border-gray-100 shadow-card">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-blue-50 text-[#2563EB] text-xs font-semibold border border-blue-200/60 mb-2">
          <SlidersHorizontal size={13} className="text-[#2563EB]" />
          <span>Deterministic Affordability Decision Engine</span>
        </div>
        <h2 className="text-xl sm:text-2xl font-black text-[#0B0F19] tracking-tight font-display">
          What-If Scenario & Purchase Simulator
        </h2>
        <p className="text-xs sm:text-sm text-gray-500 mt-1 max-w-xl">
          Simulate one-time purchases, installment schedules, or salary shifts before committing your money.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Simulator Controls (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl p-5 sm:p-6 border border-gray-100 shadow-card space-y-5">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-[#0B0F19] font-display">Simulate a Planned Expenditure</h3>
            {loading && <span className="text-xs text-[#2563EB] font-bold animate-pulse">Running Backend Simulation…</span>}
          </div>

          {/* Amount Slider */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label htmlFor="purchase-amount" className="text-xs font-bold text-gray-700">Planned Purchase Amount</label>
              <span className="text-lg font-black text-[#2563EB] font-display">
                {currencySymbol}{purchaseAmount.toLocaleString()}
              </span>
            </div>
            <input
              id="purchase-amount"
              type="range"
              min="5000"
              max="150000"
              step="2500"
              value={purchaseAmount}
              onChange={(e) => setPurchaseAmount(Number(e.target.value))}
              className="w-full accent-[#2563EB] cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-gray-400 mt-1">
              <span>{currencySymbol}5,000</span>
              <span>{currencySymbol}75,000</span>
              <span>{currencySymbol}1,50,000</span>
            </div>
          </div>

          {/* Payment Method Selector */}
          <div>
            <label className="text-xs font-bold text-gray-700 block mb-2">Payment Structure</label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setPurchaseType('full')}
                className={`p-3.5 rounded-xl border text-left transition-all ${
                  purchaseType === 'full'
                    ? 'border-[#2563EB] bg-blue-50/50 shadow-xs'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <div className="text-xs font-bold text-gray-900">One-Time Full Payment</div>
                <div className="text-[11px] text-gray-500 mt-0.5">Deducts immediately from balance</div>
              </button>

              <button
                type="button"
                onClick={() => setPurchaseType('installment')}
                className={`p-3.5 rounded-xl border text-left transition-all ${
                  purchaseType === 'installment'
                    ? 'border-[#2563EB] bg-blue-50/50 shadow-xs'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <div className="text-xs font-bold text-gray-900">Installment Plan</div>
                <div className="text-[11px] text-gray-500 mt-0.5">Paces out debits across months</div>
              </button>
            </div>
          </div>

          {/* Installment Term if applicable */}
          {purchaseType === 'installment' && (
            <div className="p-4 bg-gray-50/80 rounded-xl border border-gray-100">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-bold text-gray-700">Installment Duration:</span>
                <span className="text-sm font-bold text-[#2563EB]">{installmentMonths} Months ({currencySymbol}{monthlyInstallmentCost.toLocaleString()} / mo)</span>
              </div>
              <div className="flex gap-2">
                {[3, 6, 9, 12].map((m) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => setInstallmentMonths(m)}
                    className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${
                      installmentMonths === m
                        ? 'bg-[#2563EB] text-white shadow-xs'
                        : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    {m} mo
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Income Shift Slider */}
          <div className="pt-3 border-t border-gray-100">
            <div className="flex justify-between items-center mb-1.5">
              <label htmlFor="income-adjustment" className="text-xs font-bold text-gray-700">Salary Change / Variance</label>
              <span className={`text-xs font-bold ${monthlyAdjustment >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                {monthlyAdjustment >= 0 ? '+' : ''}{currencySymbol}{monthlyAdjustment.toLocaleString()} / mo
              </span>
            </div>
            <input
              id="income-adjustment"
              type="range"
              min="-15000"
              max="25000"
              step="2500"
              value={monthlyAdjustment}
              onChange={(e) => setMonthlyAdjustment(Number(e.target.value))}
              className="w-full accent-[#2563EB] cursor-pointer"
            />
          </div>
        </div>

        {/* Real-time Decision Output (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl p-5 sm:p-6 border border-gray-100 shadow-card flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Engine Verification</span>
              <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${decisionColor}`}>
                {decisionBadge}
              </span>
            </div>

            <div className="text-xl font-black text-[#0B0F19] font-display mb-1">
              Impact Assessment
            </div>
            <p className="text-xs text-gray-500 mb-6 leading-relaxed">
              Evaluating candidate transaction constraints against your priority thresholds.
            </p>

            <div className="space-y-4">
              <div className="p-3.5 bg-gray-50 rounded-xl border border-gray-100 flex items-center justify-between">
                <div>
                  <span className="text-[10px] uppercase font-bold text-gray-400 block">Post-Purchase Balance</span>
                  <span className="text-lg font-black text-[#0B0F19]">
                    {currencySymbol}{backendAffordability ? Math.round(backendAffordability.resulting_available_balance).toLocaleString() : postPurchaseBalance.toLocaleString()}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] uppercase font-bold text-gray-400 block">Safety Floor</span>
                  <span className="text-sm font-bold text-emerald-600">{currencySymbol}{bufferFloor.toLocaleString()}</span>
                </div>
              </div>

              <div className="p-3.5 bg-gray-50 rounded-xl border border-gray-100 flex items-center justify-between">
                <div>
                  <span className="text-[10px] uppercase font-bold text-gray-400 block">Revised Monthly Savings</span>
                  <span className="text-lg font-black text-[#2563EB]">{currencySymbol}{newMonthlySavings.toLocaleString()}</span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] uppercase font-bold text-gray-400 block">Savings Rate</span>
                  <span className={`text-sm font-bold ${Number(newSavingsRate) >= 20 ? 'text-emerald-600' : 'text-amber-600'}`}>
                    {newSavingsRate}%
                  </span>
                </div>
              </div>

              {/* Viable Payment Options from Backend */}
              {backendAffordability?.viable_payment_options && backendAffordability.viable_payment_options.length > 0 && (
                <div className="p-3 bg-blue-50/60 rounded-xl border border-blue-100 text-xs">
                  <div className="font-bold text-[#2563EB] text-[11px] uppercase mb-1 flex items-center gap-1">
                    <Activity size={13} />
                    <span>Viable Payment Options Found ({backendAffordability.viable_payment_options.length})</span>
                  </div>
                  <div className="space-y-1">
                    {backendAffordability.viable_payment_options.map((opt, idx) => (
                      <div key={idx} className="flex justify-between text-gray-700 text-[11px]">
                        <span>{opt.payment_method} ({opt.number_of_payments}x)</span>
                        <span className="font-bold">{currencySymbol}{opt.payment_amount}/mo</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Deterministic What-If Impact Engine Summary */}
              {backendWhatIf?.impact && (
                <div className="p-3 bg-emerald-50/60 rounded-xl border border-emerald-100 text-xs">
                  <span className="text-[10px] font-bold text-emerald-800 uppercase block mb-1">Backend Impact Model</span>
                  <div className="text-[11px] text-emerald-900">
                    Net Runway Impact: <strong className="font-bold">{backendWhatIf.impact.runway_impact_days || 0} days</strong>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-gray-100">
            <div className="flex items-start gap-2.5 text-xs text-gray-600 leading-relaxed bg-blue-50/60 p-3 rounded-xl border border-blue-100">
              <ShieldCheck size={16} className="text-[#2563EB] flex-shrink-0 mt-0.5" />
              <span>
                {isBufferSafe
                  ? `Your reserve buffer of ${currencySymbol}${bufferFloor.toLocaleString()} remains 100% safeguarded under this plan.`
                  : `Full payment dips ${currencySymbol}${(bufferFloor - postPurchaseBalance).toLocaleString()} into your emergency buffer. Consider 6-month installments to protect capital.`}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
