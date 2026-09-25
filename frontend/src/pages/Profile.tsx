import React from 'react';
import { useFinancialProfile } from '../hooks/useFinancialProfile';
import { ErrorState } from '../components/shared/ErrorState';
import { LoadingSkeleton } from '../components/shared/LoadingSkeleton';
import { formatCurrency, formatCategory } from '../utils/format';
import {
  User,
  Shield,
  CreditCard,
  Wallet,
  Tag,
  AlertCircle,
} from 'lucide-react';

export const Profile: React.FC = () => {
  const { data: profile, status, error, refetch } = useFinancialProfile();

  if (status === 'error') {
    return <ErrorState type="data" message={error?.message} onRetry={refetch} />;
  }

  const isLoading = status === 'loading';

  const sections = [
    {
      icon: Wallet,
      title: 'Balance',
      items: [
        {
          label: 'User ID',
          value: profile?.user_id,
        },
        {
          label: 'Home Currency',
          value: profile?.home_currency,
        },
        {
          label: 'Available Balance',
          value: profile ? formatCurrency(profile.current_available_balance, profile.home_currency) : undefined,
        },
        {
          label: 'Minimum Balance (Buffer)',
          value: profile ? formatCurrency(profile.minimum_balance_to_keep, profile.home_currency) : undefined,
        },
      ],
    },
    {
      icon: Shield,
      title: 'Financial Priorities',
      listItems: profile?.financial_priorities,
    },
    {
      icon: Tag,
      title: 'Protected Categories',
      listItems: profile?.expense_categories_to_protect,
      description: 'These categories will not be reduced in recommendations.',
    },
    {
      icon: AlertCircle,
      title: 'Reducible Categories',
      listItems: profile?.expense_categories_user_is_willing_to_reduce,
      description: 'You are open to reducing spending in these areas.',
    },
    {
      icon: AlertCircle,
      title: 'Stoppable Categories',
      listItems: profile?.expense_categories_user_is_willing_to_stop,
      description: 'You are willing to stop spending in these categories.',
    },
    {
      icon: CreditCard,
      title: 'Payment Methods',
      listItems: profile?.payment_methods_user_will_consider,
      extra: profile?.max_installment_months
        ? `Max installment period: ${profile.max_installment_months} months`
        : undefined,
    },
  ];

  return (
    <div className="space-y-6 max-w-2xl">
      {/* Header */}
      <div className="flex items-center gap-4">
        <div className="w-14 h-14 bg-primary-accent rounded-2xl flex items-center justify-center">
          <User size={24} className="text-white" aria-hidden="true" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-primary-dark">Yash</h1>
          {isLoading ? (
            <LoadingSkeleton height="h-4" className="w-32 mt-1" />
          ) : (
            <p className="text-muted text-sm mt-0.5">
              {profile?.user_id} · {profile?.home_currency}
            </p>
          )}
        </div>
      </div>

      {/* Profile sections */}
      {sections.map((section) => (
        <section key={section.title} className="card p-5" aria-labelledby={`section-${section.title.replace(/\s+/g, '-').toLowerCase()}`}>
          <div className="flex items-center gap-2 mb-4">
            <section.icon size={16} className="text-muted" aria-hidden="true" />
            <h2
              id={`section-${section.title.replace(/\s+/g, '-').toLowerCase()}`}
              className="section-title"
            >
              {section.title}
            </h2>
          </div>

          {section.description && (
            <p className="text-xs text-muted mb-3">{section.description}</p>
          )}

          {/* Key-value pairs */}
          {'items' in section && section.items && (
            <div className="space-y-3">
              {section.items.map((item) => (
                <div key={item.label} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                  <p className="text-sm text-muted">{item.label}</p>
                  {isLoading ? (
                    <LoadingSkeleton height="h-4" className="w-28" />
                  ) : (
                    <p className="text-sm font-semibold text-primary-dark">{item.value || '—'}</p>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Tag list */}
          {'listItems' in section && (
            <>
              {isLoading ? (
                <div className="flex flex-wrap gap-2">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="skeleton h-6 w-20 rounded-full" aria-hidden="true" />
                  ))}
                </div>
              ) : section.listItems && section.listItems.length > 0 ? (
                <div className="flex flex-wrap gap-2" role="list">
                  {section.listItems.map((item) => (
                    <span key={item} className="badge-neutral" role="listitem">
                      {formatCategory(item)}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted">None configured</p>
              )}
              {section.extra && (
                <p className="text-xs text-muted mt-3">{section.extra}</p>
              )}
            </>
          )}
        </section>
      ))}

      {/* Data note */}
      <p className="text-xs text-muted/70 text-center pb-4">
        Profile data is read from the FIN4YOU data directory. Contact your administrator to update preferences.
      </p>
    </div>
  );
};
