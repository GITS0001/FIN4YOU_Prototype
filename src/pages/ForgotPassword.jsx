import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, Loader2 } from 'lucide-react';
import { supabase } from '../lib/supabase';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) { setError('Please enter your email address.'); return; }
    if (!/\S+@\S+\.\S+/.test(email)) { setError('Enter a valid email address.'); return; }
    setLoading(true);
    setError('');
    const { error: err } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset-password`,
    });
    setLoading(false);
    if (err) { setError(err.message); } else { setSent(true); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
      <div className="w-full max-w-[420px]">
        <Link to="/" className="flex items-center gap-2 font-bold text-base mb-10 text-[#0B0F19]">
          <span className="w-8 h-8 bg-[#2563EB] text-white rounded-lg grid place-items-center text-sm font-black">F</span>
          Fin4<strong className="text-[#2563EB]">You</strong>
        </Link>

        {sent ? (
          <div className="bg-white rounded-2xl shadow-card border border-gray-100 p-8 text-center">
            <div className="w-16 h-16 bg-[#EFF6FF] rounded-full grid place-items-center text-3xl mx-auto mb-4">✉</div>
            <h2 className="text-xl font-black text-[#0B0F19] mb-2">Check your email</h2>
            <p className="text-sm text-gray-500 mb-1">A password reset link was sent to <strong>{email}</strong>.</p>
            <p className="text-sm text-gray-400 mb-6">It expires in 1 hour. Check your spam folder if you don't see it.</p>
            <Link to="/login" className="inline-flex items-center gap-2 px-6 py-3 bg-[#2563EB] text-white font-bold rounded-xl text-sm hover:bg-[#1D4ED8] transition-colors">
              Back to Login →
            </Link>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-card border border-gray-100 p-8">
            <h1 className="text-2xl font-black text-[#0B0F19] tracking-tight mb-2">Forgot password?</h1>
            <p className="text-sm text-gray-500 mb-6">Enter your email and we'll send a secure reset link.</p>
            <form onSubmit={handleSubmit} noValidate className="space-y-4">
              {error && <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-xl">{error}</div>}
              <div>
                <label htmlFor="reset-email" className="block text-xs font-bold text-gray-600 uppercase tracking-wider mb-1.5">Email Address</label>
                <div className="relative">
                  <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input
                    id="reset-email"
                    type="email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className="w-full pl-9 pr-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-sm focus:border-[#2563EB] focus:bg-white focus:ring-2 focus:ring-[#2563EB]/15 outline-none transition-all"
                  />
                </div>
              </div>
              <button type="submit" disabled={loading} className="w-full flex items-center justify-center gap-2 py-3.5 bg-[#2563EB] text-white font-bold rounded-xl hover:bg-[#1D4ED8] disabled:opacity-60 transition-colors shadow-blue text-sm">
                {loading ? <><Loader2 size={16} className="animate-spin" />Sending…</> : 'Send Reset Link →'}
              </button>
              <p className="text-center text-xs text-gray-500">
                Remembered? <Link to="/login" className="text-[#2563EB] font-semibold hover:underline">Sign in</Link>
              </p>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
