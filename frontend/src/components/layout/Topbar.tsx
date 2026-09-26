import React from 'react';
import { useLocation } from 'react-router-dom';
import { Menu, Bell, RefreshCw } from 'lucide-react';

const PAGE_TITLES: Record<string, { title: string; subtitle: string }> = {
  '/dashboard': { title: 'Dashboard', subtitle: 'Your financial overview at a glance' },
  '/copilot': { title: 'AI Copilot', subtitle: 'Ask questions about your money' },
  '/insights': { title: 'Insights', subtitle: 'Spending analysis and patterns' },
  '/forecast': { title: 'Forecast', subtitle: 'Projected income, expenses, and cash flow' },
  '/what-if': { title: 'What-If', subtitle: 'Simulate financial scenarios' },
  '/profile': { title: 'Profile', subtitle: 'Your financial preferences and settings' },
};

interface TopbarProps {
  onMenuClick: () => void;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const Topbar: React.FC<TopbarProps> = ({ onMenuClick, onRefresh, isRefreshing }) => {
  const location = useLocation();
  const pageInfo = PAGE_TITLES[location.pathname] || { title: 'FIN4YOU', subtitle: '' };

  return (
    <header
      className="fixed top-0 right-0 z-20 bg-background border-b border-border flex items-center px-5 gap-4"
      style={{
        height: 'var(--topbar-height)',
        left: 'var(--sidebar-width)',
      }}
      role="banner"
    >
      {/* Mobile menu button */}
      <button
        className="lg:hidden p-1.5 rounded-md text-muted hover:bg-border transition-colors"
        onClick={onMenuClick}
        aria-label="Open navigation menu"
      >
        <Menu size={20} />
      </button>

      {/* Page title */}
      <div className="flex-1 min-w-0">
        <h1 className="text-[15px] font-semibold text-primary-dark truncate">{pageInfo.title}</h1>
        <p className="text-xs text-muted truncate hidden sm:block">{pageInfo.subtitle}</p>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        {onRefresh && (
          <button
            className="btn-ghost"
            onClick={onRefresh}
            disabled={isRefreshing}
            aria-label="Refresh data"
          >
            <RefreshCw size={15} className={isRefreshing ? 'animate-spin' : ''} />
            <span className="hidden sm:inline">Refresh</span>
          </button>
        )}

        <button
          className="p-1.5 rounded-md text-muted hover:bg-border transition-colors relative"
          aria-label="Notifications"
        >
          <Bell size={18} />
        </button>

        {/* User avatar */}
        <div
          className="w-8 h-8 rounded-full bg-primary-accent text-white flex items-center justify-center text-xs font-semibold flex-shrink-0"
          aria-label="User account: Yash"
        >
          Y
        </div>
      </div>
    </header>
  );
};
