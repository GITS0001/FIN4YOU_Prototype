import React from 'react';
import type { LucideIcon } from 'lucide-react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { KpiCardSkeleton } from '../shared/LoadingSkeleton';

interface KpiCardProps {
  label: string;
  value: string;
  subValue?: string;
  icon: LucideIcon;
  iconColor?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendLabel?: string;
  isLoading?: boolean;
}

export const KpiCard: React.FC<KpiCardProps> = ({
  label,
  value,
  subValue,
  icon: Icon,
  iconColor = 'text-primary-accent',
  trend,
  trendLabel,
  isLoading,
}) => {
  if (isLoading) return <KpiCardSkeleton />;

  const trendConfig = {
    up: { icon: TrendingUp, textClass: 'text-positive', bgClass: 'badge-positive' },
    down: { icon: TrendingDown, textClass: 'text-danger', bgClass: 'badge-danger' },
    neutral: { icon: Minus, textClass: 'text-muted', bgClass: 'badge-neutral' },
  };

  const CurrentTrend = trend ? trendConfig[trend] : null;

  return (
    <article className="card-hover p-5 animate-fade-in flex flex-col justify-between relative overflow-hidden">
      <div>
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs font-medium text-muted uppercase tracking-wider">{label}</p>
          <div className={`w-8 h-8 flex items-center justify-end ${iconColor}`}>
            <Icon size={18} aria-hidden="true" />
          </div>
        </div>

        <p className="text-2xl font-bold tracking-tight text-primary-dark mb-1" aria-label={`${label}: ${value}`}>
          {value}
        </p>
      </div>

      {(subValue || trendLabel) && (
        <div className="flex items-center gap-2 mt-3 pt-3 border-t border-border">
          {CurrentTrend && trendLabel ? (
            <span className={`inline-flex items-center gap-1 text-2xs font-medium px-2 py-0.5 rounded-md border ${CurrentTrend.bgClass}`}>
              <CurrentTrend.icon size={11} aria-hidden="true" />
              {trendLabel}
            </span>
          ) : (
            subValue && <span className="text-2xs font-medium text-muted">{subValue}</span>
          )}
        </div>
      )}
    </article>
  );
};
