import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { MonthlyHistoryResponse, FinancialProfile } from '../../types';
import { formatCurrency, formatCurrencyCompact } from '../../utils/format';
import { ChartSkeleton } from '../shared/LoadingSkeleton';

interface ForecastChartProps {
  history: MonthlyHistoryResponse | null;
  profile: FinancialProfile | null;
  isLoading: boolean;
}

const CustomTooltip = ({
  active,
  payload,
  label,
  currency,
}: {
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string }>;
  label?: string;
  currency: string;
}) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-border rounded-lg px-3 py-2.5 shadow-dropdown">
        <p className="text-xs font-semibold text-muted mb-1.5">{label}</p>
        {payload.map((entry) => (
          <div key={entry.name} className="flex items-center justify-between gap-4">
            <span className="text-xs text-muted capitalize">{entry.name}</span>
            <span className="text-xs font-semibold" style={{ color: entry.color }}>
              {formatCurrency(entry.value, currency)}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export const ForecastChart: React.FC<ForecastChartProps> = ({
  history,
  profile,
  isLoading,
}) => {
  if (isLoading) return <ChartSkeleton height="h-72" />;
  if (!history || !profile || history.history.length === 0) return null;

  const currency = profile.home_currency;

  // Build chart data combining historical (state) and projected (prediction)
  const chartData = history.history.map(pt => ({
    period: pt.month,
    income: pt.income,
    expenses: pt.variable_expenses + pt.known_obligations,
    cashFlow: pt.cash_flow,
    type: 'historical',
  }));

  if (history.projected) {
    const pt = history.projected;
    chartData.push({
      period: pt.month + ' (Proj)',
      income: pt.income,
      expenses: pt.variable_expenses + pt.known_obligations,
      cashFlow: pt.cash_flow,
      type: 'projected',
    });
  }

  return (
    <section className="card p-5 animate-fade-in" aria-labelledby="forecast-chart-title">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h2 id="forecast-chart-title" className="section-title">Income vs. Expenses</h2>
          <p className="text-xs text-muted mt-0.5">Historical and projected</p>
        </div>
        <div className="flex items-center gap-3 text-xs text-muted">
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-positive inline-block rounded" />
            Income
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-danger inline-block rounded" />
            Expenses
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-primary-accent inline-block rounded" />
            Cash Flow
          </span>
        </div>
      </div>

      <div style={{ height: '220px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="incomeGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#16A34A" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#16A34A" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="expensesGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#DC2626" stopOpacity={0.1} />
                <stop offset="95%" stopColor="#DC2626" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="cashFlowGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563EB" stopOpacity={0.12} />
                <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
            <XAxis
              dataKey="period"
              tick={{ fontSize: 12, fill: '#64748B' }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 11, fill: '#64748B' }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => formatCurrencyCompact(v, currency)}
              width={60}
            />
            <Tooltip content={<CustomTooltip currency={currency} />} />
            <ReferenceLine y={0} stroke="#E2E8F0" strokeWidth={1} />
            <Area
              type="monotone"
              dataKey="income"
              stroke="#16A34A"
              strokeWidth={2}
              fill="url(#incomeGrad)"
              dot={{ fill: '#16A34A', r: 4 }}
              strokeDasharray={chartData.some(d => d.type === 'projected') ? '0 0' : undefined}
            />
            <Area
              type="monotone"
              dataKey="expenses"
              stroke="#DC2626"
              strokeWidth={2}
              fill="url(#expensesGrad)"
              dot={{ fill: '#DC2626', r: 4 }}
            />
            <Area
              type="monotone"
              dataKey="cashFlow"
              stroke="#2563EB"
              strokeWidth={2}
              fill="url(#cashFlowGrad)"
              dot={{ fill: '#2563EB', r: 4 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

    </section>
  );
};
