import React from 'react';

interface LoadingSkeletonProps {
  className?: string;
  lines?: number;
  height?: string;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  className = '',
  lines = 1,
  height = 'h-4',
}) => {
  if (lines === 1) {
    return <div className={`skeleton ${height} ${className}`} aria-hidden="true" />;
  }

  return (
    <div className={`space-y-2 ${className}`} aria-hidden="true">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={`skeleton ${height} ${i === lines - 1 ? 'w-3/4' : 'w-full'}`}
        />
      ))}
    </div>
  );
};

export const KpiCardSkeleton: React.FC = () => (
  <div className="card p-5 animate-pulse" aria-hidden="true">
    <div className="flex items-center justify-between mb-3">
      <div className="skeleton h-3 w-20" />
      <div className="skeleton h-8 w-8 rounded-lg" />
    </div>
    <div className="skeleton h-7 w-28 mb-1" />
    <div className="skeleton h-3 w-16" />
  </div>
);

export const ChartSkeleton: React.FC<{ height?: string }> = ({ height = 'h-48' }) => (
  <div className={`card p-5 animate-pulse ${height}`} aria-hidden="true">
    <div className="skeleton h-4 w-32 mb-4" />
    <div className="flex items-end gap-2 h-32">
      {[60, 80, 45, 90, 70, 55, 85].map((h, i) => (
        <div
          key={i}
          className="skeleton flex-1 rounded-t"
          style={{ height: `${h}%` }}
        />
      ))}
    </div>
  </div>
);

export const InsightCardSkeleton: React.FC = () => (
  <div className="card p-4 animate-pulse" aria-hidden="true">
    <div className="flex items-start gap-3">
      <div className="skeleton h-8 w-8 rounded-lg flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <div className="skeleton h-4 w-32" />
        <div className="skeleton h-3 w-full" />
        <div className="skeleton h-3 w-4/5" />
      </div>
    </div>
  </div>
);

export const TableRowSkeleton: React.FC<{ cols?: number }> = ({ cols = 4 }) => (
  <tr className="animate-pulse" aria-hidden="true">
    {Array.from({ length: cols }).map((_, i) => (
      <td key={i} className="px-4 py-3">
        <div className="skeleton h-3 w-full" />
      </td>
    ))}
  </tr>
);
