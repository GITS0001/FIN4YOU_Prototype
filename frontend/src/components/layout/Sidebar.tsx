import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Bot,
  BarChart2,
  TrendingUp,
  GitFork,
  UserCircle,
  Activity,
  Wifi,
  WifiOff,
  Loader2,
  ChevronRight,
  CreditCard,
  FileText,
  ChevronDown,
  Check,
} from 'lucide-react';
import { useBackendStatus } from '../../hooks/useBackendStatus';
import { useSelectedUser, DEMO_USERS, DEFAULT_USER_ID } from '../../context/UserContext';

interface NavItemDef {
  path: string;
  label: string;
  icon: React.ElementType;
}

const NAV_ITEMS_MAIN: NavItemDef[] = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/copilot', label: 'AI Copilot', icon: Bot },
  { path: '/insights', label: 'Insights', icon: BarChart2 },
  { path: '/forecast', label: 'Forecast', icon: TrendingUp },
  { path: '/what-if', label: 'What-If Simulator', icon: GitFork },
  { path: '/affordability', label: 'Affordability', icon: CreditCard },
];

const NAV_ITEMS_ACCOUNT: NavItemDef[] = [
  { path: '/profile', label: 'Demo Profile', icon: UserCircle },
  { path: '/statement', label: 'Financial Statement', icon: FileText },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = true, onClose }) => {
  const { status } = useBackendStatus();
  const location = useLocation();
  const { selectedUserId, setSelectedUserId } = useSelectedUser();
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);

  const selectedUser = DEMO_USERS.find(u => u.id === selectedUserId) || DEMO_USERS[0];

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
            <p className="text-2xs text-sidebar-text leading-none mt-0.5">Financial Intelligence</p>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 overflow-y-auto" role="navigation">
          <p className="label-sm text-white/30 px-3 mb-2 tracking-wider">MAIN</p>
          <ul className="space-y-0.5" role="list">
            {NAV_ITEMS_MAIN.map((item) => (
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

          <div className="h-px bg-white/5 my-4 mx-3"></div>

          <p className="label-sm text-white/30 px-3 mb-2 tracking-wider">ACCOUNT</p>
          <ul className="space-y-0.5" role="list">
            {NAV_ITEMS_ACCOUNT.map((item) => (
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
          </ul>

          <div className="h-px bg-white/5 my-4 mx-3"></div>

          {/* System Info */}
          <div className="px-3 space-y-2">
            <div className="bg-white/5 rounded-lg p-3">
              <p className="text-2xs text-white/40 uppercase tracking-wider mb-1">Data Coverage</p>
              <p className="text-xs text-white/70">10 demo users · 6–7 months history</p>
            </div>
            <div className="bg-white/5 rounded-lg p-3">
              <p className="text-2xs text-white/40 uppercase tracking-wider mb-1">Architecture</p>
              <p className="text-xs text-white/70">Deterministic engines + AI Copilot</p>
            </div>
          </div>
        </nav>

        {/* User Switcher */}
        <div className="px-4 py-3 border-t border-white/10 bg-primary-dark/50 relative">
          <p className="text-2xs text-white/40 uppercase tracking-wider mb-2">Demo Account</p>
          <button
            className="w-full flex items-center gap-3 hover:bg-white/5 rounded-lg p-1.5 -mx-1.5 transition-colors"
            onClick={() => setUserDropdownOpen(!userDropdownOpen)}
            aria-expanded={userDropdownOpen}
            aria-haspopup="listbox"
            aria-label="Switch demo user"
          >
            <div className="w-8 h-8 rounded-full bg-primary-accent/20 border border-primary-accent/40 flex items-center justify-center flex-shrink-0">
              <UserCircle size={18} className="text-primary-accent" />
            </div>
            <div className="flex-1 text-left">
              <p className="text-xs text-white font-semibold">{selectedUser.label}</p>
              <p className="text-2xs text-white/50">
                {selectedUserId === DEFAULT_USER_ID ? 'Primary Demo' : 'Demo Account'}
              </p>
            </div>
            <ChevronDown
              size={14}
              className={`text-white/40 transition-transform ${userDropdownOpen ? 'rotate-180' : ''}`}
              aria-hidden="true"
            />
          </button>

          {/* User dropdown */}
          {userDropdownOpen && (
            <div
              className="absolute bottom-full left-3 right-3 mb-1 bg-[#1e2a4a] border border-white/10 rounded-xl overflow-hidden shadow-xl z-50"
              role="listbox"
              aria-label="Select demo user"
            >
              {DEMO_USERS.map((user) => (
                <button
                  key={user.id}
                  role="option"
                  aria-selected={user.id === selectedUserId}
                  className={`w-full text-left px-4 py-2.5 text-sm flex items-center justify-between transition-colors ${
                    user.id === selectedUserId
                      ? 'bg-primary-accent/20 text-white'
                      : 'text-white/70 hover:bg-white/5'
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
          )}
        </div>

        {/* Backend Status */}
        <div className="px-4 py-3 border-t border-white/10">
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
                {status === 'online' ? 'API Connected' : 'Check backend server'}
              </p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
