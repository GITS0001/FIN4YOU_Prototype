import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import type { CategorySpending } from '../../types';
import { formatCurrency, formatCategory, getCategoryColor } from '../../utils/format';
import { ChartSkeleton } from '../shared/LoadingSkeleton';

interface SpendingChartProps {
  categories: CategorySpending[];
  currency: string;
  isLoading: boolean;
  totalExpenses: number;
}

interface TooltipPayload {
  name: string;
  value: number;
  payload: { percentage: number };
}

const CustomTooltip = ({
  active,
  payload,
  currency,
}: {
  active?: boolean;
  payload?: TooltipPayload[];
  currency: string;
}) => {
  if (active && payload && payload.length) {
    const item = payload[0];
    return (
      <div className="bg-card-bg border border-border rounded-lg px-3 py-2 shadow-dropdown text-sm">
        <p className="font-semibold text-primary-dark">{formatCategory(item.name)}</p>
        <p className="text-muted">{formatCurrency(item.value, currency)}</p>
        <p className="text-xs text-muted">{item.payload.percentage.toFixed(1)}% of total</p>
      </div>
    );
  }
  return null;
};

export const SpendingChart: React.FC<SpendingChartProps> = ({
  categories,
  currency,
  isLoading,
  totalExpenses,
}) => {
  if (isLoading) return <ChartSkeleton height="h-64" />;

  // Filter positive amounts only and take top 8
  const filteredCategories = categories
    .filter((c) => c.total_amount > 0)
    .slice(0, 8);

  if (filteredCategories.length === 0) {
    return (
      <div className="card p-6">
        <h2 className="section-title mb-4">Where Your Money Goes</h2>
        <p className="text-sm text-muted">No spending data available.</p>
      </div>
    );
  }

  const chartData = filteredCategories.map((c) => ({
    name: c.category,
    value: c.total_amount,
    percentage: totalExpenses > 0 ? (c.total_amount / totalExpenses) * 100 : 0,
  }));

  return (
    <section className="card p-6 animate-fade-in flex flex-col justify-between" aria-labelledby="spending-chart-title">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 id="spending-chart-title" className="section-title">Where Your Money Goes</h2>
          <p className="text-2xs text-muted mt-0.5">Top expenditure breakdown</p>
        </div>
        <span className="text-xs font-medium px-2.5 py-1 bg-border rounded-lg text-primary-dark">
          {filteredCategories.length} Categories
        </span>
      </div>

      <div className="flex flex-col lg:flex-row gap-6 items-center">
        {/* Donut Chart with Center Overlay */}
        <div className="w-full lg:w-56 h-56 flex-shrink-0 flex items-center justify-center relative">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={65}
                outerRadius={95}
                paddingAngle={4}
                dataKey="value"
                aria-label="Spending by category"
              >
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={getCategoryColor(index)} stroke="var(--color-card-bg)" strokeWidth={2} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip currency={currency} />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-2xs font-semibold text-muted uppercase tracking-wider">Total</span>
            <span className="text-sm font-bold text-primary-dark">{formatCurrency(totalExpenses, currency)}</span>
          </div>
        </div>

        {/* Legend list */}
        <div className="flex-1 w-full">
          <ul className="space-y-2.5" role="list" aria-label="Spending categories">
            {chartData.map((item, index) => (
              <li key={item.name} className="flex items-center justify-between gap-3 p-1.5 rounded-lg hover:bg-background transition-colors">
                <div className="flex items-center gap-2 min-w-0">
                  <div
                    className="w-2.5 h-2.5 rounded-xs flex-shrink-0 shadow-2xs"
                    style={{ backgroundColor: getCategoryColor(index) }}
                    aria-hidden="true"
                  />
                  <span className="text-xs font-medium text-primary-dark truncate">
                    {formatCategory(item.name)}
                  </span>
                </div>
                <div className="flex items-center gap-3 flex-shrink-0">
                  <div className="w-16 h-1.5 bg-border rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-300"
                      style={{
                        width: `${item.percentage}%`,
                        backgroundColor: getCategoryColor(index),
                      }}
                    />
                  </div>
                  <span className="text-2xs font-semibold text-muted w-8 text-right">
                    {item.percentage.toFixed(0)}%
                  </span>
                  <span className="text-xs font-bold text-primary-dark w-20 text-right">
                    {formatCurrency(item.value, currency)}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
};
