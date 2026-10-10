import React from 'react';
import type { CopilotResponse } from '../../types';
import { formatCurrency } from '../../utils/format';
import { DecisionTrace } from '../shared/DecisionTrace';
import { Shield, TrendingUp, AlertTriangle, Eye, GitFork, Lightbulb, ArrowRight } from 'lucide-react';

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
            <Section icon={Eye} title="Confidence" colorClass="bg-muted/10 text-muted">
              {response.confidence}
            </Section>
          )}
        </>
      )}

      {intent === 'WHAT_IF' && (
        <>
          {structured_result.baseline_balance !== undefined && structured_result.scenario_balance !== undefined ? (
            <Section icon={GitFork} title="Scenario Comparison" colorClass="bg-purple-500/10 text-purple-500">
              <div className="flex justify-between items-center bg-background rounded p-2 mb-2">
                <div className="text-center">
                  <div className="text-2xs text-muted uppercase tracking-wider">Baseline Balance</div>
                  <div className="font-semibold text-primary-dark">{formatCurrency(structured_result.baseline_balance as number, currency)}</div>
                </div>
                <div className="text-muted"><ArrowRight size={14} /></div>
                <div className="text-center">
                  <div className="text-2xs text-muted uppercase tracking-wider">Scenario Balance</div>
                  <div className="font-semibold text-primary-dark">{formatCurrency(structured_result.scenario_balance as number, currency)}</div>
                </div>
              </div>
              <div className="text-sm text-muted">
                Buffer status: <strong>{structured_result.buffer_status_change as string}</strong>
                {structured_result.balance_change !== undefined && ` (Change: ${formatCurrency(structured_result.balance_change as number, currency)})`}
              </div>
            </Section>
          ) : (
            <>
              <Section icon={GitFork} title="Scenario" colorClass="bg-purple-500/10 text-purple-500">
                Adjusting spending/income categories.
              </Section>
              <Section icon={TrendingUp} title="Impact" colorClass="bg-warning/10 text-warning">
                New projected balance: {formatCurrency(structured_result.projected_balance as number, currency)}.
                Buffer status is {structured_result.buffer_status_change as string}.
              </Section>
            </>
          )}
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

      {/* Top-Level Lists */}
      {response.observed_facts && response.observed_facts.length > 0 && (
        <Section icon={Eye} title="Observed Facts" colorClass="bg-primary-accent/10 text-primary-accent">
          <ul className="list-disc pl-4 space-y-1">
            {response.observed_facts.map((f, i) => <li key={i}>{f}</li>)}
          </ul>
        </Section>
      )}

      {response.assumptions && response.assumptions.length > 0 && (
        <Section icon={Lightbulb} title="Assumptions" colorClass="bg-muted/10 text-muted">
          <ul className="list-disc pl-4 space-y-1">
            {response.assumptions.map((a, i) => <li key={i}>{a}</li>)}
          </ul>
        </Section>
      )}

      {response.recommendations && response.recommendations.length > 0 && (
        <Section icon={Shield} title="Recommendations" colorClass="bg-positive/10 text-positive">
          <ul className="list-disc pl-4 space-y-1">
            {response.recommendations.map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        </Section>
      )}

      {response.trade_offs && response.trade_offs.length > 0 && (
        <Section icon={AlertTriangle} title="Trade-offs" colorClass="bg-warning/10 text-warning">
          <ul className="list-disc pl-4 space-y-1">
            {response.trade_offs.map((t, i) => <li key={i}>{t}</li>)}
          </ul>
        </Section>
      )}

      {response.limitations && response.limitations.length > 0 && (
        <Section icon={AlertTriangle} title="Limitations" colorClass="bg-danger/10 text-danger">
          <ul className="list-disc pl-4 space-y-1">
            {response.limitations.map((l, i) => <li key={i}>{l}</li>)}
          </ul>
        </Section>
      )}
    </div>
  );
};
