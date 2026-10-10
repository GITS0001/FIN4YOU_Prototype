import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Eye, EyeOff, Loader2, Lock, CheckCircle2, ShieldCheck } from 'lucide-react';
import { supabase } from '../lib/supabase';

export default function ResetPassword() {
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [show, setShow] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Supabase sends the recovery token in the URL hash
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event) => {
      if (event === 'PASSWORD_RECOVERY') {
        // Session is now active, form can be submitted
      }
    });
    return () => subscription.unsubscribe();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!password || password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }
    setLoading(true);
    setError('');
    const { error: err } = await supabase.auth.updateUser({ password });
    setLoading(false);
    if (err) {
      setError(err.message);
    } else {
      setDone(true);
      setTimeout(() => navigate('/dashboard'), 2000);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50/80 p-4 sm:p-6">
      <div className="w-full max-w-[420px]">
        <Link
          to="/"
          className="inline-flex items-center gap-2.5 font-bold text-base mb-8 text-[#0B0F19] hover:opacity-90"
        >
          <span className="w-8 h-8 bg-[#2563EB] text-white rounded-xl grid place-items-center text-sm font-black shadow-blue">
            F
          </span>
          <span className="font-display">
            Fin4<strong className="text-[#2563EB]">You</strong>
          </span>
        </Link>

        <div className="bg-white rounded-2xl shadow-card border border-gray-100 p-6 sm:p-8">
          {done ? (
            <div className="text-center py-4 animate-fade-in">
              <div className="w-16 h-16 bg-emerald-50 text-emerald-600 rounded-2xl grid place-items-center text-3xl mx-auto mb-4 border border-emerald-100">
                ✓
              </div>
              <h2 className="text-xl font-black mb-2 text-[#0B0F19] font-display">Password updated!</h2>
              <p className="text-sm text-gray-500">Redirecting to your dashboard…</p>
            </div>
          ) : (
            <>
              <div className="mb-6">
                <span className="inline-block text-xs font-bold text-[#2563EB] uppercase tracking-wider mb-1.5">
                  Update Password
                </span>
                <h1 className="text-2xl sm:text-3xl font-black text-[#0B0F19] tracking-tight mb-2 font-display">
                  Set new password
                </h1>
                <p className="text-sm text-gray-500 leading-relaxed">
                  Choose a strong, memorable password of at least 8 characters.
                </p>
              </div>

              <form onSubmit={handleSubmit} noValidate className="space-y-4">
                {error && (
                  <div role="alert" className="bg-red-50 border border-red-200 text-red-700 text-xs sm:text-sm px-4 py-3 rounded-xl font-medium">
                    {error}
                  </div>
                )}

                <div>
                  <label htmlFor="reset-password-field" className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5">
                    New Password
                  </label>
                  <div className="relative">
                    <Lock size={17} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                    <input
                      id="reset-password-field"
                      type={show ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Min 8 characters"
                      autoComplete="new-password"
                      className="w-full min-h-[46px] pl-10 pr-11 py-2.5 rounded-xl border border-gray-200 bg-gray-50/70 text-sm focus:border-[#2563EB] focus:bg-white focus:ring-2 focus:ring-[#2563EB]/15 outline-none transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => setShow((v) => !v)}
                      className="absolute right-2.5 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-700 touch-target"
                      aria-label={show ? 'Hide password' : 'Show password'}
                    >
                      {show ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <div>
                  <label htmlFor="reset-confirm" className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5">
                    Confirm Password
                  </label>
                  <div className="relative">
                    <Lock size={17} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                    <input
                      id="reset-confirm"
                      type={show ? 'text' : 'password'}
                      value={confirm}
                      onChange={(e) => setConfirm(e.target.value)}
                      placeholder="Repeat new password"
                      autoComplete="new-password"
                      className="w-full min-h-[46px] pl-10 pr-11 py-2.5 rounded-xl border border-gray-200 bg-gray-50/70 text-sm focus:border-[#2563EB] focus:bg-white focus:ring-2 focus:ring-[#2563EB]/15 outline-none transition-all"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full min-h-[46px] flex items-center justify-center gap-2 py-3.5 bg-[#2563EB] text-white font-bold rounded-xl hover:bg-[#1D4ED8] disabled:opacity-60 transition-all shadow-blue text-sm touch-target mt-2"
                >
                  {loading ? (
                    <>
                      <Loader2 size={16} className="animate-spin" /> Updating…
                    </>
                  ) : (
                    <>
                      <span>Update Password</span>
                      <CheckCircle2 size={16} />
                    </>
                  )}
                </button>
              </form>
            </>
          )}
        </div>

        <div className="mt-8 text-center text-xs text-gray-400 flex items-center justify-center gap-1.5">
          <ShieldCheck size={14} className="text-emerald-500" />
          <span>Protected session via Supabase</span>
        </div>
      </div>
    </div>
  );
}
