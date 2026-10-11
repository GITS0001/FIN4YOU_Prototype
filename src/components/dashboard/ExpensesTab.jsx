import { useState, useEffect, useMemo } from 'react';
import { Search, Upload, Plus, Trash2, CheckCircle2, AlertCircle, FileText, X } from 'lucide-react';
import { getTransactions, createTransaction, deleteTransaction } from '../../api/fin4youApi';
import StatementUploadModal from './StatementUploadModal';

const defaultTransactions = [
  { id: 'tx-1', date: '2026-05-02', desc: 'Apartment rent transfer', cat: 'Rent & Housing', dir: 'debit', amt: 18500, flex: 'Fixed' },
  { id: 'tx-2', date: '2026-05-04', desc: 'Nature Fresh Supermarket', cat: 'Food & Groceries', dir: 'debit', amt: 3420, flex: 'Essential' },
  { id: 'tx-3', date: '2026-05-05', desc: 'Metro Transit Monthly Pass', cat: 'Transport', dir: 'debit', amt: 1200, flex: 'Essential' },
  { id: 'tx-4', date: '2026-05-06', desc: 'Primary Consulting Inflow', cat: 'Income', dir: 'credit', amt: 75000, flex: 'Verified' },
  { id: 'tx-5', date: '2026-05-07', desc: 'Electricity & Gas bill', cat: 'Utilities', dir: 'debit', amt: 2150, flex: 'Essential' },
  { id: 'tx-6', date: '2026-05-08', desc: 'Cloud storage and suite', cat: 'Subscriptions', dir: 'debit', amt: 699, flex: 'Stoppable' },
  { id: 'tx-7', date: '2026-05-09', desc: 'Weekend Bistro Dining', cat: 'Dining & Social', dir: 'debit', amt: 2840, flex: 'Discretionary' },
  { id: 'tx-8', date: '2026-05-10', desc: 'Education loan instalment', cat: 'Debt & EMI', dir: 'debit', amt: 3487, flex: 'Fixed' },
  { id: 'tx-9', date: '2026-05-11', desc: 'Pharmacy and Wellness', cat: 'Healthcare', dir: 'debit', amt: 850, flex: 'Essential' },
  { id: 'tx-10', date: '2026-05-12', desc: 'Video Streaming Annual Plan', cat: 'Subscriptions', dir: 'debit', amt: 1499, flex: 'Stoppable' },
  { id: 'tx-11', date: '2026-05-13', desc: 'Corner Coffee and Bakery', cat: 'Dining & Social', dir: 'debit', amt: 460, flex: 'Discretionary' },
  { id: 'tx-12', date: '2026-05-14', desc: 'Local Green Grocer', cat: 'Food & Groceries', dir: 'debit', amt: 1120, flex: 'Essential' },
];

