import React from 'react';
import { AlertTriangle, Info, TrendingDown, Activity, ArrowRight } from 'lucide-react';
import type { FinancialState, PredictionEngineResult, FinancialProfile } from '../../types';
import { formatCurrency } from '../../utils/format';
import { useNavigate } from 'react-router-dom';
import { InsightCardSkeleton } from '../shared/LoadingSkeleton';

interface Insight {
  id: string;
  icon: React.ElementType;
  title: string;
  description: string;
  severity: 'warning' | 'info' | 'danger';
  action?: { label: string; path: string };
}

interface InsightCardProps {
  state: FinancialState | null;
  prediction: PredictionEngineResult | null;
  profile: FinancialProfile | null;
  isLoading: boolean;
}

function deriveInsights(
  state: FinancialState,
  prediction: PredictionEngineResult,
  profile: FinancialProfile
): Insight[] {
  const insights: Insight[] = [];
  const currency = profile.home_currency;

  // Cash flow gap
  if (prediction.gap_detection?.detected) {
    insights.push({
      id: 'gap',
      icon: AlertTriangle,
      title: 'Cash flow gap detected',
      description: `Your projected balance next month (${formatCurrency(prediction.gap_detection.projected_balance, currency)}) may fall ${formatCurrency(prediction.gap_detection.shortfall, currency)} below your required buffer.`,
      severity: 'danger',
      action: { label: 'View Forecast', path: '/forecast' },
    });
  }

  // High discretionary spending
  if (state.discretionary_expenses > state.essential_expenses * 0.6) {
    insights.push({
      id: 'discretionary',
      icon: TrendingDown,
      title: 'Discretionary spending is elevated',
      description: `Your discretionary expenses (${formatCurrency(state.discretionary_expenses, currency)}) are significant relative to essential spending.`,
      severity: 'warning',
      action: { label: 'What-If Analysis', path: '/what-if' },
    });
  }

  // Negative savings rate / High expense ratio
  if (state.savings_rate < 0 || state.expenses > state.income) {
    insights.push({
      id: 'negative-savings',
      icon: AlertTriangle,
      title: 'Expenses exceed income',
      description: `Your expenses (${formatCurrency(state.expenses, currency)}) are higher than your income (${formatCurrency(state.income, currency)}), leading to a negative savings rate.`,
      severity: 'danger',
      action: { label: 'View Affordability', path: '/affordability' },
    });
  } else if (state.savings_rate < 0.05) {
    insights.push({
      id: 'low-savings',
      icon: Info,
      title: 'Low savings rate',
      description: `Your savings rate is very low (${(state.savings_rate * 100).toFixed(1)}%). Consider reducing discretionary spending.`,
      severity: 'warning',
    });
  }

  // Anomalies
  const detectedAnomalies = state.anomalies.filter((a) => a.is_anomaly);
  if (detectedAnomalies.length > 0) {
    insights.push({
      id: 'anomaly',
      icon: Activity,
      title: `${detectedAnomalies.length} unusual transaction${detectedAnomalies.length > 1 ? 's' : ''} detected`,
      description: 'One or more transactions were flagged as unusual based on your spending patterns.',
      severity: 'warning',
      action: { label: 'View Insights', path: '/insights' },
    });
  }

  // Insufficient prediction data
  if (!prediction.available) {
    insights.push({
      id: 'insufficient',
      icon: Info,
      title: 'Insufficient data for forecasting',
      description: prediction.reason || 'More transaction history is needed to generate forecasts.',
      severity: 'info',
    });
  }

  // Positive: Savings rate is good
  if (state.savings_rate >= 0.2 && insights.length === 0) {
    insights.push({
      id: 'savings-good',
      icon: Info,
      title: 'Strong savings rate',
      description: `Your savings rate of ${(state.savings_rate * 100).toFixed(1)}% is above the recommended 20% threshold.`,
      severity: 'info',
    });
  }

  return insights;
}

const severityConfig = {
  danger: {
    bg: 'bg-red-50',
    border: 'border-red-100',
    icon: 'text-danger bg-red-100',
  },
  warning: {
    bg: 'bg-amber-50',
    border: 'border-amber-100',
    icon: 'text-warning bg-amber-100',
  },
  info: {
    bg: 'bg-blue-50',
    border: 'border-blue-100',
    icon: 'text-primary-accent bg-blue-100',
  },
};

interface SingleInsightProps {
  insight: Insight;
}

const SingleInsight: React.FC<SingleInsightProps> = ({ insight }) => {
  const navigate = useNavigate();
  const config = severityConfig[insight.severity];

  return (
    <article
      className={`flex items-start gap-3 p-4 rounded-xl border ${config.bg} ${config.border} animate-slide-up`}
      aria-label={insight.title}
    >
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${config.icon}`}>
        <insight.icon size={15} aria-hidden="true" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-primary-dark mb-0.5">{insight.title}</p>
        <p className="text-xs text-muted leading-relaxed">{insight.description}</p>
        {insight.action && (
          <button
            className="mt-2 flex items-center gap-1 text-xs font-medium text-primary-accent hover:underline focus:outline-none focus:ring-1 focus:ring-primary-accent rounded"
            onClick={() => navigate(insight.action!.path)}
          >
            {insight.action.label}
            <ArrowRight size={11} aria-hidden="true" />
          </button>
        )}
      </div>
    </article>
  );
};

export const InsightCard: React.FC<InsightCardProps> = ({
  state,
  prediction,
  profile,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <section className="card p-5">
        <div className="skeleton h-5 w-40 mb-4" />
        <div className="space-y-3">
          <InsightCardSkeleton />
          <InsightCardSkeleton />
        </div>
      </section>
    );
  }

  if (!state || !prediction || !profile) return null;

  const insights = deriveInsights(state, prediction, profile);

  return (
    <section className="card p-5 animate-fade-in" aria-labelledby="ai-insights-title">
      <div className="flex items-center justify-between mb-4">
        <h2 id="ai-insights-title" className="section-title">AI Financial Insights</h2>
        <span className="badge-neutral">{insights.length} insight{insights.length !== 1 ? 's' : ''}</span>
      </div>

      {insights.length === 0 ? (
        <p className="text-sm text-muted">Your finances look healthy. No alerts at this time.</p>
      ) : (
        <div className="space-y-2">
          {insights.map((insight) => (
            <SingleInsight key={insight.id} insight={insight} />
          ))}
        </div>
      )}
    </section>
  );
};
