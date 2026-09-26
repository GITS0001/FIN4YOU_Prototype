import React from 'react';
import { AlertCircle, WifiOff, Database, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  type?: 'connection' | 'data' | 'generic';
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title,
  message,
  onRetry,
  type = 'generic',
}) => {
  const icons = {
    connection: WifiOff,
    data: Database,
    generic: AlertCircle,
  };

  const defaultTitles = {
    connection: "Couldn't connect to the financial engine",
    data: "Couldn't retrieve your financial data",
    generic: "Something went wrong",
  };

  const defaultMessages = {
    connection:
      "Please ensure the FIN4YOU backend is running on localhost:8000 and try again.",
    data: "We couldn't load this information. Please try again.",
    generic: "An unexpected error occurred. Please try again.",
  };

  const Icon = icons[type];
  const displayTitle = title || defaultTitles[type];
  const displayMessage = message || defaultMessages[type];

  return (
    <div
      className="flex flex-col items-center justify-center py-16 px-6 text-center"
      role="alert"
      aria-live="polite"
    >
      <div className="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center mb-4">
        <Icon size={22} className="text-danger" aria-hidden="true" />
      </div>
      <h3 className="text-[15px] font-semibold text-primary-dark mb-1">{displayTitle}</h3>
      <p className="text-sm text-muted max-w-xs mb-5">{displayMessage}</p>
      {onRetry && (
        <button className="btn-secondary flex items-center gap-2" onClick={onRetry}>
          <RefreshCw size={14} aria-hidden="true" />
          Try again
        </button>
      )}
    </div>
  );
};

interface EmptyStateProps {
  title: string;
  message: string;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ title, message, action }) => (
  <div className="flex flex-col items-center justify-center py-12 px-6 text-center">
    <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center mb-4">
      <Database size={22} className="text-muted" aria-hidden="true" />
    </div>
    <h3 className="text-[15px] font-semibold text-primary-dark mb-1">{title}</h3>
    <p className="text-sm text-muted max-w-xs mb-4">{message}</p>
    {action}
  </div>
);
