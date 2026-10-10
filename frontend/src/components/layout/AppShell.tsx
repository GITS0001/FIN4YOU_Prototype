import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export const AppShell: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(window.innerWidth >= 1024);

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main area */}
      <div
        className={`flex flex-col flex-1 min-w-0 overflow-hidden transition-all duration-250 ${sidebarOpen ? 'lg:ml-[var(--sidebar-width)]' : 'ml-0'}`}
      >
        <Topbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} isOpen={sidebarOpen} />

        {/* Page content */}
        <main
          className="flex-1 overflow-y-auto bg-background"
          style={{ paddingTop: 'var(--topbar-height)' }}
          id="main-content"
          role="main"
        >
          <div className="p-4 sm:p-6 md:p-8 lg:p-8 max-w-[1600px] mx-auto w-full">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
