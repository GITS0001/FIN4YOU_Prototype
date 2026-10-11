import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';

// Import the migrated authenticated components and contexts
import { AppShell } from './components/layout/AppShell';
import { Dashboard } from './pages/Dashboard';
import { Copilot } from './pages/Copilot';
import { Insights } from './pages/Insights';
import { Forecast } from './pages/Forecast';
import { WhatIf } from './pages/WhatIf';
import { Profile } from './pages/Profile';
import { Affordability } from './pages/Affordability';
import { FinancialStatement } from './pages/FinancialStatement';
import { useAuth } from './context/AuthContext';

// Pages that use the landing layout (Header + Footer)
function LandingLayout({ children }) {
  return (
    <>
      <Header />
      <main>{children}</main>
      <Footer />
    </>
  );
}

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm font-medium text-slate-500">Checking session...</p>
        </div>
      </div>
    );
  }
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingLayout><Home /></LandingLayout>} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        
        {/* Authenticated Dashboard Routes */}
        <Route element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/copilot" element={<Copilot />} />
          <Route path="/insights" element={<Insights />} />
          <Route path="/forecast" element={<Forecast />} />
          <Route path="/what-if" element={<WhatIf />} />
          <Route path="/affordability" element={<Affordability />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/statement" element={<FinancialStatement />} />
          {/* 404 fallback within AppShell routes */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
