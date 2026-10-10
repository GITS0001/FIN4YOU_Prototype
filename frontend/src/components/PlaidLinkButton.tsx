import React, { useState, useEffect, useCallback } from 'react';
import { usePlaidLink } from 'react-plaid-link';
import { Link as LinkIcon, CheckCircle } from 'lucide-react';
import { apiClient } from '../api/client';

export const PlaidLinkButton: React.FC = () => {
  const [linkToken, setLinkToken] = useState<string | null>(null);
  const [isLinked, setIsLinked] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  useEffect(() => {
    // Fetch link token from our backend
    const fetchLinkToken = async () => {
      try {
        const response = await apiClient.post('/api/plaid/link/token/create');
        setLinkToken(response.data.link_token);
      } catch (err) {
        console.error('Error fetching link token:', err);
      }
    };
    fetchLinkToken();
  }, []);

  const onSuccess = useCallback(async (publicToken: string | null, metadata: any) => {
    // Send public_token to our backend
    try {
      setIsSyncing(true);
      await apiClient.post('/api/plaid/item/public_token/exchange', {
        public_token: publicToken || ''
      });
      setIsLinked(true);

      // Auto-trigger an initial sync of transactions
      await apiClient.post('/api/plaid/transactions/sync');

      setIsSyncing(false);
      // Reload page to show new transactions
      window.location.reload();
    } catch (err) {
      console.error('Error exchanging public token or syncing:', err);
      setIsSyncing(false);
    }
  }, []);

  const config = {
    token: linkToken!,
    onSuccess,
  };

  const { open, ready } = usePlaidLink(config);

  if (isLinked) {
    return (
      <div className="flex items-center gap-2 text-emerald-600 bg-emerald-500/10 px-4 py-2 rounded-lg font-bold border border-emerald-500/20">
        <CheckCircle size={18} />
        Bank Account Connected
      </div>
    );
  }

  return (
    <button
      onClick={() => open()}
      disabled={!ready || !linkToken || isSyncing}
      className="btn-primary flex items-center gap-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50"
    >
      <LinkIcon size={18} />
      {isSyncing ? 'Syncing Transactions...' : 'Connect Bank Account'}
    </button>
  );
};
