import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Menu, Bell, RefreshCw, UserCircle, ChevronDown, Check, Settings } from 'lucide-react';
import { useSelectedUser, DEMO_USERS, DEFAULT_USER_ID } from '../../context/UserContext';

const PAGE_TITLES: Record<string, { title: string; subtitle: string }> = {
  '/dashboard': { title: 'Dashboard', subtitle: 'Your financial overview at a glance' },
  '/copilot': { title: 'Artha AI', subtitle: 'Ask questions about your money' },
  '/insights': { title: 'Insights', subtitle: 'Spending analysis and patterns' },
  '/forecast': { title: 'Forecast', subtitle: 'Projected income, expenses, and cash flow' },
  '/what-if': { title: 'What-If', subtitle: 'Simulate financial scenarios' },
  '/profile': { title: 'Profile', subtitle: 'Your financial preferences and settings' },
};

interface TopbarProps {
  onMenuClick: () => void;
  isOpen?: boolean;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const Topbar: React.FC<TopbarProps> = ({ onMenuClick, isOpen = false, onRefresh, isRefreshing }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const pageInfo = PAGE_TITLES[location.pathname] || { title: 'FIN4YOU', subtitle: '' };
  
  const { selectedUserId, setSelectedUserId } = useSelectedUser();
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const selectedUser = DEMO_USERS.find(u => u.id === selectedUserId) || DEMO_USERS[0];

  return (
    <header
      className={`fixed top-0 right-0 z-20 bg-background border-b border-border flex items-center px-5 gap-4 shadow-sm transition-all duration-250 ${isOpen ? 'lg:left-[var(--sidebar-width)] left-0' : 'left-0'}`}
      style={{
        height: 'var(--topbar-height)',
      }}
      role="banner"
    >
      {/* Mobile menu button */}
      <button
        className="p-1.5 rounded-md text-muted hover:bg-border transition-colors"
        onClick={onMenuClick}
        aria-label="Toggle navigation menu"
      >
        <Menu size={20} />
      </button>

      {/* Page title */}
      <div className="flex-1 min-w-0">
        <h1 className="text-lg font-semibold text-primary-dark truncate">{pageInfo.title}</h1>
        <p className="text-sm text-muted truncate hidden sm:block">{pageInfo.subtitle}</p>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3">
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

        {/* User Switcher */}
        <div className="relative">
          <button
            className="flex items-center gap-2 hover:bg-border rounded-lg p-1.5 transition-colors"
            onClick={() => setUserDropdownOpen(!userDropdownOpen)}
            aria-expanded={userDropdownOpen}
            aria-haspopup="listbox"
            aria-label="Switch demo user"
          >
            <div className="w-8 h-8 rounded-full bg-primary-accent/10 border border-primary-accent/20 flex items-center justify-center flex-shrink-0">
              <UserCircle size={18} className="text-primary-accent" />
            </div>
            <div className="hidden md:block text-left mr-1">
              <p className="text-sm font-semibold text-primary-dark leading-tight">{selectedUser.label}</p>
            </div>
            <ChevronDown
              size={14}
              className={`text-muted transition-transform ${userDropdownOpen ? 'rotate-180' : ''}`}
            />
          </button>

          {/* User dropdown */}
          {userDropdownOpen && (
            <div
              className="absolute top-full right-0 mt-1 w-48 bg-card-bg border border-border rounded-xl shadow-lg z-50 overflow-hidden"
              role="listbox"
            >
              <div className="px-3 py-2 border-b border-border bg-background">
                <p className="text-xs font-medium text-muted uppercase tracking-wider">Switch Account</p>
              </div>
              <div className="py-1">
                {DEMO_USERS.map((user) => (
                  <button
                    key={user.id}
                    role="option"
                    aria-selected={user.id === selectedUserId}
                    className={`w-full text-left px-3 py-2 text-sm flex items-center justify-between transition-colors ${
                      user.id === selectedUserId
                        ? 'bg-primary-accent/10 text-primary-dark font-medium'
                        : 'text-primary-dark hover:bg-background'
                    }`}
                    onClick={() => {
                      setSelectedUserId(user.id);
                      setUserDropdownOpen(false);
                    }}
                  >
                    <span>{user.label}</span>
                    {user.id === selectedUserId && (
                      <Check size={14} className="text-primary-accent" />
                    )}
                  </button>
                ))}
              </div>
              <div className="border-t border-border py-1">
                <button
                  className="w-full text-left px-3 py-2 text-sm flex items-center gap-2 text-primary-dark hover:bg-background transition-colors"
                  onClick={() => {
                    navigate('/profile');
                    setUserDropdownOpen(false);
                  }}
                >
                  <Settings size={16} className="text-muted" />
                  <span>Profile & Settings</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
