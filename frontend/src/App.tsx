import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { Dashboard } from './pages/Dashboard';
import { Copilot } from './pages/Copilot';
import { Insights } from './pages/Insights';
import { Forecast } from './pages/Forecast';
import { WhatIf } from './pages/WhatIf';
import { Profile } from './pages/Profile';
import { Affordability } from './pages/Affordability';
import { FinancialStatement } from './pages/FinancialStatement';
import { Landing } from './pages/Landing';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { OtpVerify } from './pages/OtpVerify';
import { useAuth } from './context/AuthContext';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/verify-otp" element={<OtpVerify />} />
        <Route element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }>
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="copilot" element={<Copilot />} />
          <Route path="insights" element={<Insights />} />
          <Route path="forecast" element={<Forecast />} />
          <Route path="what-if" element={<WhatIf />} />
          <Route path="affordability" element={<Affordability />} />
          <Route path="profile" element={<Profile />} />
          <Route path="statement" element={<FinancialStatement />} />
          {/* 404 fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
