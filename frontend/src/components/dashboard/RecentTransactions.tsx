import React, { useEffect, useState } from 'react';
import { usersApi } from '../../api/users';
import type { Transaction } from '../../types';
import { formatCurrency } from '../../utils/format';
import { FileText, ShieldCheck } from 'lucide-react';
import { useSelectedUser } from '../../context/UserContext';
import { useFinancialProfile } from '../../hooks/useFinancialProfile';

export const RecentTransactions: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { selectedUserId } = useSelectedUser();
  const { data: profile } = useFinancialProfile();

  const currency = profile?.home_currency || 'EUR';

  useEffect(() => {
    const fetchTx = async () => {
      try {
        const data = await usersApi.getTransactions(5);
        setTransactions(data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchTx();
  }, [selectedUserId]);

  if (isLoading) {
    return <div className="card p-5 animate-pulse h-64 bg-background"></div>;
  }

  if (transactions.length === 0) {
    return null;
  }

  const getConfidenceColor = (level?: string) => {
    if (level === 'high') return 'text-positive bg-positive/10 border-positive/20';
    if (level === 'medium') return 'text-warning bg-warning/10 border-warning/20';
    return 'text-muted bg-muted/10 border-border';
  };

  return (
    <section className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <FileText size={16} className="text-primary-accent" />
          <h2 className="section-title">Recent Transactions</h2>
        </div>
      </div>

      <div className="space-y-3">
        {transactions.map(tx => (
          <div key={tx.transaction_id} className="flex flex-col sm:flex-row sm:items-center justify-between p-3 bg-background border border-border rounded-xl">
            <div className="flex flex-col gap-1">
              <p className="text-sm font-bold text-primary-dark">{tx.description}</p>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted">{new Date(tx.event_date).toLocaleDateString()}</span>
                {tx.category && (
                  <span className="badge-neutral text-xs">
                    {tx.category.replace(/_/g, ' ')}
                  </span>
                )}
                {tx.ml_confidence_level && (
                  <span className={`flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded-full border ${getConfidenceColor(tx.ml_confidence_level)}`}>
                    <ShieldCheck size={10} />
                    {tx.ml_confidence_level.toUpperCase()} CONFIDENCE
                  </span>
                )}
              </div>
            </div>
            <p className={`text-sm font-bold mt-2 sm:mt-0 ${tx.direction === 'credit' ? 'text-positive' : 'text-primary-dark'}`}>
              {tx.direction === 'credit' ? '+' : '-'}{formatCurrency(tx.amount, currency)}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
};
