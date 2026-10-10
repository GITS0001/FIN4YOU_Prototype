import { useState, useEffect } from 'react';
import { Save, CheckCircle2, AlertCircle } from 'lucide-react';
import { updateUserProfile, getUserProfile } from '../../api/fin4youApi';

export default function ProfileTab({ profile, onUpdateProfile, email, username }) {
  const [fullName, setFullName] = useState(username || profile?.full_name || '');
  const [currency, setCurrency] = useState(profile?.currency || 'INR');
  const [buffer, setBuffer] = useState(profile?.buffer || 18000);
  const [age, setAge] = useState('30');
  const [maritalStatus, setMaritalStatus] = useState('Single');
  const [dependents, setDependents] = useState('0');
  const [occupation, setOccupation] = useState('Professional');
  const [cityTier, setCityTier] = useState('Tier 1');

  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const [priorities, setPriorities] = useState({
    emergencySavings: true,
    debtRepayment: true,
    retirement: false,
    education: true,
  });

  const [categoriesToProtect] = useState(['Apartment Rent', 'Household Utilities', 'Groceries & Provisions']);
  const [categoriesToReduce] = useState(['Dining Out', 'Entertainment', 'Impulse Shopping']);
  const [categoriesToStop] = useState(['Unused Cloud Storage', 'Delivery Membership', 'Streaming Add-ons']);

  useEffect(() => {
    getUserProfile()
      .then((p) => {
        if (p) {
          if (p.full_name) setFullName(p.full_name);
          if (p.home_currency) setCurrency(p.home_currency);
          if (p.minimum_balance_to_keep) setBuffer(p.minimum_balance_to_keep);
          if (p.age) setAge(p.age);
          if (p.marital_status) setMaritalStatus(p.marital_status);
          if (p.dependents) setDependents(p.dependents);
          if (p.occupation) setOccupation(p.occupation);
          if (p.city_tier) setCityTier(p.city_tier);
        }
      })
      .catch(() => {});
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setErrorMsg(null);
    setSaving(true);

    const currencySymbol = currency === 'USD' ? '$' : currency === 'EUR' ? '€' : currency === 'ZAR' ? 'R' : '₹';

    const payload = {
      full_name: fullName,
      home_currency: currency,
      minimum_balance_to_keep: Number(buffer),
      age: String(age),
      marital_status: maritalStatus,
      dependents: String(dependents),
      occupation,
      city_tier: cityTier,
      financial_priorities: Object.keys(priorities).filter((k) => priorities[k]),
      expense_categories_to_protect: categoriesToProtect,
      expense_categories_user_is_willing_to_reduce: categoriesToReduce,
      expense_categories_user_is_willing_to_stop: categoriesToStop,
    };

    try {
      await updateUserProfile(payload);
      onUpdateProfile({
        ...profile,
        full_name: fullName,
        currency,
        currencySymbol,
        buffer: Number(buffer),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to update backend profile.');
      onUpdateProfile({
        ...profile,
        full_name: fullName,
        currency,
        currencySymbol,
        buffer: Number(buffer),
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 sm:space-y-8 animate-fade-in pb-16 md:pb-6">
      {/* Header */}
      <div className="bg-white rounded-2xl p-5 sm:p-6 border border-gray-100 shadow-card">
        <h2 className="text-xl sm:text-2xl font-black text-[#0B0F19] tracking-tight font-display">
          Profile & Financial Constraints
        </h2>
        <p className="text-xs sm:text-sm text-gray-500 mt-1 max-w-xl">
          Configure your currency, minimum safety buffer thresholds, and priority constraints used by the deterministic decision engine.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Core Settings Form (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl p-5 sm:p-6 border border-gray-100 shadow-card space-y-6">
          <h3 className="text-base font-bold text-[#0B0F19] font-display">Financial Profile Parameters</h3>

          <form onSubmit={handleSave} className="space-y-5">
            {saved && (
              <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs sm:text-sm p-3.5 rounded-xl font-medium flex items-center gap-2">
                <CheckCircle2 size={16} className="text-emerald-600" />
                <span>Financial parameters updated on backend successfully!</span>
              </div>
            )}

            {errorMsg && (
              <div className="bg-amber-50 border border-amber-200 text-amber-800 text-xs p-3.5 rounded-xl font-medium flex items-center gap-2">
                <AlertCircle size={16} className="text-amber-600" />
                <span>Note: {errorMsg} (Updated locally)</span>
              </div>
            )}

            {/* User details */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5">
                  Full Name
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full min-h-[44px] px-3.5 py-2 rounded-xl border border-gray-200 bg-white text-xs sm:text-sm text-gray-900 font-medium focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5">
                  Email Address
                </label>
                <input
                  type="email"
                  disabled
                  value={email || 'user@example.com'}
                  className="w-full min-h-[44px] px-3.5 py-2 rounded-xl border border-gray-200 bg-gray-50 text-xs sm:text-sm text-gray-700 font-mono truncate"
                />
              </div>
            </div>

            {/* Demographic Parameters */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div>
                <label className="block text-[11px] font-bold text-gray-700 uppercase mb-1">Age</label>
                <input
                  type="number"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  className="w-full px-3 py-2 text-xs border border-gray-200 rounded-xl"
                />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-gray-700 uppercase mb-1">Marital Status</label>
                <select
                  value={maritalStatus}
                  onChange={(e) => setMaritalStatus(e.target.value)}
                  className="w-full px-2 py-2 text-xs border border-gray-200 rounded-xl"
                >
                  <option value="Single">Single</option>
                  <option value="Married">Married</option>
                </select>
              </div>
              <div>
                <label className="block text-[11px] font-bold text-gray-700 uppercase mb-1">Dependents</label>
                <input
                  type="number"
                  value={dependents}
                  onChange={(e) => setDependents(e.target.value)}
                  className="w-full px-3 py-2 text-xs border border-gray-200 rounded-xl"
                />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-gray-700 uppercase mb-1">City Tier</label>
                <select
                  value={cityTier}
                  onChange={(e) => setCityTier(e.target.value)}
                  className="w-full px-2 py-2 text-xs border border-gray-200 rounded-xl"
                >
                  <option value="Tier 1">Tier 1</option>
                  <option value="Tier 2">Tier 2</option>
                  <option value="Tier 3">Tier 3</option>
                </select>
              </div>
            </div>

            {/* Currency and Buffer */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label htmlFor="currency-select" className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5">
                  Home Operating Currency
                </label>
                <select
                  id="currency-select"
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  className="w-full min-h-[44px] px-3.5 py-2 rounded-xl border border-gray-200 bg-white text-xs sm:text-sm text-gray-900 font-medium focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
                >
                  <option value="INR">INR (₹ Indian Rupee)</option>
                  <option value="USD">USD ($ United States Dollar)</option>
                  <option value="EUR">EUR (€ Euro)</option>
                  <option value="ZAR">ZAR (R South African Rand)</option>
                </select>
              </div>

              <div>
                <label htmlFor="buffer-input" className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5">
                  Minimum Safety Buffer Threshold
                </label>
                <input
                  id="buffer-input"
                  type="number"
                  value={buffer}
                  onChange={(e) => setBuffer(e.target.value)}
                  className="w-full min-h-[44px] px-3.5 py-2 rounded-xl border border-gray-200 bg-white text-xs sm:text-sm text-gray-900 font-medium focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
                />
              </div>
            </div>

            {/* Priority Checkboxes */}
            <div className="pt-2">
              <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">
                Active Financial Priorities
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {[
                  { key: 'emergencySavings', label: 'Emergency Savings Fund' },
                  { key: 'debtRepayment', label: 'Rapid Debt & EMI Pacing' },
                  { key: 'education', label: 'Education & Professional Skill' },
                  { key: 'retirement', label: 'Retirement Growth SIP' },
                ].map(({ key, label }) => (
                  <label
                    key={key}
                    className="flex items-center gap-2.5 p-3 rounded-xl border border-gray-200 bg-gray-50/50 hover:bg-gray-50 cursor-pointer text-xs font-medium text-gray-800"
                  >
                    <input
                      type="checkbox"
                      checked={priorities[key]}
                      onChange={(e) => setPriorities((p) => ({ ...p, [key]: e.target.checked }))}
                      className="rounded accent-[#2563EB] w-4 h-4"
                    />
                    <span>{label}</span>
                  </label>
                ))}
              </div>
            </div>

            <button
              type="submit"
              disabled={saving}
              className="inline-flex items-center gap-2 px-6 py-3 bg-[#2563EB] text-white text-xs sm:text-sm font-bold rounded-xl shadow-blue hover:bg-[#1D4ED8] transition-all touch-target disabled:opacity-50"
            >
              <Save size={15} />
              <span>{saving ? 'Updating Backend...' : 'Save Financial Configuration'}</span>
            </button>
          </form>
        </div>

        {/* Priority Constraints Breakdown (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl p-5 sm:p-6 border border-gray-100 shadow-card space-y-6">
          <h3 className="text-base font-bold text-[#0B0F19] font-display">Categorization Rules</h3>

          {/* Protected */}
          <div>
            <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-700 uppercase tracking-wider mb-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span>Protected Categories (Fixed Essentials)</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {categoriesToProtect.map((c) => (
                <span key={c} className="px-2.5 py-1 rounded-lg text-xs bg-emerald-50 text-emerald-800 border border-emerald-200/60 font-medium">
                  {c}
                </span>
              ))}
            </div>
          </div>

          {/* Reducible */}
          <div>
            <div className="flex items-center gap-1.5 text-xs font-bold text-amber-700 uppercase tracking-wider mb-2">
              <span className="w-2 h-2 rounded-full bg-amber-500" />
              <span>Willing to Reduce (Lifestyle Discretionary)</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {categoriesToReduce.map((c) => (
                <span key={c} className="px-2.5 py-1 rounded-lg text-xs bg-amber-50 text-amber-800 border border-amber-200/60 font-medium">
                  {c}
                </span>
              ))}
            </div>
          </div>

          {/* Stoppable */}
          <div>
            <div className="flex items-center gap-1.5 text-xs font-bold text-rose-700 uppercase tracking-wider mb-2">
              <span className="w-2 h-2 rounded-full bg-rose-500" />
              <span>Willing to Stop (Emergency Buffers)</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {categoriesToStop.map((c) => (
                <span key={c} className="px-2.5 py-1 rounded-lg text-xs bg-rose-50 text-rose-800 border border-rose-200/60 font-medium">
                  {c}
                </span>
              ))}
            </div>
          </div>

          <div className="p-3.5 bg-blue-50/60 rounded-xl border border-blue-100 text-[11px] text-gray-600 leading-relaxed">
            These category rules feed directly into the affordability optimizer when you simulate major purchases.
          </div>
        </div>
      </div>
    </div>
  );
}