export default function ExpensesTab({ profile, onRefreshState }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCat, setSelectedCat] = useState('All');
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modals state
  const [showAddModal, setShowAddModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);

  // New Transaction Form state
  const [newTx, setNewTx] = useState(() => ({
    description: '',
    amount: '',
    category: 'Food & Groceries',
    direction: 'debit',
    flexibility: 'Essential',
    event_date: new Date().toISOString().slice(0, 10),
  }));

  // Statement Upload state
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);

  const currencySymbol = profile?.currencySymbol || (typeof window !== 'undefined' && localStorage.getItem('fin4you_currency_symbol')) || '₹';

  // Load transactions from backend
  const loadTransactions = async () => {
    try {
      setLoading(true);
      const data = await getTransactions(200);
      if (Array.isArray(data) && data.length > 0) {
        const mapped = data.map((t) => {
          const isDebit = t.direction === 'OUTFLOW' || t.direction === 'debit' || t.event_type === 'expense';
          const catRaw = t.category || '';
          let finalCat = catRaw;
          if (!catRaw || catRaw === 'unknown' || catRaw === 'Uncategorized' || catRaw === 'Unknown') {
            const u = (t.description || '').toUpperCase();
            if (u.includes('SALARY')) finalCat = 'Salary & Payroll';
            else if (u.includes('RENT')) finalCat = 'Rent & Housing';
            else if (u.includes('FOOD') || u.includes('SUPERMARKET') || u.includes('GROCER') || u.includes('BISTRO') || u.includes('BAKERY')) finalCat = 'Food & Groceries';
            else if (u.includes('ELECTRIC') || u.includes('GAS') || u.includes('BILLPAY') || u.includes('INTERNET') || u.includes('POWER') || u.includes('BROADBAND') || u.includes('MOBILE')) finalCat = 'Utilities & Bills';
            else if (u.includes('SUBSCRIPTION') || u.includes('STREAMING') || u.includes('GOOGLE WORKSPACE') || u.includes('GOOGLE ADS')) finalCat = 'Subscriptions & Ads';
            else if (u.includes('PURCHASE') || u.includes('STATIONERY') || u.includes('HARDWARE') || u.includes('SUPPLIES') || u.includes('ENTERPRISES')) finalCat = 'Purchases & Supplies';
            else if (u.includes('ATM') || u.includes('WITHDRAWAL') || u.includes('CASH')) finalCat = 'Cash & ATM';
            else if (u.includes('GST') || u.includes('TAX') || u.includes('TDS') || u.includes('ITNS')) finalCat = 'Taxes & Statutory';
            else if (u.includes('LOGISTICS') || u.includes('FREIGHT')) finalCat = 'Logistics & Ops';
            else if (u.includes('SIP') || u.includes('MUTUAL') || u.includes('NIPPON')) finalCat = 'Investments & SIP';
            else finalCat = 'General Expense';
          }

          return {
            id: t.transaction_id || t.id,
            date: t.event_date ? String(t.event_date).slice(0, 10) : new Date().toISOString().slice(0, 10),
            desc: t.description || 'Transaction',
            cat: finalCat,
            dir: isDebit ? 'debit' : 'credit',
            amt: Math.abs(t.amount || 0),
            flex: t.flexibility || (isDebit ? 'Essential' : 'Verified'),
          };
        });
        setTransactions(mapped);
      } else {
        setTransactions(defaultTransactions);
      }
    } catch {
      setTransactions(defaultTransactions);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTransactions();
  }, []);

  // Compute category statistics from actual transactions
  const categories = useMemo(() => {
    const debits = transactions.filter((t) => t.dir === 'debit');
    const totalDebit = debits.reduce((acc, t) => acc + t.amt, 0) || 1;

    const map = {};
    const colorPalette = [
      'bg-[#2563EB]', 'bg-blue-400', 'bg-emerald-500',
      'bg-amber-500', 'bg-purple-500', 'bg-rose-400', 'bg-indigo-500'
    ];

    debits.forEach((t) => {
      const cat = t.cat || 'General';
      map[cat] = (map[cat] || 0) + t.amt;
    });

    return Object.entries(map).map(([name, amount], idx) => ({
      name,
      amount,
      percent: Number(((amount / totalDebit) * 100).toFixed(1)),
      color: colorPalette[idx % colorPalette.length],
    })).sort((a, b) => b.amount - a.amount);
  }, [transactions]);

  const totalMonthlyDebits = useMemo(() => {
    return transactions.filter(t => t.dir === 'debit').reduce((acc, t) => acc + t.amt, 0);
  }, [transactions]);

  const filteredTx = useMemo(() => {
    return transactions.filter((t) => {
      const matchSearch = t.desc.toLowerCase().includes(searchTerm.toLowerCase()) || t.cat.toLowerCase().includes(searchTerm.toLowerCase());
      const matchCat = selectedCat === 'All' || t.cat === selectedCat;
      return matchSearch && matchCat;
    });
  }, [transactions, searchTerm, selectedCat]);

  // Handle Add Transaction Submit
  const handleAddSubmit = async (e) => {
    e.preventDefault();
    if (!newTx.description || !newTx.amount) return;

    try {
      await createTransaction({
        description: newTx.description,
        amount: parseFloat(newTx.amount),
        category: newTx.category,
        direction: newTx.direction,
        event_type: newTx.direction === 'credit' ? 'income' : 'expense',
        flexibility: newTx.flexibility,
        event_date: newTx.event_date,
      });

      setStatusMsg({ type: 'success', text: 'Transaction created successfully!' });
      setShowAddModal(false);
      setNewTx({
        description: '',
        amount: '',
        category: 'Food & Groceries',
        direction: 'debit',
        flexibility: 'Essential',
        event_date: new Date().toISOString().slice(0, 10),
      });
      loadTransactions();
      if (onRefreshState) onRefreshState();
    } catch (err) {
      setStatusMsg({ type: 'error', text: err.message || 'Failed to create transaction' });
    }
  };

  // Handle Delete Transaction
  const handleDeleteTx = async (txId) => {
    if (!window.confirm('Delete this transaction permanently from ledger?')) return;
    try {
      await deleteTransaction(txId);
      setStatusMsg({ type: 'success', text: 'Transaction removed' });
      setTransactions((prev) => prev.filter((t) => t.id !== txId));
      if (onRefreshState) onRefreshState();
    } catch (err) {
      setStatusMsg({ type: 'error', text: err.message || 'Failed to delete transaction' });
    }
  };

  // Handle CSV Upload Submit
  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;

    try {
      setUploading(true);
      setUploadResult(null);
      const res = await uploadStatementCsv(uploadFile);
      setUploadResult({
        success: true,
        message: res.message,
        parsedCount: res.total_parsed,
        quality: res.data_quality_metrics,
      });
      loadTransactions();
      if (onRefreshState) onRefreshState();
    } catch (err) {
      setUploadResult({
        success: false,
        message: err.message || 'Failed to upload statement. Make sure it is a valid CSV.',
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6 sm:space-y-8 animate-fade-in pb-16 md:pb-6">
      {/* Toast Notification */}
      {statusMsg && (
        <div
          className={`p-4 rounded-xl border text-xs sm:text-sm font-semibold flex items-center justify-between shadow-xs ${
            statusMsg.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-rose-50 border-rose-200 text-rose-800'
          }`}
        >
          <div className="flex items-center gap-2">
            {statusMsg.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
            <span>{statusMsg.text}</span>
          </div>
          <button onClick={() => setStatusMsg(null)} className="font-bold underline text-xs">Dismiss</button>
        </div>
      )}

      {/* Header Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-gray-100 shadow-card">
        <div>
          <h2 className="text-xl font-black text-[#0B0F19] font-display">Cash Flow & Ledger Management</h2>
          <p className="text-xs text-gray-500">Categorized debit logs, recurring obligations, and bank statement parser</p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setShowUploadModal(true)}
            className="px-4 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-800 text-xs font-bold rounded-xl border border-gray-200/80 transition-all flex items-center gap-1.5 touch-target"
          >
            <Upload size={14} className="text-[#2563EB]" />
            <span>Upload Statement (PDF / CSV)</span>
          </button>

          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2.5 bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold rounded-xl shadow-blue transition-all flex items-center gap-1.5 touch-target"
          >
            <Plus size={15} />
            <span>Add Entry</span>
          </button>
        </div>
      </div>

      {/* Allocation Summary Card */}
      <div className="bg-white rounded-2xl p-5 sm:p-6 border border-gray-100 shadow-card">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
          <div>
            <h3 className="text-base font-bold text-[#0B0F19] font-display">Expense Allocation by Category</h3>
            <p className="text-xs text-gray-500">Categorized debits based on deterministic classification</p>
          </div>
          <div className="text-right">
            <span className="text-xs text-gray-400">Total Monthly Debits:</span>
            <span className="text-lg font-black text-[#0B0F19] block">{currencySymbol}{totalMonthlyDebits.toLocaleString()}</span>
          </div>
        </div>

        {/* Stacked Percentage Bar */}
        <div className="h-3.5 w-full bg-gray-100 rounded-full flex overflow-hidden mb-6">
          {categories.map((c) => (
            <div
              key={c.name}
              className={`${c.color} h-full transition-all`}
              style={{ width: `${c.percent}%` }}
              title={`${c.name}: ${c.percent}%`}
            />
          ))}
        </div>

        {/* Category Cards Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {categories.map((c) => (
            <button
              key={c.name}
              onClick={() => setSelectedCat(selectedCat === c.name ? 'All' : c.name)}
              className={`p-3 rounded-xl border text-left transition-all ${
                selectedCat === c.name
                  ? 'border-[#2563EB] bg-blue-50/50 shadow-xs'
                  : 'border-gray-100 bg-gray-50/60 hover:bg-gray-100/60'
              }`}
            >
              <div className="flex items-center gap-1.5 mb-1">
                <span className={`w-2 h-2 rounded-full ${c.color}`} />
                <span className="text-[11px] font-bold text-gray-700 truncate">{c.name}</span>
              </div>
              <div className="text-sm font-black text-[#0B0F19]">
                {currencySymbol}
                {c.amount.toLocaleString()}
              </div>
              <span className="text-[10px] text-gray-400 block mt-0.5">{c.percent}%</span>
            </button>
          ))}
        </div>
      </div>

      {/* Filterable Transaction Ledger */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-card p-5 sm:p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5">
          <div>
            <h3 className="text-base font-bold text-[#0B0F19] font-display">Verified Transaction Ledger ({filteredTx.length})</h3>
            <p className="text-xs text-gray-500">Search and filter recorded entries</p>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5">
            <div className="relative">
              <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
              <input
                type="text"
                placeholder="Search merchant or category..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full sm:w-64 pl-9 pr-3 py-2 text-xs border border-gray-200 rounded-xl bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
              />
            </div>

            {selectedCat !== 'All' && (
              <button
                onClick={() => setSelectedCat('All')}
                className="px-3 py-2 text-xs font-semibold text-[#2563EB] bg-blue-50 rounded-xl border border-blue-200/60 hover:bg-blue-100 transition-colors"
              >
                Clear filter ({selectedCat}) ✕
              </button>
            )}
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto -mx-5 sm:mx-0">
          <div className="inline-block min-w-full align-middle px-5 sm:px-0">
            {loading ? (
              <div className="py-12 text-center text-xs text-gray-400 font-semibold">Loading ledger records…</div>
            ) : (
              <table className="min-w-full text-left text-xs text-gray-700">
                <thead className="bg-gray-50/80 text-[11px] uppercase tracking-wider text-gray-400 font-bold border-b border-gray-100">
                  <tr>
                    <th className="py-3 px-3">Date</th>
                    <th className="py-3 px-3">Description</th>
                    <th className="py-3 px-3">Category</th>
                    <th className="py-3 px-3">Flexibility</th>
                    <th className="py-3 px-3 text-right">Amount</th>
                    <th className="py-3 px-3 text-center">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filteredTx.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-gray-400 text-sm">
                        No transactions found matching your search.
                      </td>
                    </tr>
                  ) : (
                    filteredTx.map((tx) => (
                      <tr key={tx.id} className="hover:bg-blue-50/30 transition-colors">
                        <td className="py-3.5 px-3 text-gray-500 font-mono whitespace-nowrap">{tx.date}</td>
                        <td className="py-3.5 px-3 font-semibold text-gray-900">{tx.desc}</td>
                        <td className="py-3.5 px-3">
                          <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-gray-100 text-gray-700 border border-gray-200/60">
                            {tx.cat}
                          </span>
                        </td>
                        <td className="py-3.5 px-3">
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                              tx.flex === 'Fixed'
                                ? 'text-blue-700 bg-blue-50'
                                : tx.flex === 'Essential'
                                ? 'text-emerald-700 bg-emerald-50'
                                : tx.flex === 'Discretionary'
                                ? 'text-amber-700 bg-amber-50'
                                : 'text-rose-700 bg-rose-50'
                            }`}
                          >
                            {tx.flex}
                          </span>
                        </td>
                        <td className="py-3.5 px-3 text-right whitespace-nowrap font-bold">
                          <span className={tx.dir === 'credit' ? 'text-emerald-600' : 'text-gray-900'}>
                            {tx.dir === 'credit' ? '+' : '-'}
                            {currencySymbol}
                            {tx.amt.toLocaleString()}
                          </span>
                        </td>
                        <td className="py-3.5 px-3 text-center whitespace-nowrap">
                          <button
                            onClick={() => handleDeleteTx(tx.id)}
                            className="p-1 text-gray-400 hover:text-rose-600 rounded hover:bg-rose-50 transition-colors"
                            title="Delete entry"
                          >
                            <Trash2 size={14} />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>

      {/* Add Transaction Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-gray-100 pb-3">
              <h3 className="text-base font-bold text-gray-900 font-display">Add Verified Entry</h3>
              <button onClick={() => setShowAddModal(false)} className="text-gray-400 hover:text-gray-600">
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleAddSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">Description</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Grocery Store"
                  value={newTx.description}
                  onChange={(e) => setNewTx({ ...newTx, description: e.target.value })}
                  className="w-full px-3.5 py-2 text-xs border rounded-xl border-gray-200 focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-gray-700 mb-1">Amount ({currencySymbol})</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    placeholder="1250"
                    value={newTx.amount}
                    onChange={(e) => setNewTx({ ...newTx, amount: e.target.value })}
                    className="w-full px-3.5 py-2 text-xs border rounded-xl border-gray-200 focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-700 mb-1">Direction</label>
                  <select
                    value={newTx.direction}
                    onChange={(e) => setNewTx({ ...newTx, direction: e.target.value })}
                    className="w-full px-3 py-2 text-xs border rounded-xl border-gray-200 focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
                  >
                    <option value="debit">Debit (Expense)</option>
                    <option value="credit">Credit (Income)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-gray-700 mb-1">Category</label>
                  <input
                    type="text"
                    value={newTx.category}
                    onChange={(e) => setNewTx({ ...newTx, category: e.target.value })}
                    className="w-full px-3.5 py-2 text-xs border rounded-xl border-gray-200 focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-700 mb-1">Flexibility</label>
                  <select
                    value={newTx.flexibility}
                    onChange={(e) => setNewTx({ ...newTx, flexibility: e.target.value })}
                    className="w-full px-3 py-2 text-xs border rounded-xl border-gray-200 focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
                  >
                    <option value="Fixed">Fixed</option>
                    <option value="Essential">Essential</option>
                    <option value="Discretionary">Discretionary</option>
                    <option value="Stoppable">Stoppable</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1">Date</label>
                <input
                  type="date"
                  value={newTx.event_date}
                  onChange={(e) => setNewTx({ ...newTx, event_date: e.target.value })}
                  className="w-full px-3.5 py-2 text-xs border rounded-xl border-gray-200 focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
                />
              </div>

              <div className="pt-2 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-xs font-bold text-gray-600 bg-gray-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-bold text-white bg-[#2563EB] hover:bg-[#1D4ED8] rounded-xl shadow-xs"
                >
                  Save Entry
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Bank Statement Upload Modal (PDF or CSV) */}
      <StatementUploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onSuccess={() => {
          loadTransactions();
          if (onRefreshState) onRefreshState();
        }}
        currencySymbol={currencySymbol}
      />
    </div>
  );
}
