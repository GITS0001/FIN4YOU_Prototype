import React from 'react';
import type { ChatMessage as ChatMessageType } from '../../types';
import { DecisionTrace } from '../shared/DecisionTrace';
import { ConfidenceBadge } from '../shared/ConfidenceBadge';
import { PaymentOptionCard } from '../shared/PaymentOptionCard';
import { formatCurrency } from '../../utils/format';
import { Bot, User } from 'lucide-react';

interface ChatMessageProps {
  message: ChatMessageType;
  currency: string;
}

const AffordabilityCard: React.FC<{
  result: Record<string, unknown>;
  currency: string;
}> = ({ result, currency }) => {
  const status = result.affordability_status as string;
  const balance = result.resulting_balance as number;
  const tradeOff = result.trade_off as number;

  const statusConfig: Record<string, { color: string; badge: string }> = {
    AFFORDABLE: { color: 'text-positive', badge: 'badge-positive' },
    'POTENTIALLY AFFORDABLE WITH TRADE-OFF': { color: 'text-warning', badge: 'badge-warning' },
    'NOT AFFORDABLE UNDER CURRENT PROJECTION': { color: 'text-danger', badge: 'badge-danger' },
    'INSUFFICIENT DATA': { color: 'text-muted', badge: 'badge-neutral' },
  };

  const config = statusConfig[status] || statusConfig['INSUFFICIENT DATA'];

  return (
    <div className="mt-3 bg-background rounded-xl border border-border p-4">
      <p className="label-sm mb-2">Affordability Analysis</p>
      <span className={config.badge}>{status}</span>

      {balance !== undefined && (
        <div className="grid grid-cols-2 gap-3 mt-3">
          <div>
            <p className="text-xs text-muted">Projected Balance</p>
            <p className={`text-sm font-semibold ${config.color}`}>
              {formatCurrency(balance, currency)}
            </p>
          </div>
          {tradeOff !== undefined && tradeOff > 0 && (
            <div>
              <p className="text-xs text-muted">Required Trade-Off</p>
              <p className="text-sm font-semibold text-warning">
                {formatCurrency(tradeOff, currency)}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const PaymentOptionsCard: React.FC<{
  result: Record<string, unknown>;
  currency: string;
}> = ({ result, currency }) => {
  const options = result.viable_options as Array<Record<string, unknown>>;
  if (!options || options.length === 0) return null;

  return (
    <div className="mt-3 bg-background rounded-xl border border-border p-4">
      <p className="label-sm mb-3">Viable Payment Options</p>
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        {options.map((opt) => (
          <PaymentOptionCard
            key={opt.payment_option_id as string}
            option={opt as unknown as Parameters<typeof PaymentOptionCard>[0]['option']}
            currency={currency}
          />
        ))}
      </div>
    </div>
  );
};

const CashFlowCard: React.FC<{
  result: Record<string, unknown>;
  currency: string;
}> = ({ result, currency }) => {
  const cashFlow = result.projected_cash_flow as number;
  const balance = result.projected_balance as number;

  return (
    <div className="mt-3 bg-background rounded-xl border border-border p-4">
      <p className="label-sm mb-3">Cash Flow Forecast</p>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <p className="text-xs text-muted">Projected Cash Flow</p>
          <p className={`text-sm font-semibold ${cashFlow >= 0 ? 'text-positive' : 'text-danger'}`}>
            {formatCurrency(cashFlow, currency)}
          </p>
        </div>
        <div>
          <p className="text-xs text-muted">Projected Balance</p>
          <p className={`text-sm font-semibold ${balance >= 0 ? 'text-positive' : 'text-danger'}`}>
            {formatCurrency(balance, currency)}
          </p>
        </div>
      </div>
    </div>
  );
};

const WhatIfCard: React.FC<{
  result: Record<string, unknown>;
  currency: string;
}> = ({ result, currency }) => {
  const balance = result.projected_balance as number;
  const bufferStatus = result.buffer_status_change as string;

  return (
    <div className="mt-3 bg-background rounded-xl border border-border p-4">
      <p className="label-sm mb-3">Scenario Result</p>
      <div className="grid grid-cols-2 gap-3">
        {balance !== undefined && (
          <div>
            <p className="text-xs text-muted">New Balance</p>
            <p className={`text-sm font-semibold ${balance >= 0 ? 'text-positive' : 'text-danger'}`}>
              {formatCurrency(balance, currency)}
            </p>
          </div>
        )}
        {bufferStatus && (
          <div>
            <p className="text-xs text-muted">Buffer Status</p>
            <p className="text-sm font-semibold text-primary-dark capitalize">{bufferStatus}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, currency }) => {
  const isUser = message.role === 'user';
  const response = message.response;

  if (isUser) {
    return (
      <div className="flex justify-end gap-2 animate-slide-up">
        <div className="chat-bubble-user max-w-sm">{message.content}</div>
        <div className="w-7 h-7 rounded-full bg-primary-accent flex items-center justify-center flex-shrink-0 mt-0.5">
          <User size={14} className="text-white" aria-hidden="true" />
        </div>
      </div>
    );
  }

  // AI message
  return (
    <div className="flex gap-2 animate-slide-up">
      <div className="w-7 h-7 rounded-full bg-sidebar-bg flex items-center justify-center flex-shrink-0 mt-0.5">
        <Bot size={14} className="text-white" aria-hidden="true" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="chat-bubble-ai">
          <p className="leading-relaxed whitespace-pre-wrap">{message.content}</p>

          {/* Structured result rendering */}
          {response?.structured_result && response.intent === 'AFFORDABILITY_CHECK' && (
            <AffordabilityCard result={response.structured_result} currency={currency} />
          )}
          {response?.structured_result && response.intent === 'PAYMENT_OPTION_ANALYSIS' && (
            <PaymentOptionsCard result={response.structured_result} currency={currency} />
          )}
          {response?.structured_result && response.intent === 'CASH_FLOW_FORECAST' && (
            <CashFlowCard result={response.structured_result} currency={currency} />
          )}
          {response?.structured_result && response.intent === 'WHAT_IF' && (
            <WhatIfCard result={response.structured_result} currency={currency} />
          )}

          {/* Decision trace */}
          {response?.decision_trace && (
            <DecisionTrace trace={response.decision_trace} currency={currency} />
          )}

          {/* Footer: confidence + data sources */}
          {response && (
            <div className="flex items-center justify-between mt-3 pt-2 border-t border-border/50">
              <ConfidenceBadge confidence={response.confidence} />
              {response.data_sources?.length > 0 && (
                <span className="text-2xs text-muted/60 truncate max-w-[160px]" title={response.data_sources.join(', ')}>
                  {response.data_sources[0]}{response.data_sources.length > 1 ? ` +${response.data_sources.length - 1}` : ''}
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
