import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export const AppShell: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main area */}
      <div
        className="flex flex-col flex-1 min-w-0 overflow-hidden"
        style={{ marginLeft: 'var(--sidebar-width)' }}
      >
        <Topbar onMenuClick={() => setSidebarOpen(true)} />

        {/* Page content */}
        <main
          className="flex-1 overflow-y-auto"
          style={{ paddingTop: 'var(--topbar-height)' }}
          id="main-content"
          role="main"
        >
          <div className="p-5 md:p-6 lg:p-8 max-w-screen-xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
