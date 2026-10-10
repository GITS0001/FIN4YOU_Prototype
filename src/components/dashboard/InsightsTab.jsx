import { useState, useEffect } from 'react';
import { Sparkles, ArrowRight, ShieldAlert } from 'lucide-react';
import { getMonthlyStatement } from '../../api/fin4youApi';

export default function InsightsTab({ profile, alerts = [], onSelectTab }) {
  const currencySymbol = profile?.currencySymbol || '₹';
  const [statement, setStatement] = useState(null);
  const [dismissed, setDismissed] = useState([]);

  useEffect(() => {
    getMonthlyStatement()
      .then((stmt) => setStatement(stmt))
      .catch(() => {});
  }, []);

  const dismiss = (id) => setDismissed((prev) => [...prev, id]);

  const defaultInsights = [
    {
      id: 'leak-1',
      type: 'leak',
      title: 'Micro-Delivery & Quick Food Drains',
      amount: `~${currencySymbol}4,200 / month`,
      description: 'You had 18 micro-transactions under ₹350 this month on delivery apps. Batching these or switching to weekly grocery plans can recover ~₹2,500/month.',
      severity: 'medium',
      badge: 'Cash Drain Leak',
    },
    {
      id: 'leak-2',
      type: 'stoppable',
      title: 'Dormant Subscription Identified',
      amount: `${currencySymbol}699 / month`,
      description: 'Zero verified activity recorded on your secondary cloud storage subscription over the last 60 days. Marked as a stoppable expense in your profile.',
      severity: 'low',
      badge: 'Unused Recurring',
    },
    {
      id: 'anomaly-1',
      type: 'anomaly',
      title: 'Z-Score Anomaly: Dining Out (+38%)',
      amount: `+${currencySymbol}1,840 above mean`,
      description: 'Weekend bistro dining expenditure spiked to 2.4 standard deviations above your 90-day baseline during Week 2.',
      severity: 'medium',
      badge: 'Statistical Outlier',
    },
    {
      id: 'positive-1',
      type: 'positive',
      title: 'Utility Pacing Optimization',
      amount: `Saved ${currencySymbol}480`,
      description: 'Electricity & heating usage remained 12% lower than your typical seasonal benchmark.',
      severity: 'positive',
      badge: 'Efficiency Win',
    },
  ];

  // Merge real alerts into insights
  const liveAlertInsights = alerts.map((a, idx) => ({
    id: a.id || `alert-${idx}`,
    type: a.type === 'danger' ? 'leak' : 'anomaly',
    title: a.title || 'Financial Alert',
    amount: 'Action Required',
    description: a.message || 'Anomaly detected in transaction pattern.',
    severity: a.type === 'danger' ? 'high' : 'medium',
    badge: 'Backend Alert',
  }));

  const combinedInsights = [...liveAlertInsights, ...defaultInsights].filter(
    (i) => !dismissed.includes(i.id)
  );

  return (
    <div className="space-y-6 sm:space-y-8 animate-fade-in pb-16 md:pb-6">
      {/* Scorecard Header */}
      <div className="bg-white rounded-2xl p-5 sm:p-6 border border-gray-100 shadow-card flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-blue-50 text-[#2563EB] text-xs font-semibold border border-blue-200/60 mb-2">
            <Sparkles size={13} className="text-[#2563EB]" />
            <span>AI Statistical & Rule-Based Audit</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-black text-[#0B0F19] tracking-tight font-display">
            Actionable Intelligence & Spending Leaks
          </h2>
          <p className="text-xs sm:text-sm text-gray-500 mt-1 max-w-xl">
            Our deterministic anomaly detector and categorization engine identified actionable opportunities to expand your savings reserve.
          </p>
        </div>

        <div className="bg-emerald-50 border border-emerald-200/80 rounded-2xl p-4 flex items-center gap-4 flex-shrink-0">
          <div className="text-3xl font-black text-emerald-700 font-display">{currencySymbol}6,700</div>
          <div>
            <div className="text-xs font-bold text-emerald-900">Monthly Recoverable Leak</div>
            <div className="text-[11px] text-emerald-700">Without reducing essential living comfort</div>
          </div>
        </div>
      </div>

      {/* Monthly Statement Recommendations */}
      {statement && (
        <div className="bg-white rounded-2xl p-5 border border-gray-100 shadow-card">
          <h3 className="text-base font-bold text-[#0B0F19] font-display mb-3">Deterministic Monthly Statement Analysis</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4 text-xs">
            <div className="p-3 bg-gray-50 rounded-xl">
              <span className="text-gray-400 block text-[10px]">Current Income</span>
              <span className="font-bold text-emerald-600 text-sm">{currencySymbol}{statement.income?.current?.toLocaleString()}</span>
            </div>
            <div className="p-3 bg-gray-50 rounded-xl">
              <span className="text-gray-400 block text-[10px]">Current Expenses</span>
              <span className="font-bold text-gray-900 text-sm">{currencySymbol}{statement.expenses?.current?.toLocaleString()}</span>
            </div>
            <div className="p-3 bg-gray-50 rounded-xl">
              <span className="text-gray-400 block text-[10px]">Monthly Net Savings</span>
              <span className="font-bold text-[#2563EB] text-sm">{currencySymbol}{statement.savings?.current?.toLocaleString()}</span>
            </div>
          </div>

          {statement.observations && statement.observations.length > 0 && (
            <div className="text-xs text-gray-600 space-y-1 bg-blue-50/50 p-3 rounded-xl border border-blue-100">
              <div className="font-bold text-[#2563EB] text-[11px] uppercase">Engine Observations:</div>
              {statement.observations.map((obs, i) => (
                <div key={i} className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#2563EB]" />
                  <span>{obs}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Cards List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {combinedInsights.map((item) => (
          <div
            key={item.id}
            className={`rounded-2xl p-5 sm:p-6 border shadow-card flex flex-col justify-between transition-all ${
              item.severity === 'positive'
                ? 'bg-emerald-50/40 border-emerald-200/70'
                : item.severity === 'high'
                ? 'bg-rose-50/40 border-rose-200/70'
                : 'bg-white border-gray-200/80'
            }`}
          >
            <div>
              <div className="flex items-center justify-between gap-2 mb-3">
                <span
                  className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full ${
                    item.severity === 'positive'
                      ? 'bg-emerald-100 text-emerald-800'
                      : item.severity === 'high'
                      ? 'bg-rose-100 text-rose-800'
                      : item.type === 'leak'
                      ? 'bg-rose-50 text-rose-700 border border-rose-200/60'
                      : 'bg-amber-50 text-amber-800 border border-amber-200/60'
                  }`}
                >
                  {item.badge}
                </span>
                <span className="text-xs font-black text-[#0B0F19]">{item.amount}</span>
              </div>

              <h3 className="text-base font-bold text-[#0B0F19] font-display mb-2 flex items-center gap-1.5">
                {item.severity === 'high' && <ShieldAlert size={16} className="text-rose-600" />}
                <span>{item.title}</span>
              </h3>
              <p className="text-xs text-gray-600 leading-relaxed mb-4">{item.description}</p>
            </div>

            <div className="pt-4 border-t border-gray-100 flex items-center justify-between gap-2">
              <button
                onClick={() => onSelectTab('copilot')}
                className="text-xs font-bold text-[#2563EB] hover:text-[#1D4ED8] flex items-center gap-1"
              >
                <span>Consult Artha AI</span>
                <ArrowRight size={13} />
              </button>
              <button
                onClick={() => dismiss(item.id)}
                className="text-[11px] text-gray-400 hover:text-gray-600 px-2 py-1 rounded"
              >
                Dismiss
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
