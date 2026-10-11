import React, { useEffect, useState } from 'react';
import { usersApi } from '../../api/users';
import type { Transaction } from '../../types';
import { formatCurrency, formatCategory } from '../../utils/format';
import { FileText, ShieldCheck, TrendingUp, TrendingDown, Clock, Tag } from 'lucide-react';
import { useSelectedUser } from '../../context/UserContext';
import { useFinancialProfile } from '../../hooks/useFinancialProfile';

export const RecentTransactions: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { selectedUserId } = useSelectedUser();
  const { data: profile } = useFinancialProfile();

  const currency = profile?.home_currency || 'INR';

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
    return (
      <section className="card p-6">
        <div className="flex items-center gap-2 mb-6">
          <FileText size={18} className="text-primary-accent" />
          <h2 className="section-title">Recent Transactions</h2>
        </div>
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="flex justify-between items-center py-2">
              <div className="flex gap-3">
                <div className="skeleton w-10 h-10 rounded-full"></div>
                <div className="flex flex-col gap-2">
                  <div className="skeleton h-4 w-32 rounded"></div>
                  <div className="skeleton h-3 w-20 rounded"></div>
                </div>
              </div>
              <div className="skeleton h-5 w-16 rounded"></div>
            </div>
          ))}
        </div>
      </section>
    );
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
    <section className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <FileText size={18} className="text-primary-accent" />
          <h2 className="section-title">Recent Transactions</h2>
        </div>
        <button className="btn-ghost text-xs text-primary-accent hover:text-primary-dark">View all</button>
      </div>

      <div className="space-y-4">
        {transactions.map(tx => (
          <div key={tx.transaction_id} className="group flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-background border border-border shadow-sm hover:border-primary-accent/30 hover:shadow-md rounded-xl transition-all duration-200">
            <div className="flex items-center gap-4">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${tx.direction === 'credit' ? 'bg-positive/10 text-positive' : 'bg-primary-dark/5 text-primary-dark'}`}>
                {tx.direction === 'credit' ? <TrendingUp size={18} /> : <TrendingDown size={18} />}
              </div>
              <div className="flex flex-col gap-1.5">
                <p className="text-sm font-semibold text-primary-dark leading-none">{tx.description}</p>
                <div className="flex items-center flex-wrap gap-2">
                  <span className="flex items-center gap-1 text-[11px] font-medium text-muted">
                    <Clock size={12} />
                    {new Date(tx.event_date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' })}
                  </span>
                  {tx.category && (
                    <span className="flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 bg-surface-2 text-primary-dark rounded-md border border-border">
                      <Tag size={10} />
                      {formatCategory(tx.category)}
                    </span>
                  )}
                  {tx.ml_confidence_level && (
                    <span className={`flex items-center gap-1 text-[10px] font-semibold px-1.5 py-0.5 rounded-md border ${getConfidenceColor(tx.ml_confidence_level)}`}>
                      <ShieldCheck size={10} />
                      {tx.ml_confidence_level.toUpperCase()}
                    </span>
                  )}
                </div>
              </div>
            </div>
            <p className={`text-base font-bold mt-3 sm:mt-0 whitespace-nowrap text-right ${tx.direction === 'credit' ? 'text-positive' : 'text-primary-dark'}`}>
              {tx.direction === 'credit' ? '+' : '-'}{formatCurrency(tx.amount, currency)}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
};
