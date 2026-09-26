import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { Dashboard } from './pages/Dashboard';
import { Copilot } from './pages/Copilot';
import { Insights } from './pages/Insights';
import { Forecast } from './pages/Forecast';
import { WhatIf } from './pages/WhatIf';
import { Profile } from './pages/Profile';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppShell />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="copilot" element={<Copilot />} />
          <Route path="insights" element={<Insights />} />
          <Route path="forecast" element={<Forecast />} />
          <Route path="what-if" element={<WhatIf />} />
          <Route path="profile" element={<Profile />} />
          {/* 404 fallback */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
