import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, Loader2, ArrowLeft, ArrowRight, ShieldCheck } from 'lucide-react';
import { supabase } from '../lib/supabase';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) {
      setError('Please enter your email address.');
      return;
    }
    if (!/\S+@\S+\.\S+/.test(email.trim())) {
      setError('Enter a valid email address.');
      return;
    }
    setLoading(true);
    setError('');
    const { error: err } = await supabase.auth.resetPasswordForEmail(email.trim(), {
      redirectTo: `${window.location.origin}/reset-password`,
    });
    setLoading(false);
    if (err) {
      setError(err.message);
    } else {
      setSent(true);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50/80 p-4 sm:p-6">
      <div className="w-full max-w-[420px]">
        {/* Brand Link */}
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

        {sent ? (
          <div className="bg-white rounded-2xl shadow-card border border-gray-100 p-6 sm:p-8 text-center animate-fade-in">
            <div className="w-16 h-16 bg-blue-50 text-[#2563EB] rounded-2xl grid place-items-center text-3xl mx-auto mb-4 border border-blue-100">
              ✉
            </div>
            <h2 className="text-xl font-black text-[#0B0F19] mb-2 font-display">Check your inbox</h2>
            <p className="text-sm text-gray-600 mb-2 leading-relaxed">
              We sent a secure password reset link to <strong className="text-gray-900">{email}</strong>.
            </p>
            <p className="text-xs text-gray-400 mb-6">
              The link expires in 60 minutes. Check your spam folder if it doesn't appear shortly.
            </p>
            <Link
              to="/login"
              className="inline-flex items-center justify-center gap-2 w-full py-3.5 bg-[#2563EB] text-white font-bold rounded-xl text-sm shadow-blue hover:bg-[#1D4ED8] transition-colors touch-target"
            >
              <span>Back to Login</span>
              <ArrowRight size={16} />
            </Link>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-card border border-gray-100 p-6 sm:p-8">
            <div className="mb-6">
              <span className="inline-block text-xs font-bold text-[#2563EB] uppercase tracking-wider mb-1.5">
                Account Recovery
              </span>
              <h1 className="text-2xl sm:text-3xl font-black text-[#0B0F19] tracking-tight mb-2 font-display">
                Forgot password?
              </h1>
              <p className="text-sm text-gray-500 leading-relaxed">
                Enter your registered email address and we'll send a secure reset link.
              </p>
            </div>

            <form onSubmit={handleSubmit} noValidate className="space-y-4">
              {error && (
                <div role="alert" className="bg-red-50 border border-red-200 text-red-700 text-xs sm:text-sm px-4 py-3 rounded-xl font-medium">
                  {error}
                </div>
              )}

              <div>
                <label htmlFor="reset-email" className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5">
                  Email Address
                </label>
                <div className="relative">
                  <Mail size={17} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                  <input
                    id="reset-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@example.com"
                    autoComplete="email"
                    className="w-full min-h-[46px] pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 bg-gray-50/70 text-sm focus:border-[#2563EB] focus:bg-white focus:ring-2 focus:ring-[#2563EB]/15 outline-none transition-all"
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
                    <Loader2 size={16} className="animate-spin" /> Sending link…
                  </>
                ) : (
                  <>
                    <span>Send Reset Link</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>

              <div className="pt-2 text-center">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-1.5 text-xs text-gray-500 hover:text-[#2563EB] font-semibold transition-colors py-1"
                >
                  <ArrowLeft size={14} /> Remember your password? Sign in
                </Link>
              </div>
            </form>
          </div>
        )}

        <div className="mt-8 text-center text-xs text-gray-400 flex items-center justify-center gap-1.5">
          <ShieldCheck size={14} className="text-emerald-500" />
          <span>Secure password reset via Supabase Auth</span>
        </div>
      </div>
    </div>
  );
}
