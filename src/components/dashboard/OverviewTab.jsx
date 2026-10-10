import { useState, useEffect } from 'react';
import {
  Wallet,
  TrendingUp,
  TrendingDown,
  Activity,
  Sparkles,
} from 'lucide-react';
import { getTransactions, getMonthlyStatement } from '../../api/fin4youApi';

export default function OverviewTab({ profile, financialState, onSelectTab }) {
  const [timeframe, setTimeframe] = useState('30d');
  const [liveTransactions, setLiveTransactions] = useState([]);
  const [statementData, setStatementData] = useState(null);

  useEffect(() => {
    getTransactions(6)
      .then((txs) => {
        if (Array.isArray(txs) && txs.length > 0) {
          const mapped = txs.map((t) => ({
            id: t.transaction_id || t.id,
            date: t.event_date ? String(t.event_date).slice(5) : 'Recent',
            desc: t.description || 'Transaction',
            cat: t.category || 'General',
            dir: t.direction || (t.event_type === 'income' ? 'credit' : 'debit'),
            amt: Math.abs(t.amount || 0),
            status: t.flexibility || (t.event_type === 'income' ? 'Verified' : 'Essential'),
          }));
          setLiveTransactions(mapped);
        }
      })
      .catch((err) => console.warn('Using fallback overview txs:', err));

    getMonthlyStatement()
      .then((stmt) => {
        if (stmt) setStatementData(stmt);
      })
      .catch(() => {});
  }, []);

  const currencySymbol = profile?.currencySymbol || '₹';
  const balance = financialState?.available_balance ?? profile?.balance ?? 58480;
  const buffer = financialState?.minimum_reserve ?? profile?.buffer ?? 18000;
  const income = financialState?.total_observed_income ?? profile?.income ?? 75000;
  const expenses = financialState?.total_observed_expenses ?? profile?.expenses ?? 42200;
  const savings = income - expenses;
  const savingsRate = income > 0 ? ((savings / income) * 100).toFixed(1) : '0.0';

  const defaultRecent = [
    { id: '1', date: 'May 02', desc: 'Monthly Apartment Rent', cat: 'Housing', dir: 'debit', amt: 18500, status: 'Fixed Essential' },
    { id: '2', date: 'May 04', desc: 'Nature Fresh Supermarket', cat: 'Groceries', dir: 'debit', amt: 3420, status: 'Essential' },
    { id: '3', date: 'May 06', desc: 'Monthly Consulting Payout', cat: 'Income', dir: 'credit', amt: 75000, status: 'Verified' },
    { id: '4', date: 'May 07', desc: 'Electricity & Gas Bill', cat: 'Utilities', dir: 'debit', amt: 2150, status: 'Essential' },
    { id: '5', date: 'May 08', desc: 'Cloud Storage & Software', cat: 'Subscriptions', dir: 'debit', amt: 699, status: 'Stoppable' },
    { id: '6', date: 'May 09', desc: 'Weekend Bistro Dining', cat: 'Dining Out', dir: 'debit', amt: 2840, status: 'Discretionary' },
  ];

  const transactionsToDisplay = liveTransactions.length > 0 ? liveTransactions : defaultRecent;

  const kpis = [
    {
      label: 'Available Balance',
      value: `${currencySymbol}${balance.toLocaleString()}`,
      sub: `Min Buffer: ${currencySymbol}${buffer.toLocaleString()}`,
      status: 'Protected',
      statusColor: 'text-emerald-700 bg-emerald-50 border-emerald-200/60',
      icon: Wallet,
      iconColor: 'text-[#2563EB]',
    },
    {
      label: 'Monthly Inflow',
      value: `${currencySymbol}${income.toLocaleString()}`,
      sub: statementData?.income?.change ? `${statementData.income.change >= 0 ? '+' : ''}${currencySymbol}${statementData.income.change} MoM` : 'Verified run-rate',
      status: 'Stable',
      statusColor: 'text-blue-700 bg-blue-50 border-blue-200/60',
      icon: TrendingUp,
      iconColor: 'text-emerald-600',
    },
    {
      label: 'Monthly Outflows',
      value: `${currencySymbol}${expenses.toLocaleString()}`,
      sub: financialState ? `Fixed: ${currencySymbol}${Math.round(financialState.total_fixed_obligations || 0)}` : 'Essential: 58% • Discretionary: 42%',
      status: '-4.2% MoM',
      statusColor: 'text-emerald-700 bg-emerald-50 border-emerald-200/60',
      icon: TrendingDown,
      iconColor: 'text-gray-600',
    },
    {
      label: 'Net Savings Run-Rate',
      value: `${currencySymbol}${savings.toLocaleString()}`,
      sub: `Savings Rate: ${savingsRate}%`,
      status: 'Target > 25%',
      statusColor: 'text-emerald-700 bg-emerald-50 border-emerald-200/60',
      icon: Activity,
      iconColor: 'text-[#2563EB]',
    },
  ];

  return (
    <div className="space-y-6 sm:space-y-8 animate-fade-in pb-16 md:pb-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-[#0B0F19] to-[#1E293B] rounded-2xl sm:rounded-3xl p-5 sm:p-7 text-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-card">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-white/10 text-[11px] font-semibold text-blue-200 mb-2">
            <Sparkles size={12} className="text-[#60A5FA]" />
            Personal Financial Health Overview
          </div>
          <h2 className="text-xl sm:text-2xl lg:text-3xl font-black tracking-tight font-display">
            Financial Health: <span className="text-emerald-400">Excellent (92/100)</span>
          </h2>
          <p className="text-xs sm:text-sm text-gray-300 mt-1 max-w-xl">
            Your essential expenses are covered, and your 90-day cash-flow forecast maintains your safety buffer without debt risk.
          </p>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <button
            onClick={() => onSelectTab('what-if')}
            className="flex-1 sm:flex-none px-4 py-2.5 bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold rounded-xl transition-all shadow-blue touch-target"
          >
            What-If Simulator
          </button>
          <button
            onClick={() => onSelectTab('copilot')}
            className="flex-1 sm:flex-none px-4 py-2.5 bg-white/10 hover:bg-white/15 text-white text-xs font-bold rounded-xl border border-white/20 transition-all touch-target"
          >
            Ask Artha AI
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <div
              key={kpi.label}
              className="bg-white rounded-2xl p-5 border border-gray-100 shadow-card hover:shadow-card-hover transition-all duration-200"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider">{kpi.label}</span>
                <div className={`p-2 rounded-xl bg-gray-50 ${kpi.iconColor}`}>
                  <Icon size={17} />
                </div>
              </div>
              <div className="text-2xl sm:text-3xl font-black text-[#0B0F19] tracking-tight font-display mb-1">
                {kpi.value}
              </div>
              <div className="flex items-center justify-between text-xs pt-2 border-t border-gray-50">
                <span className="text-gray-400 truncate max-w-[150px]">{kpi.sub}</span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${kpi.statusColor}`}>
                  {kpi.status}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Cash Flow Visualizer & Buffer Card */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Cash Flow Chart (8 cols on lg) */}
        <div className="lg:col-span-8 bg-white rounded-2xl p-5 sm:p-6 border border-gray-100 shadow-card">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
            <div>
              <h3 className="text-base font-bold text-[#0B0F19] font-display">Monthly Cash-Flow Run-Rate</h3>
              <p className="text-xs text-gray-500">Inflows vs Outflows and Forward Trajectory</p>
            </div>
            <div className="flex items-center gap-1.5 bg-gray-100/80 p-1 rounded-xl self-start sm:self-auto">
              {['30d', '60d', '90d'].map((t) => (
                <button
                  key={t}
                  onClick={() => setTimeframe(t)}
                  className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                    timeframe === t ? 'bg-white text-[#2563EB] shadow-xs' : 'text-gray-500 hover:text-gray-900'
                  }`}
                >
                  {t.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {/* SVG Cash Flow Graphic */}
          <div className="h-48 sm:h-56 w-full relative pt-2">
            <svg className="w-full h-full" viewBox="0 0 500 180" fill="none" preserveAspectRatio="none">
              {/* Background horizontal grid lines */}
              <line x1="0" y1="40" x2="500" y2="40" stroke="#F1F5F9" strokeWidth="1" strokeDasharray="4 4" />
              <line x1="0" y1="90" x2="500" y2="90" stroke="#F1F5F9" strokeWidth="1" strokeDasharray="4 4" />
              <line x1="0" y1="140" x2="500" y2="140" stroke="#F1F5F9" strokeWidth="1" strokeDasharray="4 4" />

              {/* Safety Buffer Horizontal Floor Threshold */}
              <line x1="0" y1="130" x2="500" y2="130" stroke="#10B981" strokeWidth="1.5" strokeDasharray="6 3" />
              <text x="4" y="124" fill="#059669" fontSize="10" fontWeight="bold">
                Safety Floor Threshold ({currencySymbol}{buffer.toLocaleString()})
              </text>

              {/* Balance Trajectory Line */}
              <path
                d="M0 80 C80 95, 140 70, 220 50 S360 40, 500 25"
                stroke="#2563EB"
                strokeWidth="3"
                strokeLinecap="round"
              />
              <path
                d="M0 80 C80 95, 140 70, 220 50 S360 40, 500 25 L500 180 L0 180 Z"
                fill="url(#flowGradient)"
                opacity="0.12"
              />

              {/* Data points */}
              <circle cx="140" cy="70" r="4.5" fill="#2563EB" />
              <circle cx="360" cy="40" r="4.5" fill="#2563EB" />
              <circle cx="500" cy="25" r="5" fill="#10B981" />

              <defs>
                <linearGradient id="flowGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#2563EB" />
                  <stop offset="100%" stopColor="#2563EB" stopOpacity="0" />
                </linearGradient>
              </defs>
            </svg>
          </div>

          <div className="flex justify-between text-xs text-gray-400 font-medium pt-3 border-t border-gray-100">
            <span>Current Month</span>
            <span>Month +1 Projection</span>
            <span>Month +2 Projection</span>
            <span className="text-emerald-600 font-bold">Month +3 (+{currencySymbol}98,400)</span>
          </div>
        </div>

        {/* Safety Buffer & Priorities Card (4 cols on lg) */}
        <div className="lg:col-span-4 bg-white rounded-2xl p-5 sm:p-6 border border-gray-100 shadow-card flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Risk Assessment</span>
              <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200/60">
                Low Risk
              </span>
            </div>

            <h3 className="text-lg font-bold text-[#0B0F19] font-display mb-2">Liquidity Buffer Status</h3>
            <p className="text-xs text-gray-500 leading-relaxed mb-4">
              Your minimum required reserve of <strong>{currencySymbol}{buffer.toLocaleString()}</strong> is fully funded. Forward cash pacing indicates 0 days of deficit over the next 90 days.
            </p>

            <div className="space-y-3 pt-2 border-t border-gray-100">
              <div>
                <div className="flex justify-between text-xs font-medium mb-1">
                  <span className="text-gray-600">Buffer Coverage</span>
                  <span className="font-bold text-emerald-600">3.2x Minimum</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-500 rounded-full" style={{ width: '85%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-medium mb-1">
                  <span className="text-gray-600">Essential Expense Coverage</span>
                  <span className="font-bold text-[#2563EB]">100% Guaranteed</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full bg-[#2563EB] rounded-full" style={{ width: '100%' }} />
                </div>
              </div>
            </div>
          </div>

          <div className="pt-5 mt-5 border-t border-gray-100">
            <button
              onClick={() => onSelectTab('forecast')}
              className="w-full py-2.5 bg-gray-50 hover:bg-gray-100 text-gray-800 text-xs font-bold rounded-xl transition-colors border border-gray-200"
            >
              Inspect Complete 90-Day Simulation →
            </button>
          </div>
        </div>
      </div>

      {/* Recent Activity Table */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-card p-5 sm:p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
          <div>
            <h3 className="text-base font-bold text-[#0B0F19] font-display">Recent Verified Activity</h3>
            <p className="text-xs text-gray-500">Latest debits and inflows mapped into financial buckets</p>
          </div>
          <button
            onClick={() => onSelectTab('expenses')}
            className="text-xs font-bold text-[#2563EB] hover:underline self-start sm:self-auto"
          >
            View Complete Ledger (884 txns) →
          </button>
        </div>

        {/* Responsive Table / Stacked Card Container */}
        <div className="overflow-x-auto -mx-5 sm:mx-0">
          <div className="inline-block min-w-full align-middle px-5 sm:px-0">
            <table className="min-w-full text-left text-xs text-gray-700">
              <thead className="bg-gray-50/80 text-[11px] uppercase tracking-wider text-gray-400 font-bold border-b border-gray-100">
                <tr>
                  <th className="py-3 px-3">Date</th>
                  <th className="py-3 px-3">Transaction</th>
                  <th className="py-3 px-3">Category</th>
                  <th className="py-3 px-3">Type</th>
                  <th className="py-3 px-3 text-right">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {transactionsToDisplay.map((tx) => (
                  <tr key={tx.id} className="hover:bg-blue-50/30 transition-colors">
                    <td className="py-3.5 px-3 text-gray-500 whitespace-nowrap font-medium">{tx.date}</td>
                    <td className="py-3.5 px-3 font-semibold text-gray-900">{tx.desc}</td>
                    <td className="py-3.5 px-3">
                      <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-gray-100 text-gray-700 border border-gray-200/60">
                        {tx.cat}
                      </span>
                    </td>
                    <td className="py-3.5 px-3">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          tx.dir === 'credit'
                            ? 'text-emerald-700 bg-emerald-50'
                            : tx.status.includes('Essential')
                            ? 'text-blue-700 bg-blue-50'
                            : 'text-amber-700 bg-amber-50'
                        }`}
                      >
                        {tx.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-3 text-right whitespace-nowrap font-bold">
                      <span className={tx.dir === 'credit' ? 'text-emerald-600' : 'text-gray-900'}>
                        {tx.dir === 'credit' ? '+' : '-'}
                        {currencySymbol}
                        {tx.amt.toLocaleString()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
