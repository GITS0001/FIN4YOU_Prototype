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
  <div className="mb-4 last:mb-0 bg-white rounded-xl border border-slate-100 p-4 shadow-sm">
    <div className="flex items-center gap-2 mb-2">
      <div className={`w-6 h-6 rounded flex items-center justify-center ${colorClass}`}>
        <Icon size={14} />
      </div>
      <h4 className="text-sm font-semibold text-slate-800">{title}</h4>
    </div>
    <div className="text-sm text-slate-600 pl-8">
      {children}
    </div>
  </div>
);

export const CopilotStructuredResponse: React.FC<CopilotStructuredResponseProps> = ({ response, currency }) => {
  const { intent, structured_result, decision_trace } = response;
  
  if (!structured_result) return null;

  return (
    <div className="mt-4 space-y-3 bg-slate-50 p-4 rounded-xl border border-slate-200">
      {intent === 'AFFORDABILITY_CHECK' && (
        <>
          <Section icon={Eye} title="Observed" colorClass="bg-blue-50 text-blue-600">
            Current balance and projections analyzed.
          </Section>
          <Section icon={GitFork} title="Scenario" colorClass="bg-purple-50 text-purple-600">
            Checking affordability for planned expense.
          </Section>
          <Section icon={TrendingUp} title="Impact" colorClass="bg-amber-50 text-amber-600">
            Projected balance would be {formatCurrency(structured_result.resulting_balance as number, currency)}.
            {(structured_result.trade_off as number) > 0 && ` A trade-off of ${formatCurrency(structured_result.trade_off as number, currency)} is required.`}
          </Section>
          <Section icon={structured_result.affordability_status === 'AFFORDABLE' ? Shield : AlertTriangle} title="Recommendation" colorClass={structured_result.affordability_status === 'AFFORDABLE' ? "bg-emerald-50 text-emerald-600" : "bg-red-50 text-red-600"}>
            <strong>{structured_result.affordability_status as string}</strong>
          </Section>
        </>
      )}

      {intent === 'WHAT_IF' && (
        <>
          <Section icon={Eye} title="Observed" colorClass="bg-blue-50 text-blue-600">
            Baseline spending and savings rates analyzed.
          </Section>
          <Section icon={GitFork} title="Scenario" colorClass="bg-purple-50 text-purple-600">
            Adjusting spending/income categories.
          </Section>
          <Section icon={TrendingUp} title="Impact" colorClass="bg-amber-50 text-amber-600">
            New projected balance: {formatCurrency(structured_result.projected_balance as number, currency)}.
            Buffer status is {structured_result.buffer_status_change as string}.
          </Section>
          <Section icon={Lightbulb} title="Recommendation" colorClass="bg-emerald-50 text-emerald-600">
            {structured_result.buffer_status_change === 'breached' ? 'Avoid this change if possible.' : 'This change maintains financial health.'}
          </Section>
        </>
      )}
      
      {intent === 'CASH_FLOW_FORECAST' && (
        <>
          <Section icon={Eye} title="Observed" colorClass="bg-blue-50 text-blue-600">
            Historical transaction patterns analyzed.
          </Section>
          <Section icon={TrendingUp} title="Prediction" colorClass="bg-purple-50 text-purple-600">
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
