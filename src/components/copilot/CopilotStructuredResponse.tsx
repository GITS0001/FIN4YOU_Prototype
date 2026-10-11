import React from 'react';
import type { CopilotResponse } from '../../types';
import { formatCurrency } from '../../utils/format';
import { DecisionTrace } from '../shared/DecisionTrace';
import { Shield, TrendingUp, AlertTriangle, Eye, GitFork, Lightbulb, ArrowRight, PieChart as PieChartIcon } from 'lucide-react';

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
  
  const hasStructuredResult = Boolean(structured_result && Object.keys(structured_result).length > 0);
  const isSpecialIntent = ['AFFORDABILITY_CHECK', 'WHAT_IF', 'CASH_FLOW_FORECAST', 'SPENDING_ANALYSIS'].includes(intent);

  if (!hasStructuredResult && !decision_trace) return null;
  if (!isSpecialIntent && !decision_trace) return null;

  const messageText = response.response || (response as any).message || '';
  const hasBuiltInSections = messageText.includes('###') || messageText.includes('📌') || messageText.includes('📊');

  return (
    <div className="mt-4 space-y-3 bg-background p-4 rounded-xl border border-border">
      {intent === 'AFFORDABILITY_CHECK' && structured_result && (
        <>
          {Boolean(structured_result.has_conflict) && (
            <div className="mb-3 p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs text-amber-700 dark:text-amber-300 flex items-start gap-2.5">
              <AlertTriangle size={15} className="mt-0.5 shrink-0 text-amber-600 dark:text-amber-400" />
              <div>
                <strong className="font-semibold block mb-0.5">Scenario Override Active</strong>
                <span>Stated scenario values differ from your profile on record. Analysis evaluated against your stated scenario inputs. Confidence adjusted to MEDIUM.</span>
              </div>
            </div>
          )}

          <Section icon={Eye} title="Observed & Stated Inputs" colorClass="bg-primary-accent/10 text-primary-accent">
            <div className="space-y-1">
              <div>Bank balance: <strong>{formatCurrency(structured_result.current_balance as number, currency)}</strong></div>
              <div>Minimum buffer / Emergency fund: <strong>{formatCurrency(structured_result.minimum_buffer as number, currency)}</strong></div>
              {structured_result.monthly_income !== undefined && (
                <div>Monthly income: <strong>{formatCurrency(structured_result.monthly_income as number, currency)}</strong></div>
              )}
              {structured_result.monthly_expenses !== undefined && (
                <div>Monthly expenses: <strong>{formatCurrency(structured_result.monthly_expenses as number, currency)}</strong></div>
              )}
              {structured_result.monthly_savings !== undefined && (
                <div>Monthly savings: <strong>{formatCurrency(structured_result.monthly_savings as number, currency)}</strong></div>
              )}
              <div>Projected cash flow: <strong>{formatCurrency(structured_result.projected_cash_flow as number, currency)}</strong></div>
            </div>
          </Section>

          <Section icon={GitFork} title="Scenario" colorClass="bg-purple-500/10 text-purple-500">
            <div>Purchase intent: <strong>{formatCurrency(structured_result.proposed_amount as number, currency)}</strong></div>
            {structured_result.monthly_premium_provision !== undefined && structured_result.monthly_premium_provision !== null && (
              <div className="text-2xs text-muted mt-0.5">
                Monthly premium provision: {formatCurrency(structured_result.monthly_premium_provision as number, currency)}/mo (Annualized)
              </div>
            )}
          </Section>

          <Section icon={TrendingUp} title="Expected Impact" colorClass="bg-warning/10 text-warning">
            <div className="space-y-1">
              {structured_result.immediate_post_payment_balance !== undefined && (
                <div>Immediate post-payment balance: <strong>{formatCurrency(structured_result.immediate_post_payment_balance as number, currency)}</strong></div>
              )}
              {structured_result.balance_above_emergency_fund !== undefined && (
                <div>Balance above emergency fund: <strong>{formatCurrency(structured_result.balance_above_emergency_fund as number, currency)}</strong></div>
              )}
              <div>Projected balance: <strong>{formatCurrency(structured_result.resulting_balance as number, currency)}</strong></div>
              {(structured_result.shortfall as number) > 0 && <div>Shortfall: <strong className="text-danger">{formatCurrency(structured_result.shortfall as number, currency)}</strong></div>}
              {(structured_result.trade_off as number) > 0 && <div>Trade-off required: <strong className="text-warning">{formatCurrency(structured_result.trade_off as number, currency)}</strong></div>}
            </div>
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
              ? 'Proceed with upfront purchase as emergency reserve and safety buffer are maintained.' 
              : structured_result.viable_options && (structured_result.viable_options as any[]).length > 0 
              ? 'Upfront purchase breaches buffer. Recommend using an installment option to preserve financial health.'
              : 'Purchase is not affordable and no viable installment options were found. Delay purchase.'}
          </Section>

          {response.confidence && (
            <Section icon={Eye} title="Confidence" colorClass="bg-muted/10 text-muted">
              <div className="flex items-center gap-2">
                <span className="font-semibold uppercase tracking-wider text-xs px-2 py-0.5 rounded bg-muted/20">{response.confidence}</span>
                {Boolean(structured_result.has_conflict) && (
                  <span className="text-2xs text-muted">(Adjusted due to scenario variance vs profile on record)</span>
                )}
              </div>
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

      {intent === 'SPENDING_ANALYSIS' && structured_result && (
        <>
          {structured_result.queried_merchant && structured_result.queried_merchant_amount !== undefined && (
            <div className="mb-3 p-3.5 rounded-xl bg-primary-accent/10 border border-primary-accent/30 text-sm">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs uppercase font-bold tracking-wider text-primary-accent">Detected App & Merchant</span>
                  <div className="text-base font-bold text-primary-dark mt-0.5">
                    {structured_result.queried_merchant as string}
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xs text-muted block">Direct Spend</span>
                  <span className="text-base font-bold text-primary-dark">
                    {formatCurrency(structured_result.queried_merchant_amount as number, currency)}
                  </span>
                </div>
              </div>
              {structured_result.queried_category && (
                <div className="mt-2 text-xs text-muted">
                  Auto-categorized under: <strong className="capitalize text-primary-dark">{structured_result.queried_category as string}</strong>
                </div>
              )}
            </div>
          )}

          <Section icon={PieChartIcon} title="Category-Wise Distribution & Recognized Apps" colorClass="bg-primary-accent/10 text-primary-accent">
            <div className="space-y-3">
              {Array.isArray(structured_result.category_distribution) && structured_result.category_distribution.length > 0 ? (
                (structured_result.category_distribution as any[]).map((cat: any, idx: number) => (
                  <div key={idx} className="p-2.5 rounded-lg bg-background/60 border border-border/60">
                    <div className="flex items-center justify-between text-xs font-semibold text-primary-dark mb-1">
                      <span className="capitalize flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-primary-accent inline-block"></span>
                        {cat.category}
                      </span>
                      <span>
                        {formatCurrency(cat.total_amount, currency)} ({cat.percentage}%)
                      </span>
                    </div>
                    {/* Progress bar */}
                    <div className="w-full bg-border/40 h-1.5 rounded-full overflow-hidden mb-2">
                      <div
                        className="bg-primary-accent h-full rounded-full"
                        style={{ width: `${Math.min(100, Math.max(5, cat.percentage || 0))}%` }}
                      />
                    </div>
                    {/* Detected apps pills */}
                    {cat.apps && cat.apps.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-1.5 pt-1.5 border-t border-border/40">
                        <span className="text-[11px] text-muted self-center mr-1">Apps:</span>
                        {cat.apps.map((app: any, aIdx: number) => (
                          <span
                            key={aIdx}
                            className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-card-bg border border-border text-primary-dark font-medium"
                          >
                            <span>{app.name}</span>
                            <span className="text-muted font-normal">({formatCurrency(app.amount, currency)})</span>
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-xs text-muted">No categorized transactions available.</div>
              )}
            </div>
          </Section>
        </>
      )}

      {decision_trace && (
        <div className="mt-4">
          <DecisionTrace trace={decision_trace} currency={currency} />
        </div>
      )}

      {/* Top-Level Lists - only render if not already detailed in the message above */}
      {!hasBuiltInSections && (
        <>
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
        </>
      )}
    </div>
  );
};
