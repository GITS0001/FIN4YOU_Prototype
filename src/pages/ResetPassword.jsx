import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
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
    if (!password || password.length < 8) { setError('Password must be at least 8 characters.'); return; }
    if (password !== confirm) { setError('Passwords do not match.'); return; }
    setLoading(true);
    setError('');
    const { error: err } = await supabase.auth.updateUser({ password });
    setLoading(false);
    if (err) { setError(err.message); } else { setDone(true); setTimeout(() => navigate('/dashboard'), 2000); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
      <div className="w-full max-w-[420px]">
        <Link to="/" className="flex items-center gap-2 font-bold text-base mb-10 text-[#0B0F19]">
          <span className="w-8 h-8 bg-[#2563EB] text-white rounded-lg grid place-items-center text-sm font-black">F</span>
          Fin4<strong className="text-[#2563EB]">You</strong>
        </Link>
        <div className="bg-white rounded-2xl shadow-card border border-gray-100 p-8">
          {done ? (
            <div className="text-center">
              <div className="w-16 h-16 bg-[#EFF6FF] rounded-full grid place-items-center text-3xl mx-auto mb-4">✓</div>
              <h2 className="text-xl font-black mb-2 text-[#0B0F19]">Password updated!</h2>
              <p className="text-sm text-gray-500">Redirecting to your dashboard…</p>
            </div>
          ) : (
            <>
              <h1 className="text-2xl font-black text-[#0B0F19] tracking-tight mb-2">Set new password</h1>
              <p className="text-sm text-gray-500 mb-6">Choose a strong password for your account.</p>
              <form onSubmit={handleSubmit} noValidate className="space-y-4">
                {error && <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-xl">{error}</div>}
                {[['reset-password-field','New Password',password,setPassword],['reset-confirm','Confirm Password',confirm,setConfirm]].map(([id,label,val,setter])=>(
                  <div key={id}>
                    <label htmlFor={id} className="block text-xs font-bold text-gray-600 uppercase tracking-wider mb-1.5">{label}</label>
                    <div className="relative">
                      <input id={id} type={show ? 'text' : 'password'} value={val} onChange={e=>setter(e.target.value)} placeholder="Min 8 characters"
                        className="w-full pl-4 pr-10 py-3 rounded-xl border border-gray-200 bg-gray-50 text-sm focus:border-[#2563EB] focus:bg-white focus:ring-2 focus:ring-[#2563EB]/15 outline-none transition-all" />
                      <button type="button" onClick={()=>setShow(v=>!v)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                        {show ? <EyeOff size={16}/> : <Eye size={16}/>}
                      </button>
                    </div>
                  </div>
                ))}
                <button type="submit" disabled={loading} className="w-full flex items-center justify-center gap-2 py-3.5 bg-[#2563EB] text-white font-bold rounded-xl hover:bg-[#1D4ED8] disabled:opacity-60 transition-colors shadow-blue text-sm">
                  {loading ? <><Loader2 size={16} className="animate-spin"/>Updating…</> : 'Update Password →'}
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
