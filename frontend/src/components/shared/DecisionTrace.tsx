import React, { useState } from 'react';
import {
  ChevronDown,
  Eye,
  Calculator,
  TrendingUp,
  GitBranch,
  Lightbulb,
} from 'lucide-react';
import type { DecisionTrace as DecisionTraceType } from '../../types';
import { formatCurrency } from '../../utils/format';
import { ConfidenceBadge } from './ConfidenceBadge';

interface Step {
  icon: React.ElementType;
  label: string;
  content: string;
  color: string;
}

interface DecisionTraceProps {
  trace: DecisionTraceType;
  currency?: string;
}

export const DecisionTrace: React.FC<DecisionTraceProps> = ({ trace, currency = 'USD' }) => {
  const [isOpen, setIsOpen] = useState(false);

  const steps: Step[] = [
    {
      icon: Eye,
      label: 'Observed',
      content: trace.observed_fact,
      color: 'text-primary-accent bg-primary-accent/10',
    },
    {
      icon: Calculator,
      label: 'Calculated',
      content: trace.calculation,
      color: 'text-warning bg-warning/10',
    },
    {
      icon: TrendingUp,
      label: 'Predicted',
      content: trace.prediction,
      color: 'text-purple-500 bg-purple-500/10',
    },
    {
      icon: GitBranch,
      label: 'Simulated',
      content: trace.simulation,
      color: 'text-positive bg-positive/10',
    },
    {
      icon: Lightbulb,
      label: 'Recommended',
      content: trace.recommendation.actionable_text,
      color: 'text-positive bg-positive/10',
    },
  ];

  return (
    <div className="border border-border rounded-lg overflow-hidden mt-3">
      <button
        className="w-full flex items-center justify-between px-4 py-3 text-sm font-medium text-primary-dark hover:bg-background transition-colors"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-controls="decision-trace-content"
      >
        <span className="flex items-center gap-2">
          <GitBranch size={14} className="text-muted" aria-hidden="true" />
          How FIN4YOU reached this conclusion
        </span>
        <ChevronDown
          size={14}
          className={`text-muted transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          aria-hidden="true"
        />
      </button>

      <div
        id="decision-trace-content"
        className={`accordion-content ${isOpen ? 'max-h-[600px] opacity-100' : 'max-h-0 opacity-0'}`}
      >
        <div className="px-4 pb-4 border-t border-border">
          {/* Steps */}
          <ol className="mt-4 space-y-3" aria-label="Decision reasoning steps">
            {steps.map((step, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <div className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 ${step.color}`}>
                  <step.icon size={13} aria-hidden="true" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-semibold text-muted uppercase tracking-wide mb-0.5">
                    {idx + 1}. {step.label}
                  </p>
                  <p className="text-sm text-primary-dark">{step.content}</p>
                </div>
              </li>
            ))}
          </ol>

          {/* Supporting data */}
          {Object.keys(trace.supporting_data).length > 0 && (
            <div className="mt-4 pt-3 border-t border-border">
              <p className="label-sm mb-2">Supporting Data</p>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(trace.supporting_data).map(([key, val]) => (
                  <div key={key} className="bg-background rounded-lg p-2.5">
                    <p className="text-2xs text-muted uppercase tracking-wide capitalize">
                      {key.replace(/_/g, ' ')}
                    </p>
                    <p className="text-sm font-semibold text-primary-dark">
                      {formatCurrency(val, currency)}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Confidence */}
          <div className="mt-3 pt-3 border-t border-border flex items-center justify-between">
            <p className="text-xs text-muted">{trace.recommendation.confidence_reason}</p>
            <ConfidenceBadge confidence={trace.recommendation.confidence_level} />
          </div>
        </div>
      </div>
    </div>
  );
};
