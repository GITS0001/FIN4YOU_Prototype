import { LayoutDashboard, Receipt, TrendingUp, Sparkles, SlidersHorizontal, User } from 'lucide-react';

export default function MobileBottomNav({ activeTab, onSelectTab }) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'expenses', label: 'Expenses', icon: Receipt },
    { id: 'forecast', label: 'Forecast', icon: TrendingUp },
    { id: 'what-if', label: 'What-If', icon: SlidersHorizontal },
    { id: 'copilot', label: 'Artha AI', icon: Sparkles },
    { id: 'profile', label: 'Profile', icon: User },
  ];

  return (
    <nav
      className="md:hidden fixed bottom-0 inset-x-0 z-50 bg-white/95 backdrop-blur-md border-t border-gray-200/90 shadow-lg px-2 py-1.5 flex items-center justify-around safe-bottom"
      aria-label="Mobile Bottom Navigation"
    >
      {navItems.map(({ id, label, icon: Icon }) => {
        const isActive = activeTab === id;
        return (
          <button
            key={id}
            onClick={() => onSelectTab(id)}
            className={`flex flex-col items-center justify-center py-1 px-2 rounded-xl transition-all touch-target flex-1 ${
              isActive ? 'text-[#2563EB] font-bold' : 'text-gray-400 hover:text-gray-700 font-medium'
            }`}
          >
            <div className={`p-1 rounded-lg ${isActive ? 'bg-blue-50 text-[#2563EB]' : ''}`}>
              <Icon size={18} strokeWidth={isActive ? 2.4 : 1.8} />
            </div>
            <span className="text-[10px] tracking-tight mt-0.5 leading-tight">{label}</span>
          </button>
        );
      })}
    </nav>
  );
}
