import React from 'react';
import type { PaymentOption } from '../../types';
import { formatCurrency, formatDate } from '../../utils/format';
import { CreditCard, Calendar, Percent } from 'lucide-react';

interface PaymentOptionCardProps {
  option: PaymentOption;
  currency: string;
  isSelected?: boolean;
  onSelect?: (id: string) => void;
}

export const PaymentOptionCard: React.FC<PaymentOptionCardProps> = ({
  option,
  currency,
  isSelected,
  onSelect,
}) => {
  const isInstallment = option.number_of_payments > 1;

  return (
    <button
      className={`
        w-full text-left card p-4 transition-all duration-150 border-2
        ${isSelected
          ? 'border-primary-accent bg-primary-accent/10'
          : 'border-transparent hover:border-border hover:shadow-card-hover'
        }
      `}
      onClick={() => onSelect?.(option.payment_option_id)}
      aria-pressed={isSelected}
      aria-label={`${option.payment_method}: ${formatCurrency(option.payment_amount, currency)}`}
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <div>
          <span className="badge-info mb-1">{option.payment_method.replace(/_/g, ' ')}</span>
          <p className="text-base font-semibold text-primary-dark mt-1">
            {formatCurrency(option.payment_amount, currency)}
            {isInstallment && (
              <span className="text-xs font-normal text-muted"> / payment</span>
            )}
          </p>
        </div>
        <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${isSelected ? 'bg-primary-accent' : 'bg-background'}`}>
          {isSelected && (
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
              <path d="M2 6l3 3 5-5" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="flex items-center gap-1.5 text-muted">
          <CreditCard size={11} aria-hidden="true" />
          <span>{option.number_of_payments}x payment{option.number_of_payments > 1 ? 's' : ''}</span>
        </div>
        <div className="flex items-center gap-1.5 text-muted">
          <Percent size={11} aria-hidden="true" />
          <span>Fee: {formatCurrency(option.financing_fee, currency)}</span>
        </div>
        <div className="flex items-center gap-1.5 text-muted col-span-2">
          <Calendar size={11} aria-hidden="true" />
          <span>First payment: {formatDate(option.first_payment_date)}</span>
        </div>
      </div>

      <div className="mt-3 pt-2 border-t border-border flex items-center justify-between">
        <p className="text-xs text-muted">Total payable</p>
        <p className="text-sm font-semibold text-primary-dark">
          {formatCurrency(option.total_payable_amount, currency)}
        </p>
      </div>
    </button>
  );
};
