import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface PageHeaderProps {
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  icon?: LucideIcon;
  eyebrow?: React.ReactNode;
  actions?: React.ReactNode;
}

/** Consistent page heading used on every app page. */
export const PageHeader: React.FC<PageHeaderProps> = ({ title, subtitle, icon: Icon, eyebrow, actions }) => (
  <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between animate-slide-up">
    <div className="flex items-start gap-4 min-w-0">
      {Icon && (
        <div className="hidden sm:flex w-12 h-12 rounded-2xl bg-brand-gradient items-center justify-center flex-shrink-0 shadow-lg shadow-primary-accent/25">
          <Icon size={22} className="text-white" aria-hidden="true" />
        </div>
      )}
      <div className="min-w-0">
        {eyebrow && <p className="text-overline text-primary-accent mb-1.5">{eyebrow}</p>}
        <h1 className="text-display">{title}</h1>
        {subtitle && <p className="text-sm text-muted mt-1.5 max-w-2xl">{subtitle}</p>}
      </div>
    </div>
    {actions && <div className="flex items-center gap-2 flex-shrink-0">{actions}</div>}
  </header>
);

interface SectionHeaderProps {
  title: React.ReactNode;
  description?: React.ReactNode;
  icon?: LucideIcon;
  iconClass?: string;
  action?: React.ReactNode;
  id?: string;
  className?: string;
}

/** Consistent section/card heading. */
export const SectionHeader: React.FC<SectionHeaderProps> = ({
  title,
  description,
  icon: Icon,
  iconClass = 'bg-primary-accent/10 text-primary-accent',
  action,
  id,
  className = 'mb-5',
}) => (
  <div className={`flex items-start justify-between gap-4 ${className}`}>
    <div className="flex items-start gap-3 min-w-0">
      {Icon && (
        <div className={`icon-tile ${iconClass}`}>
          <Icon size={18} aria-hidden="true" />
        </div>
      )}
      <div className="min-w-0">
        <h2 id={id} className="text-h2">
          {title}
        </h2>
        {description && <p className="text-xs text-muted mt-0.5">{description}</p>}
      </div>
    </div>
    {action && <div className="flex-shrink-0">{action}</div>}
  </div>
);
