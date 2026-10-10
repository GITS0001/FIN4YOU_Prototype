import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import { LogOut, TrendingUp, PieChart, Wallet, BarChart3 } from 'lucide-react';

export default function Dashboard() {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (!session) { navigate('/login', { replace: true }); } else { setSession(session); setLoading(false); }
    });
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_, s) => {
      if (!s) navigate('/login', { replace: true });
      else setSession(s);
    });
    return () => subscription.unsubscribe();
  }, [navigate]);

  const logout = async () => {
    await supabase.auth.signOut();
    navigate('/login', { replace: true });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-10 h-10 border-2 border-gray-200 border-t-[#2563EB] rounded-full animate-spin" />
      </div>
    );
  }

  const email = session?.user?.email || '';
  const username = session?.user?.user_metadata?.username || session?.user?.user_metadata?.full_name || email.split('@')[0];

  const cards = [
    { icon: Wallet, label: 'Total Income', value: '₹45,000', note: 'Sample data', color: 'text-[#2563EB]' },
    { icon: BarChart3, label: 'Total Expenses', value: '₹28,400', note: 'Sample data', color: 'text-gray-700' },
    { icon: TrendingUp, label: 'Net Savings', value: '₹16,600', note: 'Sample data', color: 'text-green-600' },
    { icon: PieChart, label: 'Savings Rate', value: '36.9%', note: 'Sample data', color: 'text-[#2563EB]' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Nav */}
      <header className="bg-[#0B0F19] text-white px-6 md:px-10 h-16 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-2.5 font-bold text-base">
          <span className="w-8 h-8 bg-[#2563EB] rounded-lg grid place-items-center text-sm font-black">F</span>
          Fin4<strong className="text-[#93C5FD]">You</strong>
        </div>
        <div className="flex items-center gap-4">
          <span id="user-email" className="text-xs text-[#93C5FD] font-mono hidden sm:block">{email}</span>
          <button id="logout-btn" onClick={logout} className="flex items-center gap-1.5 px-3 py-1.5 border border-[#2563EB]/40 text-[#93C5FD] text-xs font-semibold rounded-lg hover:bg-[#2563EB]/10 transition-colors">
            <LogOut size={14} /> Sign out
          </button>
        </div>
      </header>

      <main className="max-w-[1140px] mx-auto px-6 py-10">
        {/* Greeting */}
        <div className="mb-8">
          <h1 className="text-3xl font-black tracking-tight text-[#0B0F19]">
            Hello, <em className="not-italic text-[#2563EB]">{username}</em> 👋
          </h1>
          <p className="text-gray-500 text-sm mt-1">Here's your financial overview. Data shown below is illustrative.</p>
        </div>

        {/* Summary cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {cards.map(({ icon: Icon, label, value, note, color }) => (
            <div key={label} className="bg-white rounded-2xl border border-gray-100 shadow-card p-5">
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">{label}</span>
                <Icon size={16} className="text-gray-300" />
              </div>
              <div className={`text-2xl font-black tracking-tight ${color}`}>{value}</div>
              <div className="text-[10px] text-gray-400 italic mt-1">{note}</div>
            </div>
          ))}
        </div>

        {/* Notice */}
        <div className="bg-[#EFF6FF] border border-[#BFDBFE] rounded-2xl p-6 flex gap-4 items-start">
          <div className="text-2xl flex-shrink-0">📊</div>
          <div>
            <h3 className="text-sm font-bold text-[#0B0F19] mb-1">This is a demo dashboard</h3>
            <p className="text-sm text-gray-500 leading-relaxed">
              The figures shown above are sample data for illustration only. Full financial data entry, transaction tracking, and real summaries will be available here once connected to your financial records.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
