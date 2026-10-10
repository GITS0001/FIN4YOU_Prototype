import { Link } from 'react-router-dom';
import { LogOut } from 'lucide-react';

export default function DashboardHeader({ email, username, onLogout, activeTab, onSelectTab, unreadAlertsCount = 0 }) {
  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'expenses', label: 'Cash Flow & Ledger' },
    { id: 'forecast', label: '90-Day Forecast' },
    { id: 'insights', label: 'Insights & Leaks', badge: unreadAlertsCount },
    { id: 'what-if', label: 'What-If Simulator' },
    { id: 'copilot', label: 'Artha AI Copilot' },
    { id: 'profile', label: 'Profile & Settings' },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-gray-200/90 shadow-xs">
      {/* Top Bar */}
      <div className="max-w-[1360px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Left: Brand */}
        <div className="flex items-center gap-6">
          <Link to="/" className="flex items-center gap-2.5 font-bold text-lg tracking-tight text-[#0B0F19]">
            <span className="w-8 h-8 bg-[#2563EB] text-white rounded-xl grid place-items-center font-black text-sm shadow-blue">
              F
            </span>
            <span className="font-display">
              Fin4<strong className="text-[#2563EB]">You</strong>
            </span>
          </Link>

          {/* Engine Status Tag */}
          <div className="hidden md:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200/60 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>Deterministic Engine Active</span>
          </div>
        </div>

        {/* Right: User and Sign Out */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 text-right">
            <div>
              <div className="text-xs font-bold text-gray-900 leading-tight">{username || 'User'}</div>
              <div id="user-email" className="text-[10px] text-gray-400 font-mono truncate max-w-[180px]">
                {email}
              </div>
            </div>
            <div className="w-8 h-8 rounded-full bg-blue-100 text-[#2563EB] font-bold text-xs grid place-items-center border border-blue-200">
              {(username || 'U').charAt(0).toUpperCase()}
            </div>
          </div>

          <button
            id="logout-btn"
            onClick={onLogout}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-gray-200 hover:border-red-200 text-gray-600 hover:text-red-600 hover:bg-red-50 text-xs font-semibold transition-all touch-target"
            title="Sign out of your session"
          >
            <LogOut size={15} />
            <span className="hidden sm:inline">Sign out</span>
          </button>
        </div>
      </div>

      {/* Desktop Horizontal Navigation Rail */}
      <div className="hidden md:block border-t border-gray-100 bg-[#F8FAFC]">
        <div className="max-w-[1360px] mx-auto px-4 sm:px-6 lg:px-8 flex items-center gap-1 overflow-x-auto no-scrollbar">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onSelectTab(tab.id)}
                className={`px-4 py-2.5 text-xs font-bold transition-all border-b-2 whitespace-nowrap flex items-center gap-1.5 ${
                  isActive
                    ? 'border-[#2563EB] text-[#2563EB] bg-white shadow-xs'
                    : 'border-transparent text-gray-500 hover:text-gray-900 hover:bg-gray-100/60'
                }`}
              >
                <span>{tab.label}</span>
                {Boolean(tab.badge) && (
                  <span className="px-1.5 py-0.2 rounded-full text-[10px] font-black bg-amber-500 text-white">
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
