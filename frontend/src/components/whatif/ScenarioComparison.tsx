import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { formatCurrency, formatCurrencyCompact } from '../../utils/format';
import { ArrowRight, CheckCircle, XCircle } from 'lucide-react';

interface ScenarioData {
  label: string;
  income: number;
  expenses: number;
  cashFlow: number;
  balance: number;
  bufferBreached: boolean;
  shortfall: number;
}

interface ScenarioComparisonProps {
  baseline: ScenarioData;
  scenario: ScenarioData;
  currency: string;
}

const CustomTooltip = ({
  active,
  payload,
  label,
  currency,
}: {
  active?: boolean;
  payload?: Array<{ name: string; value: number }>;
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
            <span className="text-xs font-semibold text-primary-dark">
              {formatCurrency(entry.value, currency)}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export const ScenarioComparison: React.FC<ScenarioComparisonProps> = ({
  baseline,
  scenario,
  currency,
}) => {
  const chartData = [
    {
      name: 'Income',
      Current: baseline.income,
      Scenario: scenario.income,
    },
    {
      name: 'Expenses',
      Current: baseline.expenses,
      Scenario: scenario.expenses,
    },
    {
      name: 'Cash Flow',
      Current: baseline.cashFlow,
      Scenario: scenario.cashFlow,
    },
    {
      name: 'Balance',
      Current: baseline.balance,
      Scenario: scenario.balance,
    },
  ];

  const metrics: Array<{ label: string; current: string; scenario: string; better: boolean | null }> = [
    {
      label: 'Projected Income',
      current: formatCurrency(baseline.income, currency),
      scenario: formatCurrency(scenario.income, currency),
      better: scenario.income > baseline.income ? true : scenario.income < baseline.income ? false : null,
    },
    {
      label: 'Projected Expenses',
      current: formatCurrency(baseline.expenses, currency),
      scenario: formatCurrency(scenario.expenses, currency),
      better: scenario.expenses < baseline.expenses ? true : scenario.expenses > baseline.expenses ? false : null,
    },
    {
      label: 'Cash Flow',
      current: formatCurrency(baseline.cashFlow, currency),
      scenario: formatCurrency(scenario.cashFlow, currency),
      better: scenario.cashFlow > baseline.cashFlow ? true : scenario.cashFlow < baseline.cashFlow ? false : null,
    },
    {
      label: 'Projected Balance',
      current: formatCurrency(baseline.balance, currency),
      scenario: formatCurrency(scenario.balance, currency),
      better: scenario.balance > baseline.balance ? true : scenario.balance < baseline.balance ? false : null,
    },
    {
      label: 'Buffer Breached',
      current: baseline.bufferBreached ? 'Yes' : 'No',
      scenario: scenario.bufferBreached ? 'Yes' : 'No',
      better: !scenario.bufferBreached && baseline.bufferBreached
        ? true
        : scenario.bufferBreached && !baseline.bufferBreached
        ? false
        : null,
    },
  ];

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Comparison table */}
      <div className="card overflow-hidden">
        <div className="grid grid-cols-3 gap-0 divide-x divide-border">
          <div className="p-4 bg-background">
            <p className="label-sm mb-1">Current</p>
            <p className="text-xs text-muted">Baseline projection</p>
          </div>
          <div className="p-4 flex items-center justify-center bg-background">
            <ArrowRight size={18} className="text-muted" aria-hidden="true" />
          </div>
          <div className="p-4 bg-blue-50/30">
            <p className="label-sm mb-1 text-primary-accent">Scenario</p>
            <p className="text-xs text-muted">What changes</p>
          </div>
        </div>

        <div className="divide-y divide-border">
          {metrics.map((metric) => (
            <div key={metric.label} className="grid grid-cols-3 gap-0 divide-x divide-border items-center">
              <div className="px-4 py-3">
                <p className="text-xs text-muted">{metric.label}</p>
                <p className="text-sm font-medium text-primary-dark">{metric.current}</p>
              </div>
              <div className="flex items-center justify-center py-3">
                {metric.better === true && <CheckCircle size={15} className="text-positive" aria-label="Improved" />}
                {metric.better === false && <XCircle size={15} className="text-danger" aria-label="Worse" />}
                {metric.better === null && <div className="w-3 h-0.5 bg-border rounded" aria-label="No change" />}
              </div>
              <div className="px-4 py-3 bg-blue-50/20">
                <p className="text-sm font-semibold text-primary-dark">{metric.scenario}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Chart */}
      <div className="card p-5">
        <h3 className="section-title mb-4">Visual Comparison</h3>
        <div style={{ height: '200px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 0, right: 10, left: 0, bottom: 0 }} barGap={4}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
              <XAxis
                dataKey="name"
                tick={{ fontSize: 11, fill: '#64748B' }}
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
              <Bar dataKey="Current" fill="#E2E8F0" radius={[4, 4, 0, 0]} name="Current" />
              <Bar dataKey="Scenario" radius={[4, 4, 0, 0]} name="Scenario">
                {chartData.map((_, index) => (
                  <Cell
                    key={index}
                    fill="#2563EB"
                    opacity={0.85}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="flex items-center gap-4 justify-center mt-2">
          <span className="flex items-center gap-1.5 text-xs text-muted">
            <span className="w-2.5 h-2.5 rounded-sm bg-border inline-block" />
            Current
          </span>
          <span className="flex items-center gap-1.5 text-xs text-muted">
            <span className="w-2.5 h-2.5 rounded-sm bg-primary-accent inline-block" />
            Scenario
          </span>
        </div>
      </div>

      {/* Buffer alert */}
      {scenario.bufferBreached && (
        <div className="bg-red-50 border border-red-100 rounded-xl p-4">
          <div className="flex items-start gap-2">
            <XCircle size={16} className="text-danger flex-shrink-0 mt-0.5" aria-hidden="true" />
            <div>
              <p className="text-sm font-semibold text-danger">Buffer Breached in Scenario</p>
              <p className="text-xs text-red-600/80 mt-0.5">
                Projected shortfall: {formatCurrency(scenario.shortfall, currency)}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
