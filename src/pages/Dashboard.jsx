import { useEffect, useState, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import MobileBottomNav from '../components/dashboard/MobileBottomNav';
import OverviewTab from '../components/dashboard/OverviewTab';
import ExpensesTab from '../components/dashboard/ExpensesTab';
import ForecastTab from '../components/dashboard/ForecastTab';
import InsightsTab from '../components/dashboard/InsightsTab';
import WhatIfTab from '../components/dashboard/WhatIfTab';
import CopilotTab from '../components/dashboard/CopilotTab';
import ProfileTab from '../components/dashboard/ProfileTab';
import { getUserProfile, getFinancialState, getAlerts } from '../api/fin4youApi';

export default function Dashboard() {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'overview');
  const navigate = useNavigate();

  // Financial profile & state calibrated with FIN4YOU backend
  const [profile, setProfile] = useState({
    userId: 'user_01',
    currency: 'INR',
    currencySymbol: '₹',
    balance: 58480,
    buffer: 18000,
    income: 75000,
    expenses: 42200,
    full_name: '',
    email: '',
  });
  const [financialState, setFinancialState] = useState(null);
  const [alerts, setAlerts] = useState([]);

  // Load live data from backend
  const fetchBackendData = useCallback(async () => {
    try {
      setApiError(null);
      const [profileData, stateData, alertsData] = await Promise.allSettled([
        getUserProfile(),
        getFinancialState(),
        getAlerts(),
      ]);

      if (profileData.status === 'fulfilled' && profileData.value) {
        const p = profileData.value;
        const symbol = p.home_currency === 'USD' ? '$' : p.home_currency === 'EUR' ? '€' : p.home_currency === 'ZAR' ? 'R' : '₹';
        setProfile((prev) => ({
          ...prev,
          userId: p.user_id || prev.userId,
          currency: p.home_currency || 'INR',
          currencySymbol: symbol,
          balance: p.current_available_balance ?? prev.balance,
          buffer: p.minimum_balance_to_keep ?? prev.buffer,
          full_name: p.full_name || '',
          email: p.email || '',
        }));
      }

      if (stateData.status === 'fulfilled' && stateData.value) {
        setFinancialState(stateData.value);
        if (stateData.value.total_observed_income) {
          setProfile((prev) => ({
            ...prev,
            income: stateData.value.total_observed_income || prev.income,
            expenses: stateData.value.total_observed_expenses || prev.expenses,
            balance: stateData.value.available_balance ?? prev.balance,
            buffer: stateData.value.minimum_reserve ?? prev.buffer,
          }));
        }
      }

      if (alertsData.status === 'fulfilled' && Array.isArray(alertsData.value)) {
        setAlerts(alertsData.value);
      }
    } catch (err) {
      console.warn('Backend live sync warning:', err);
      setApiError(err.message || 'Connecting in fallback mode');
    }
  }, []);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (!session) {
        navigate('/login', { replace: true });
      } else {
        setSession(session);
        setLoading(false);
        fetchBackendData();
      }
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_, s) => {
      if (!s) {
        navigate('/login', { replace: true });
      } else {
        setSession(s);
        setLoading(false);
        fetchBackendData();
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate, fetchBackendData]);

  const handleSelectTab = (tabId) => {
    setActiveTab(tabId);
    setSearchParams(tabId === 'overview' ? {} : { tab: tabId });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const logout = async () => {
    await supabase.auth.signOut();
    navigate('/login', { replace: true });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-3 border-gray-200 border-t-[#2563EB] rounded-full animate-spin" />
          <span className="text-xs font-semibold text-gray-500">Loading your verified financial overview…</span>
        </div>
      </div>
    );
  }

  const email = profile.email || session?.user?.email || 'user@fin4you.com';
  const username =
    profile.full_name ||
    session?.user?.user_metadata?.full_name ||
    session?.user?.user_metadata?.username ||
    email.split('@')[0];

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col">
      {/* Top Header with live status, branding, and desktop navigation rail */}
      <DashboardHeader
        email={email}
        username={username}
        onLogout={logout}
        activeTab={activeTab}
        onSelectTab={handleSelectTab}
        unreadAlertsCount={alerts.filter(a => !a.is_read).length}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-[1360px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {apiError && (
          <div className="mb-4 p-3 bg-amber-50 border border-amber-200 text-amber-800 text-xs rounded-xl flex items-center justify-between">
            <span>Note: {apiError}. Demonstrating cached / offline interface state.</span>
            <button onClick={fetchBackendData} className="font-bold underline ml-2">Retry API</button>
          </div>
        )}

        {activeTab === 'overview' && (
          <OverviewTab
            profile={profile}
            financialState={financialState}
            onSelectTab={handleSelectTab}
            onRefresh={fetchBackendData}
          />
        )}

        {activeTab === 'expenses' && (
          <ExpensesTab
            profile={profile}
            onRefreshState={fetchBackendData}
          />
        )}

        {activeTab === 'forecast' && (
          <ForecastTab
            profile={profile}
            financialState={financialState}
          />
        )}

        {activeTab === 'insights' && (
          <InsightsTab
            profile={profile}
            alerts={alerts}
            onSelectTab={handleSelectTab}
          />
        )}

        {activeTab === 'what-if' && (
          <WhatIfTab profile={profile} />
        )}

        {activeTab === 'copilot' && (
          <CopilotTab profile={profile} />
        )}

        {activeTab === 'profile' && (
          <ProfileTab
            profile={profile}
            onUpdateProfile={(updated) => {
              setProfile((prev) => ({ ...prev, ...updated }));
              fetchBackendData();
            }}
            email={email}
            username={username}
          />
        )}
      </main>

      {/* Mobile App-Like Bottom Navigation */}
      <MobileBottomNav activeTab={activeTab} onSelectTab={handleSelectTab} />
    </div>
  );
}

