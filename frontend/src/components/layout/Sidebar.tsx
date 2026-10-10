import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import {
  LayoutDashboard,
  CreditCard,
  FileText,
  Bot,
  BarChart2,
  TrendingUp,
  GitFork,
  X,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { useBackendStatus } from '../../hooks/useBackendStatus';

interface NavItem {
  path: string;
  label: string;
  icon: LucideIcon;
  badge?: string;
}

const NAV_GROUPS: { title: string; items: NavItem[] }[] = [
  {
    title: 'Overview',
    items: [
      { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
      { path: '/copilot', label: 'Artha AI', icon: Bot, badge: 'AI' },
    ],
  },
  {
    title: 'Analyze',
    items: [
      { path: '/insights', label: 'Insights', icon: BarChart2 },
      { path: '/forecast', label: 'Forecast', icon: TrendingUp },
      { path: '/statement', label: 'Statement', icon: FileText },
    ],
  },
  {
    title: 'Plan',
    items: [
      { path: '/what-if', label: 'What-If', icon: GitFork },
      { path: '/affordability', label: 'Affordability', icon: CreditCard },
    ],
  },
];

import fin4youLogo from '../../assets/fin4you_logo.jpg';

/** Brand mark */
export const BrandMark: React.FC<{ size?: number }> = ({ size = 32 }) => (
  <div
    className="rounded-[10px] flex items-center justify-center shadow-sm flex-shrink-0 overflow-hidden"
    style={{ width: size, height: size }}
    aria-hidden="true"
  >
    <img src={fin4youLogo} alt="FIN4YOU Logo" className="w-full h-full object-cover" />
  </div>
);

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = true, onClose }) => {
  const { status } = useBackendStatus();

  const statusMeta = {
    checking: { dot: 'bg-warning', label: 'Connecting…', sub: 'Reaching data service' },
    online: { dot: 'bg-positive', label: 'Live data', sub: 'All systems operational' },
    offline: { dot: 'bg-danger', label: 'Offline', sub: 'Showing cached data' },
  }[status as 'checking' | 'online' | 'offline'] ?? { dot: 'bg-muted', label: 'Unknown', sub: '' };

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && onClose && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 lg:hidden animate-fade-in"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`
          fixed top-0 left-0 h-full z-40 flex flex-col
          bg-sidebar-bg border-r border-border text-sidebar-text
          transition-transform duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] shadow-2xl lg:shadow-none
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
        style={{ width: 'var(--sidebar-width)' }}
        aria-label="Sidebar navigation"
      >
        {/* Logo */}
        <div className="px-5 flex items-center justify-between border-b border-border" style={{ height: 'var(--topbar-height)' }}>
          <Link to="/" className="flex items-center gap-2.5 group">
            <BrandMark />
            <div className="leading-none">
              <span className="block font-display font-bold text-primary-dark text-[17px] tracking-tight">FIN4YOU</span>
              <span className="block text-[10px] font-medium text-muted mt-1 tracking-wide">Financial Intelligence</span>
            </div>
          </Link>
          {onClose && (
            <button className="icon-btn lg:hidden" onClick={onClose} aria-label="Close navigation">
              <X size={18} />
            </button>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-5 overflow-y-auto space-y-6" role="navigation">
          {NAV_GROUPS.map((group) => (
            <div key={group.title}>
              <p className="text-overline px-3 mb-2 text-subtle">{group.title}</p>
              <ul className="space-y-0.5" role="list">
                {group.items.map((item) => (
                  <li key={item.path}>
                    <NavLink
                      to={item.path}
                      className={({ isActive }) =>
                        `group relative w-full flex items-center gap-3 px-3 h-10 rounded-[10px] text-sm font-medium transition-all duration-150 ${
                          isActive
                            ? 'bg-primary-accent/10 text-primary-accent'
                            : 'text-muted hover:bg-surface-2 hover:text-primary-dark'
                        }`
                      }
                      onClick={() => {
                        if (window.innerWidth < 1024 && onClose) onClose();
                      }}
                    >
                      {({ isActive }) => (
                        <>
                          <span
                            className={`absolute left-0 top-1/2 -translate-y-1/2 w-[3px] rounded-r-full bg-primary-accent transition-all duration-200 ${
                              isActive ? 'h-5 opacity-100' : 'h-0 opacity-0'
                            }`}
                            aria-hidden="true"
                          />
                          <item.icon size={18} strokeWidth={isActive ? 2.25 : 1.9} className="flex-shrink-0" />
                          <span className="flex-1">{item.label}</span>
                          {item.badge && (
                            <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-md bg-brand-gradient text-white leading-none">
                              {item.badge}
                            </span>
                          )}
                        </>
                      )}
                    </NavLink>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>

        {/* Backend Status */}
        <div className="p-3 border-t border-border">
          <div className="panel px-3 py-2.5 flex items-center gap-3" role="status">
            <span className="relative flex h-2.5 w-2.5">
              {status !== 'offline' && (
                <span className={`absolute inline-flex h-full w-full rounded-full ${statusMeta.dot} opacity-60 animate-ping`} />
              )}
              <span className={`relative inline-flex h-2.5 w-2.5 rounded-full ${statusMeta.dot}`} />
            </span>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-primary-dark leading-tight">{statusMeta.label}</p>
              <p className="text-[11px] text-muted leading-tight mt-0.5 truncate">{statusMeta.sub}</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
