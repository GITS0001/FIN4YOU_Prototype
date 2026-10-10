import React, { useEffect, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

const DESKTOP_QUERY = '(min-width: 1024px)';

export const AppShell: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(() => window.matchMedia(DESKTOP_QUERY).matches);
  const location = useLocation();

  // Keep sidebar state in sync with viewport size
  useEffect(() => {
    const mq = window.matchMedia(DESKTOP_QUERY);
    const onChange = (e: MediaQueryListEvent) => setSidebarOpen(e.matches);
    mq.addEventListener('change', onChange);
    return () => mq.removeEventListener('change', onChange);
  }, []);

  // Scroll content to top on route change
  useEffect(() => {
    document.getElementById('main-content')?.scrollTo({ top: 0 });
  }, [location.pathname]);

  const isCopilot = location.pathname === '/copilot';

  return (
    <div className="flex h-screen overflow-hidden app-ambient">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div
        className={`flex flex-col flex-1 min-w-0 overflow-hidden transition-[margin] duration-300 ${
          sidebarOpen ? 'lg:ml-[var(--sidebar-width)]' : 'ml-0'
        }`}
      >
        <Topbar onMenuClick={() => setSidebarOpen((o) => !o)} isOpen={sidebarOpen} />

        <main
          className="flex-1 overflow-y-auto"
          style={{ paddingTop: 'var(--topbar-height)' }}
          id="main-content"
          role="main"
          tabIndex={-1}
        >
          <div
            key={location.pathname}
            className={`w-full mx-auto px-4 sm:px-6 lg:px-8 animate-fade-in ${
              isCopilot ? 'max-w-6xl py-4 sm:py-6' : 'max-w-7xl pt-6 sm:pt-8 pb-16'
            }`}
          >
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
