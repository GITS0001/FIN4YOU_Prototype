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
  iconColor = 'text-primary-accent bg-primary-accent/10',
  trend,
  trendLabel,
  isLoading,
}) => {
  if (isLoading) return <KpiCardSkeleton />;

  const trendConfig = {
    up: { icon: TrendingUp, class: 'text-positive' },
    down: { icon: TrendingDown, class: 'text-danger' },
    neutral: { icon: Minus, class: 'text-muted' },
  };

  const TrendIcon = trend ? trendConfig[trend].icon : null;

  return (
    <article className="card-hover p-5 animate-fade-in">
      <div className="flex items-center justify-between mb-3">
        <p className="label-sm">{label}</p>
        <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${iconColor}`}>
          <Icon size={17} aria-hidden="true" />
        </div>
      </div>

      <p className="value-lg mb-0.5" aria-label={`${label}: ${value}`}>
        {value}
      </p>

      {(subValue || trend) && (
        <div className="flex items-center gap-1.5 mt-1">
          {TrendIcon && trend && (
            <TrendIcon
              size={12}
              className={trendConfig[trend].class}
              aria-hidden="true"
            />
          )}
          {trendLabel && (
            <p className={`text-xs ${trend ? trendConfig[trend].class : 'text-muted'}`}>
              {trendLabel}
            </p>
          )}
          {subValue && !trendLabel && (
            <p className="text-xs text-muted">{subValue}</p>
          )}
        </div>
      )}
    </article>
  );
};
