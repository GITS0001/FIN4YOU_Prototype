import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Bot,
  BarChart2,
  TrendingUp,
  GitFork,
  UserCircle,
  Settings,
  Activity,
  Wifi,
  WifiOff,
  Loader2,
  ChevronRight,
} from 'lucide-react';
import { useBackendStatus } from '../../hooks/useBackendStatus';

interface NavItemDef {
  path: string;
  label: string;
  icon: React.ElementType;
}

const NAV_ITEMS: NavItemDef[] = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/copilot', label: 'AI Copilot', icon: Bot },
  { path: '/insights', label: 'Insights', icon: BarChart2 },
  { path: '/forecast', label: 'Forecast', icon: TrendingUp },
  { path: '/what-if', label: 'What-If', icon: GitFork },
  { path: '/profile', label: 'Profile', icon: UserCircle },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = true, onClose }) => {
  const { status } = useBackendStatus();
  const location = useLocation();

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && onClose && (
        <div
          className="fixed inset-0 bg-black/40 z-30 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`
          fixed top-0 left-0 h-full z-40 flex flex-col
          bg-sidebar-bg text-sidebar-text
          transition-transform duration-250 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0 lg:static lg:z-auto
        `}
        style={{ width: 'var(--sidebar-width)' }}
        aria-label="Main navigation"
      >
        {/* Logo */}
        <div className="flex items-center gap-2.5 px-5 py-5 border-b border-white/10">
          <div className="w-8 h-8 bg-primary-accent rounded-lg flex items-center justify-center flex-shrink-0">
            <Activity size={16} className="text-white" />
          </div>
          <div>
            <span className="font-bold text-white text-[15px] tracking-tight">FIN4YOU</span>
            <p className="text-2xs text-sidebar-text leading-none mt-0.5">Financial AI</p>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 overflow-y-auto" role="navigation">
          <p className="label-sm text-white/30 px-3 mb-2">Main</p>
          <ul className="space-y-0.5" role="list">
            {NAV_ITEMS.slice(0, 5).map((item) => (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    isActive ? 'nav-item-active' : 'nav-item'
                  }
                  onClick={onClose}
                  aria-current={location.pathname === item.path ? 'page' : undefined}
                >
                  <item.icon size={17} aria-hidden="true" />
                  <span className="flex-1">{item.label}</span>
                  {location.pathname === item.path && (
                    <ChevronRight size={14} className="opacity-60" aria-hidden="true" />
                  )}
                </NavLink>
              </li>
            ))}
          </ul>

          <p className="label-sm text-white/30 px-3 mt-5 mb-2">Account</p>
          <ul className="space-y-0.5" role="list">
            {NAV_ITEMS.slice(5).map((item) => (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    isActive ? 'nav-item-active' : 'nav-item'
                  }
                  onClick={onClose}
                >
                  <item.icon size={17} aria-hidden="true" />
                  <span className="flex-1">{item.label}</span>
                </NavLink>
              </li>
            ))}
            <li>
              <button
                className="nav-item w-full text-left"
                aria-label="Settings"
              >
                <Settings size={17} aria-hidden="true" />
                <span className="flex-1">Settings</span>
              </button>
            </li>
          </ul>
        </nav>

        {/* Backend Status */}
        <div className="px-4 py-4 border-t border-white/10">
          <div className="flex items-center gap-2.5">
            {status === 'checking' && (
              <Loader2 size={14} className="text-sidebar-text animate-spin" aria-label="Checking backend status" />
            )}
            {status === 'online' && (
              <Wifi size={14} className="text-positive" aria-label="Backend online" />
            )}
            {status === 'offline' && (
              <WifiOff size={14} className="text-danger" aria-label="Backend offline" />
            )}
            <div>
              <p className="text-xs text-white font-medium">
                {status === 'checking' ? 'Connecting...' : status === 'online' ? 'Engine Online' : 'Engine Offline'}
              </p>
              <p className="text-2xs text-sidebar-text">
                {status === 'online' ? 'FastAPI v0.5.0' : 'Check backend server'}
              </p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
