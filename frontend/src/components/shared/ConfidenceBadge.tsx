import React from 'react';
import { formatConfidence } from '../../utils/format';
import { CheckCircle, AlertTriangle, HelpCircle } from 'lucide-react';

interface ConfidenceBadgeProps {
  confidence: string;
  showIcon?: boolean;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({
  confidence,
  showIcon = true,
}) => {
  const { label, variant } = formatConfidence(confidence);

  const variantClasses = {
    positive: 'badge-positive',
    warning: 'badge-warning',
    neutral: 'badge-neutral',
  };

  const icons = {
    positive: CheckCircle,
    warning: AlertTriangle,
    neutral: HelpCircle,
  };

  const Icon = showIcon ? icons[variant] : null;

  return (
    <span
      className={variantClasses[variant]}
      aria-label={label}
      title={label}
    >
      {Icon && <Icon size={11} aria-hidden="true" />}
      {label}
    </span>
  );
};
