import React, { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Menu, Bell, RefreshCw, ChevronDown, Check, Settings, Sun, Moon, LogOut, ChevronRight } from 'lucide-react';
import { useSelectedUser } from '../../context/UserContext';
import { useTheme } from '../../hooks/useTheme';
import { useAuth } from '../../context/AuthContext';
import { useFinancialProfile } from '../../hooks/useFinancialProfile';
import { useAlerts } from '../../hooks/useAlerts';

interface TopbarProps {
  onMenuClick: () => void;
  isOpen?: boolean;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

const PAGE_META: Record<string, { title: string; section: string }> = {
  '/dashboard': { title: 'Dashboard', section: 'Overview' },
  '/copilot': { title: 'Artha AI', section: 'Overview' },
  '/insights': { title: 'Insights', section: 'Analyze' },
  '/forecast': { title: 'Forecast', section: 'Analyze' },
  '/statement': { title: 'Statement', section: 'Analyze' },
  '/what-if': { title: 'What-If Simulator', section: 'Plan' },
  '/affordability': { title: 'Affordability', section: 'Plan' },
  '/profile': { title: 'Profile & Settings', section: 'Account' },
};

export const initialsOf = (name: string) =>
  name
    .replace(/\(.*?\)/g, '')
    .trim()
    .split(/\s+/)
    .map((p) => p[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

export const Topbar: React.FC<TopbarProps> = ({ onMenuClick, isOpen = false, onRefresh, isRefreshing }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { selectedUserId, setSelectedUserId } = useSelectedUser();
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [alertsDropdownOpen, setAlertsDropdownOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const alertsRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const { logout } = useAuth();
  const { data: profile } = useFinancialProfile();
  const { data: alerts } = useAlerts();

  const { theme, toggleTheme } = useTheme();
  const meta = PAGE_META[location.pathname] ?? { title: 'FIN4YOU', section: '' };

  const displayName = profile?.full_name || 'User';
  const displayCurrency = profile?.home_currency || 'USD';

  // Close dropdown on outside click / Escape
  useEffect(() => {
    const onDown = (e: MouseEvent) => {
      if (userDropdownOpen && menuRef.current && !menuRef.current.contains(e.target as Node)) setUserDropdownOpen(false);
      if (alertsDropdownOpen && alertsRef.current && !alertsRef.current.contains(e.target as Node)) setAlertsDropdownOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setUserDropdownOpen(false);
        setAlertsDropdownOpen(false);
        triggerRef.current?.focus();
      }
    };
    document.addEventListener('mousedown', onDown);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onDown);
      document.removeEventListener('keydown', onKey);
    };
  }, [userDropdownOpen, alertsDropdownOpen]);

  return (
    <header
      className={`fixed top-0 right-0 z-20 bg-background/75 backdrop-blur-xl border-b border-border flex items-center gap-3 px-4 sm:px-6 lg:px-8 transition-[left] duration-300 ${
        isOpen ? 'lg:left-[var(--sidebar-width)] left-0' : 'left-0'
      }`}
      style={{ height: 'var(--topbar-height)' }}
      role="banner"
    >
      <button className="icon-btn lg:hidden -ml-1" onClick={onMenuClick} aria-label="Toggle navigation menu">
        <Menu size={20} />
      </button>

      {/* Left: page context */}
      <div className="flex-1 min-w-0">
        {meta.section && (
          <nav aria-label="Breadcrumb" className="hidden sm:flex items-center gap-1 text-[11px] font-medium text-subtle leading-none mb-1">
            <span>{meta.section}</span>
            <ChevronRight size={11} aria-hidden="true" />
            <span className="text-muted">{meta.title}</span>
          </nav>
        )}
        <p className="font-display text-[17px] font-semibold text-primary-dark leading-tight truncate">{meta.title}</p>
      </div>

      {/* Right: actions */}
      <div className="flex items-center gap-1 sm:gap-1.5">
        {onRefresh && (
          <button className="btn-ghost btn-sm" onClick={onRefresh} disabled={isRefreshing} aria-label="Refresh data">
            <RefreshCw size={15} className={isRefreshing ? 'animate-spin' : ''} />
            <span className="hidden sm:inline">Refresh</span>
          </button>
        )}

        <button
          onClick={toggleTheme}
          className="icon-btn relative overflow-hidden"
          aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
        >
          <Sun
            size={18}
            className={`absolute transition-all duration-300 ${theme === 'dark' ? 'rotate-0 scale-100 opacity-100' : '-rotate-90 scale-50 opacity-0'}`}
          />
          <Moon
            size={18}
            className={`absolute transition-all duration-300 ${theme === 'dark' ? 'rotate-90 scale-50 opacity-0' : 'rotate-0 scale-100 opacity-100'}`}
          />
        </button>

        <div className="relative" ref={alertsRef}>
          <button
            className="icon-btn relative"
            aria-label="Notifications"
            title="Notifications"
            onClick={() => setAlertsDropdownOpen(o => !o)}
          >
            <Bell size={18} />
            {alerts && alerts.length > 0 && (
              <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-danger ring-2 ring-background" aria-hidden="true" />
            )}
          </button>

          {alertsDropdownOpen && (
            <div className="absolute top-full right-0 mt-2 w-80 bg-card-bg border border-border rounded-2xl shadow-[var(--shadow-dropdown)] z-50 overflow-hidden animate-scale-in">
              <div className="px-4 py-3.5 border-b border-border flex items-center justify-between">
                <h3 className="text-sm font-semibold text-primary-dark">Notifications</h3>
                {alerts && alerts.length > 0 && <span className="badge-danger">{alerts.length} new</span>}
              </div>
              <div className="max-h-80 overflow-y-auto p-1.5">
                {(!alerts || alerts.length === 0) ? (
                  <div className="px-4 py-6 text-center text-sm text-muted">No new notifications</div>
                ) : (
                  alerts.map((alert, i) => (
                    <div key={i} className="px-3 py-2.5 hover:bg-surface-2 rounded-xl transition-colors cursor-pointer mb-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`w-2 h-2 rounded-full flex-shrink-0 ${alert.type === 'danger' ? 'bg-danger' : alert.type === 'warning' ? 'bg-warning' : 'bg-primary-accent'}`} />
                        <h4 className="text-sm font-semibold text-primary-dark">{alert.title}</h4>
                      </div>
                      <p className="text-xs text-muted leading-relaxed ml-4">{alert.message}</p>
                      <p className="text-[10px] text-muted/70 ml-4 mt-1">{alert.timestamp}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        <div className="w-px h-6 bg-border mx-1.5 hidden sm:block" aria-hidden="true" />

        {/* User Profile */}
        <div className="relative" ref={menuRef}>
          <button
            ref={triggerRef}
            className="flex items-center gap-2.5 hover:bg-surface-2 rounded-[12px] pl-1 pr-2 py-1 transition-colors"
            onClick={() => setUserDropdownOpen((o) => !o)}
            aria-expanded={userDropdownOpen}
            aria-haspopup="menu"
          >
            <div className="w-8 h-8 rounded-full bg-brand-gradient text-white text-xs font-semibold flex items-center justify-center flex-shrink-0 ring-2 ring-card-bg shadow-sm">
              {initialsOf(displayName)}
            </div>
            <div className="hidden md:block text-left">
              <p className="text-sm font-semibold text-primary-dark leading-tight">{displayName}</p>
              <p className="text-[11px] text-muted leading-tight">{displayCurrency} · Personal</p>
            </div>
            <ChevronDown size={14} className={`text-muted transition-transform duration-200 ${userDropdownOpen ? 'rotate-180' : ''}`} />
          </button>

          {userDropdownOpen && (
            <div
              className="absolute top-full right-0 mt-2 w-64 bg-card-bg border border-border rounded-2xl shadow-[var(--shadow-dropdown)] z-50 overflow-hidden animate-scale-in"
              role="menu"
            >
              <div className="px-4 py-3.5 flex items-center gap-3 border-b border-border">
                <div className="w-10 h-10 rounded-full bg-brand-gradient text-white text-sm font-semibold flex items-center justify-center">
                  {initialsOf(displayName)}
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-primary-dark truncate">{displayName}</p>
                  <p className="text-xs text-muted truncate">{profile?.email || 'user@example.com'}</p>
                </div>
              </div>
              <div className="p-1.5">
                <button
                  role="menuitem"
                  className="w-full text-left px-2.5 h-9 rounded-lg text-sm flex items-center gap-2.5 text-primary-dark hover:bg-surface-2 transition-colors"
                  onClick={() => {
                    navigate('/profile');
                    setUserDropdownOpen(false);
                  }}
                >
                  <Settings size={16} className="text-muted" />
                  <span>Profile & Settings</span>
                </button>
                <button
                  role="menuitem"
                  className="w-full text-left px-2.5 h-9 rounded-lg text-sm flex items-center gap-2.5 text-danger hover:bg-danger/10 transition-colors"
                  onClick={() => {
                    logout();
                    navigate('/login');
                    setUserDropdownOpen(false);
                  }}
                >
                  <LogOut size={16} />
                  <span>Log out</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
