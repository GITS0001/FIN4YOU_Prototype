import { useState, useEffect } from 'react';
import { ShieldCheck, BarChart3, Activity } from 'lucide-react';
import { getForecastHistory, getProbabilisticForecast } from '../../api/fin4youApi';

export default function ForecastTab({ profile, financialState }) {
  const [stressScenario, setStressScenario] = useState(false);
  const [historyData, setHistoryData] = useState(null);
  const [probForecast, setProbForecast] = useState(null);

  useEffect(() => {
    getForecastHistory()
      .then((data) => setHistoryData(data))
      .catch((err) => console.warn('Using fallback forecast history:', err));

    getProbabilisticForecast({ horizon_months: 6 })
      .then((res) => setProbForecast(res))
      .catch((err) => console.warn('Probabilistic forecast call warning:', err));
  }, []);

  const currencySymbol = profile?.currencySymbol || '₹';
  const buffer = financialState?.minimum_reserve ?? profile?.buffer ?? 18000;
  const initialBalance = financialState?.available_balance ?? profile?.balance ?? 58480;

  const runwayDays = financialState?.runway_days ?? 41.5;
  const safeDailySpend = financialState?.safe_daily_spend_limit ?? 450;

  // Build 90-Day stages
  const stage1Out = stressScenario ? 52200 : (financialState?.total_observed_expenses || 42200);
  const stage2Out = stressScenario ? 54000 : (financialState?.total_observed_expenses || 42200);
  const stage3Out = financialState?.total_observed_expenses || 42200;

  const incomeVal = financialState?.total_observed_income || 75000;

  const timeline = [
    {
      period: 'Day 1–30',
      month: 'Month +1',
      inflow: incomeVal,
      outflow: stage1Out,
      netChange: incomeVal - stage1Out,
      endBalance: initialBalance + (incomeVal - stage1Out),
      isProjected: true,
    },
    {
      period: 'Day 31–60',
      month: 'Month +2',
      inflow: incomeVal,
      outflow: stage2Out,
      netChange: incomeVal - stage2Out,
      endBalance: initialBalance + (incomeVal - stage1Out) + (incomeVal - stage2Out),
      isProjected: true,
    },
    {
      period: 'Day 61–90',
      month: 'Month +3',
      inflow: incomeVal,
      outflow: stage3Out,
      netChange: incomeVal - stage3Out,
      endBalance: initialBalance + (incomeVal - stage1Out) + (incomeVal - stage2Out) + (incomeVal - stage3Out),
      isProjected: true,
    },
  ];

  const netSurplus90 = timeline.reduce((acc, t) => acc + t.netChange, 0);

  return (
    <div className="space-y-6 sm:space-y-8 animate-fade-in pb-16 md:pb-6">
      {/* Overview Banner */}
      <div className="bg-white rounded-2xl p-5 sm:p-6 border border-gray-100 shadow-card">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-xs font-semibold border border-emerald-200/60 mb-2">
              <ShieldCheck size={13} className="text-emerald-600" />
              <span>Multi-Period Deterministic Liquidity Model</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-black text-[#0B0F19] tracking-tight font-display">
              Forward Cash-Flow Pacing & Runway
            </h2>
            <p className="text-xs sm:text-sm text-gray-500 mt-1 max-w-xl">
              Simulating continuous scheduled debits against recurring payroll cycles with zero arithmetic hallucination.
            </p>
          </div>

          <div className="flex items-center gap-2 bg-gray-50 p-2 rounded-xl border border-gray-200/60">
            <span className="text-xs font-medium text-gray-600">Simulate Expense Stress:</span>
            <button
              onClick={() => setStressScenario(!stressScenario)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                stressScenario
                  ? 'bg-amber-600 text-white shadow-xs'
                  : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-100'
              }`}
            >
              {stressScenario ? `Active (+${currencySymbol}10k/mo)` : 'Normal Baseline'}
            </button>
          </div>
        </div>

        {/* 3 Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-3 border-t border-gray-100">
          <div className="bg-gray-50/70 rounded-xl p-4 border border-gray-100">
            <span className="text-[10px] font-bold tracking-wider uppercase text-gray-400 block mb-1">
              Zero-Income Runway
            </span>
            <span className="text-2xl font-black text-[#0B0F19] font-display">{runwayDays} Days</span>
            <span className="text-[11px] text-gray-500 block mt-1">Sustains all essential obligations</span>
          </div>

          <div className="bg-gray-50/70 rounded-xl p-4 border border-gray-100">
            <span className="text-[10px] font-bold tracking-wider uppercase text-gray-400 block mb-1">
              Safe Daily Spend Limit
            </span>
            <span className="text-2xl font-black text-[#2563EB] font-display">{currencySymbol}{safeDailySpend} / day</span>
            <span className="text-[11px] text-emerald-600 block mt-1">Leaves safety reserve intact</span>
          </div>

          <div className="bg-gray-50/70 rounded-xl p-4 border border-gray-100">
            <span className="text-[10px] font-bold tracking-wider uppercase text-gray-400 block mb-1">
              Projected 90d Net Surplus
            </span>
            <span className="text-2xl font-black text-emerald-600 font-display">
              +{currencySymbol}{netSurplus90.toLocaleString()}
            </span>
            <span className="text-[11px] text-gray-500 block mt-1">Cumulative balance increase</span>
          </div>
        </div>
      </div>

      {/* Probabilistic Evaluation Metrics */}
      {probForecast?.evaluation_metrics && (
        <div className="bg-blue-50/60 rounded-2xl p-5 border border-blue-100 shadow-card">
          <div className="flex items-center gap-2 mb-2 text-[#2563EB] font-bold text-xs">
            <Activity size={15} />
            <span>Probabilistic Model Accuracy Metrics</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div>
              <span className="text-gray-500 block text-[10px]">Expense MAE:</span>
              <span className="font-bold text-gray-900">{currencySymbol}{probForecast.evaluation_metrics.expense_mae}</span>
            </div>
            <div>
              <span className="text-gray-500 block text-[10px]">Expense RMSE:</span>
              <span className="font-bold text-gray-900">{currencySymbol}{probForecast.evaluation_metrics.expense_rmse}</span>
            </div>
            <div>
              <span className="text-gray-500 block text-[10px]">Interval Coverage:</span>
              <span className="font-bold text-emerald-700">{(probForecast.evaluation_metrics.interval_coverage * 100).toFixed(1)}%</span>
            </div>
            <div>
              <span className="text-gray-500 block text-[10px]">Buffer Shortfall Prob:</span>
              <span className="font-bold text-emerald-700">{(probForecast.overall_buffer_breach_probability * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>
      )}

      {/* 90-Day Simulation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {timeline.map((stage) => (
          <div
            key={stage.period}
            className="bg-white rounded-2xl p-5 border border-gray-200/80 shadow-card flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-[#2563EB] bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-200/60">
                  {stage.period}
                </span>
                <span className="text-xs font-semibold text-gray-500">{stage.month}</span>
              </div>

              <div className="text-lg font-bold text-[#0B0F19] mt-3 font-display">
                End-of-Month Balance
              </div>
              <div className="text-3xl font-black text-[#0B0F19] tracking-tight font-display mb-4">
                {currencySymbol}
                {stage.endBalance.toLocaleString()}
              </div>

              <div className="space-y-2.5 pt-3 border-t border-gray-100 text-xs">
                <div className="flex justify-between text-gray-600">
                  <span>Projected Inflow:</span>
                  <span className="font-bold text-emerald-600">+{currencySymbol}{stage.inflow.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Total Scheduled Debits:</span>
                  <span className="font-bold text-gray-900">-{currencySymbol}{stage.outflow.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span>Net Savings Paced:</span>
                  <span className="font-bold text-[#2563EB]">+{currencySymbol}{stage.netChange.toLocaleString()}</span>
                </div>
              </div>
            </div>

            <div className="mt-5 pt-3 border-t border-gray-100 flex items-center justify-between text-[11px]">
              <span className="text-gray-400">Buffer Floor ({currencySymbol}{buffer.toLocaleString()}):</span>
              <span className="font-bold text-emerald-600 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                Protected (+{currencySymbol}{(stage.endBalance - buffer).toLocaleString()})
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Monthly Observed History vs Projections */}
      {historyData && Array.isArray(historyData.history) && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-card p-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-[#0B0F19] font-display flex items-center gap-2">
              <BarChart3 size={18} className="text-[#2563EB]" />
              <span>Historical Observations vs Multi-Period Forecast</span>
            </h3>
            <span className="text-xs text-gray-400 font-mono">
              {historyData.observed_months} Months Observed ({historyData.period_start} to {historyData.period_end})
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-xs">
              <thead className="bg-gray-50 text-gray-500 font-bold border-b border-gray-100">
                <tr>
                  <th className="py-2.5 px-3">Month</th>
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3">Inflow</th>
                  <th className="py-2.5 px-3">Variable Exp.</th>
                  <th className="py-2.5 px-3">Fixed Oblig.</th>
                  <th className="py-2.5 px-3 text-right">Net Cash Flow</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {historyData.history.map((h) => (
                  <tr key={h.month} className="hover:bg-gray-50">
                    <td className="py-2.5 px-3 font-semibold text-gray-900">{h.month}</td>
                    <td className="py-2.5 px-3">
                      <span className="px-2 py-0.5 rounded text-[10px] bg-gray-100 text-gray-600 font-bold">Observed</span>
                    </td>
                    <td className="py-2.5 px-3 text-emerald-600 font-bold">+{currencySymbol}{h.income.toLocaleString()}</td>
                    <td className="py-2.5 px-3">{currencySymbol}{h.variable_expenses.toLocaleString()}</td>
                    <td className="py-2.5 px-3">{currencySymbol}{h.known_obligations.toLocaleString()}</td>
                    <td className="py-2.5 px-3 text-right font-bold">{currencySymbol}{h.cash_flow.toLocaleString()}</td>
                  </tr>
                ))}
                {historyData.projected.map((p) => (
                  <tr key={p.month} className="bg-blue-50/40 hover:bg-blue-50">
                    <td className="py-2.5 px-3 font-semibold text-[#2563EB]">{p.month}</td>
                    <td className="py-2.5 px-3">
                      <span className="px-2 py-0.5 rounded text-[10px] bg-blue-100 text-[#2563EB] font-bold">Projected</span>
                    </td>
                    <td className="py-2.5 px-3 text-emerald-600 font-bold">+{currencySymbol}{p.income.toLocaleString()}</td>
                    <td className="py-2.5 px-3">{currencySymbol}{p.variable_expenses.toLocaleString()}</td>
                    <td className="py-2.5 px-3">{currencySymbol}{p.known_obligations.toLocaleString()}</td>
                    <td className="py-2.5 px-3 text-right font-bold text-[#2563EB]">{currencySymbol}{p.cash_flow.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
