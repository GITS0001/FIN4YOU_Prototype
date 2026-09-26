import React from 'react';
import type { CopilotResponse } from '../../types';
import { formatCurrency } from '../../utils/format';
import { DecisionTrace } from '../shared/DecisionTrace';
import { Shield, TrendingUp, AlertTriangle, Eye, GitFork, Lightbulb } from 'lucide-react';

interface CopilotStructuredResponseProps {
  response: CopilotResponse;
  currency: string;
}

const Section = ({ icon: Icon, title, children, colorClass }: { icon: any, title: string, children: React.ReactNode, colorClass: string }) => (
  <div className="mb-4 last:mb-0 bg-card-bg rounded-xl border border-border p-4 shadow-sm">
    <div className="flex items-center gap-2 mb-2">
      <div className={`w-6 h-6 rounded flex items-center justify-center ${colorClass}`}>
        <Icon size={14} />
      </div>
      <h4 className="text-sm font-semibold text-primary-dark">{title}</h4>
    </div>
    <div className="text-sm text-muted pl-8">
      {children}
    </div>
  </div>
);

export const CopilotStructuredResponse: React.FC<CopilotStructuredResponseProps> = ({ response, currency }) => {
  const { intent, structured_result, decision_trace } = response;
  
  if (!structured_result) return null;

  return (
    <div className="mt-4 space-y-3 bg-background p-4 rounded-xl border border-border">
      {intent === 'AFFORDABILITY_CHECK' && (
        <>
          <Section icon={Eye} title="Observed" colorClass="bg-primary-accent/10 text-primary-accent">
            Current balance: {formatCurrency(structured_result.current_balance as number, currency)}<br />
            Minimum buffer: {formatCurrency(structured_result.minimum_buffer as number, currency)}<br />
            Projected cash flow: {formatCurrency(structured_result.projected_cash_flow as number, currency)}
          </Section>

          <Section icon={GitFork} title="Scenario" colorClass="bg-purple-500/10 text-purple-500">
            Purchase intent: {formatCurrency(structured_result.proposed_amount as number, currency)}
          </Section>

          <Section icon={TrendingUp} title="Expected Impact" colorClass="bg-warning/10 text-warning">
            Projected balance: {formatCurrency(structured_result.resulting_balance as number, currency)}<br />
            {(structured_result.shortfall as number) > 0 && `Shortfall: ${formatCurrency(structured_result.shortfall as number, currency)}`}
            {(structured_result.trade_off as number) > 0 && `Trade-off required: ${formatCurrency(structured_result.trade_off as number, currency)}`}
          </Section>

          <Section icon={structured_result.affordability_status === 'AFFORDABLE' ? Shield : AlertTriangle} title="Affordability" colorClass={structured_result.affordability_status === 'AFFORDABLE' ? "bg-positive/10 text-positive" : "bg-danger/10 text-danger"}>
            <strong>Upfront: {structured_result.affordability_status as string}</strong>
          </Section>

          {structured_result.viable_options && (structured_result.viable_options as any[]).length > 0 && (
            <Section icon={Lightbulb} title="Payment Options" colorClass="bg-primary-accent/10 text-primary-accent">
              <ul className="list-disc pl-4 mt-1 space-y-1">
                {(structured_result.viable_options as any[]).map((opt: any, idx: number) => (
                  <li key={idx} className="text-sm">
                    {opt.number_of_payments > 1 
                      ? `${opt.number_of_payments} x ${formatCurrency(opt.payment_amount, currency)}/mo (Total: ${formatCurrency(opt.total_payable_amount, currency)})` 
                      : `Full payment of ${formatCurrency(opt.payment_amount, currency)}`}
                  </li>
                ))}
              </ul>
            </Section>
          )}

          <Section icon={Shield} title="Recommendation" colorClass="bg-positive/10 text-positive">
            {structured_result.affordability_status === 'AFFORDABLE' 
              ? 'Proceed with upfront purchase as buffer is maintained.' 
              : structured_result.viable_options && (structured_result.viable_options as any[]).length > 0 
              ? 'Upfront purchase breaches buffer. Recommend using an installment option to preserve financial health.'
              : 'Purchase is not affordable and no viable installment options were found. Delay purchase.'}
          </Section>

          {response.confidence && (
            <Section icon={Eye} title="Confidence" colorClass="bg-gray-100 text-gray-500">
              {response.confidence}
            </Section>
          )}
        </>
      )}

      {intent === 'WHAT_IF' && (
        <>
          <Section icon={Eye} title="Observed" colorClass="bg-primary-accent/10 text-primary-accent">
            Baseline spending and savings rates analyzed.
          </Section>
          <Section icon={GitFork} title="Scenario" colorClass="bg-purple-500/10 text-purple-500">
            Adjusting spending/income categories.
          </Section>
          <Section icon={TrendingUp} title="Impact" colorClass="bg-warning/10 text-warning">
            New projected balance: {formatCurrency(structured_result.projected_balance as number, currency)}.
            Buffer status is {structured_result.buffer_status_change as string}.
          </Section>
          <Section icon={Lightbulb} title="Recommendation" colorClass="bg-positive/10 text-positive">
            {structured_result.buffer_status_change === 'breached' ? 'Avoid this change if possible.' : 'This change maintains financial health.'}
          </Section>
        </>
      )}
      
      {intent === 'CASH_FLOW_FORECAST' && (
        <>
          <Section icon={Eye} title="Observed" colorClass="bg-primary-accent/10 text-primary-accent">
            Historical transaction patterns analyzed.
          </Section>
          <Section icon={TrendingUp} title="Prediction" colorClass="bg-purple-500/10 text-purple-500">
            Projected Cash Flow: {formatCurrency(structured_result.projected_cash_flow as number, currency)}
            <br />
            Projected Balance: {formatCurrency(structured_result.projected_balance as number, currency)}
          </Section>
        </>
      )}

      {decision_trace && (
        <div className="mt-4">
          <DecisionTrace trace={decision_trace} currency={currency} />
        </div>
      )}
    </div>
  );
};
