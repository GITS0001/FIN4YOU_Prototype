import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, Loader2 } from 'lucide-react';
import { supabase } from '../../lib/supabase';

function Input({ icon: Icon, type = 'text', id, label, value, onChange, error, placeholder, right }) {
  return (
    <div>
      <label htmlFor={id} className="block text-xs font-bold text-gray-600 uppercase tracking-wider mb-1.5">{label}</label>
      <div className="relative">
        {Icon && <Icon size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />}
        <input
          id={id}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className={`w-full ${Icon ? 'pl-9' : 'pl-3.5'} ${right ? 'pr-10' : 'pr-3.5'} py-3 rounded-xl border text-sm transition-all outline-none
            ${error ? 'border-red-400 bg-red-50 focus:border-red-500' : 'border-gray-200 bg-gray-50 focus:border-[#2563EB] focus:bg-white focus:ring-2 focus:ring-[#2563EB]/15'}`}
        />
        {right}
      </div>
      {error && <p className="text-xs text-red-500 mt-1 font-medium">{error}</p>}
    </div>
  );
}

function PasswordInput({ id, label, value, onChange, error, placeholder }) {
  const [show, setShow] = useState(false);
  return (
    <Input
      icon={Lock}
      id={id}
      label={label}
      type={show ? 'text' : 'password'}
      value={value}
      onChange={onChange}
      error={error}
      placeholder={placeholder}
      right={
        <button
          type="button"
          onClick={() => setShow(v => !v)}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          aria-label={show ? 'Hide password' : 'Show password'}
        >
          {show ? <EyeOff size={16} /> : <Eye size={16} />}
        </button>
      }
    />
  );
}

function ErrorBanner({ msg }) {
  if (!msg) return null;
  return (
    <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-xl font-medium">
      {msg}
    </div>
  );
}

// ─── Login Form ───────────────────────────────────────────────
export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const validate = () => {
    const e = {};
    if (!email) e.email = 'Email is required.';
    else if (!/\S+@\S+\.\S+/.test(email)) e.email = 'Enter a valid email address.';
    if (!password) e.password = 'Password is required.';
    return e;
  };

  const handleSubmit = async (ev) => {
    ev.preventDefault();
    const e = validate();
    setErrors(e);
    if (Object.keys(e).length) return;
    setLoading(true);
    setApiError('');
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    setLoading(false);
    if (error) {
      setApiError(error.message.includes('Invalid') ? 'Incorrect email or password. Please try again.' : error.message);
    } else {
      navigate('/dashboard');
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-4">
      <ErrorBanner msg={apiError} />
      <Input icon={Mail} id="login-email" label="Email Address" type="email" value={email} onChange={e => setEmail(e.target.value)} error={errors.email} placeholder="you@example.com" />
      <PasswordInput id="login-password" label="Password" value={password} onChange={e => setPassword(e.target.value)} error={errors.password} placeholder="Your password" />
      <div className="flex justify-end">
        <Link to="/forgot-password" className="text-xs text-[#2563EB] font-semibold hover:underline">Forgot password?</Link>
      </div>
      <button
        type="submit"
        disabled={loading}
        className="w-full flex items-center justify-center gap-2 py-3.5 bg-[#2563EB] text-white font-bold rounded-xl hover:bg-[#1D4ED8] disabled:opacity-60 disabled:cursor-not-allowed transition-colors shadow-blue text-sm"
      >
        {loading ? <><Loader2 size={16} className="animate-spin" /> Signing in…</> : 'Login →'}
      </button>
      <p className="text-center text-xs text-gray-500 pt-1">
        Don't have an account?{' '}
        <Link to="/signup" className="text-[#2563EB] font-semibold hover:underline">Sign up</Link>
      </p>
    </form>
  );
}

// ─── Signup Form ──────────────────────────────────────────────
export function SignupForm() {
  const [step, setStep] = useState(1);
  const [fields, setFields] = useState({ name: '', username: '', email: '', password: '', confirm: '' });
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const set = (k) => (e) => setFields(f => ({ ...f, [k]: e.target.value }));

  const validateStep1 = () => {
    const e = {};
    if (!fields.name.trim()) e.name = 'Full name is required.';
    return e;
  };

  const validateStep2 = () => {
    const e = {};
    if (!fields.email) e.email = 'Email is required.';
    else if (!/\S+@\S+\.\S+/.test(fields.email)) e.email = 'Enter a valid email address.';
    if (!fields.password || fields.password.length < 8) e.password = 'Password must be at least 8 characters.';
    if (!fields.confirm || fields.confirm !== fields.password) e.confirm = 'Passwords do not match.';
    return e;
  };

  const nextStep = () => {
    const e = validateStep1();
    setErrors(e);
    if (!Object.keys(e).length) setStep(2);
  };

  const handleSubmit = async (ev) => {
    ev.preventDefault();
    const e = validateStep2();
    setErrors(e);
    if (Object.keys(e).length) return;
    setLoading(true);
    setApiError('');
    const { data, error } = await supabase.auth.signUp({
      email: fields.email,
      password: fields.password,
      options: { data: { username: fields.username || fields.name, full_name: fields.name } },
    });
    setLoading(false);
    if (error) {
      setApiError(error.message.includes('already registered') ? 'An account with this email already exists. Please log in.' : error.message);
    } else if (data.session) {
      navigate('/dashboard');
    } else {
      setSuccess(true);
    }
  };

  if (success) {
    return (
      <div className="text-center py-6">
        <div className="w-16 h-16 bg-[#EFF6FF] rounded-full grid place-items-center text-[#2563EB] text-3xl mx-auto mb-4">✓</div>
        <h3 className="text-xl font-bold text-[#0B0F19] mb-2">You're all set!</h3>
        <p className="text-gray-500 text-sm mb-6">Your account is ready. <Link to="/login" className="text-[#2563EB] font-semibold">Log in now →</Link></p>
      </div>
    );
  }

  return (
    <form onSubmit={step === 1 ? (e) => { e.preventDefault(); nextStep(); } : handleSubmit} noValidate className="space-y-4">
      {/* Progress indicator */}
      <div className="flex gap-2 mb-2">
        {[1,2].map(s => (
          <div key={s} className={`h-1 flex-1 rounded-full transition-colors ${s <= step ? 'bg-[#2563EB]' : 'bg-gray-200'}`} />
        ))}
      </div>
      <p className="text-xs text-gray-400 font-medium">Step {step} of 2 — {step === 1 ? 'Personal Details' : 'Account Details'}</p>

      <ErrorBanner msg={apiError} />

      {step === 1 && (
        <>
          <Input id="signup-name" label="Full Name" value={fields.name} onChange={set('name')} error={errors.name} placeholder="Your full name" />
          <Input id="signup-username" label="Username (optional)" value={fields.username} onChange={set('username')} placeholder="Choose a username" />
          <button type="submit" className="w-full py-3.5 bg-[#2563EB] text-white font-bold rounded-xl hover:bg-[#1D4ED8] transition-colors shadow-blue text-sm">
            Next →
          </button>
        </>
      )}

      {step === 2 && (
        <>
          <Input icon={Mail} id="signup-email" label="Email Address" type="email" value={fields.email} onChange={set('email')} error={errors.email} placeholder="you@example.com" />
          <PasswordInput id="signup-password" label="Password" value={fields.password} onChange={set('password')} error={errors.password} placeholder="Min 8 characters" />
          <PasswordInput id="signup-confirm" label="Confirm Password" value={fields.confirm} onChange={set('confirm')} error={errors.confirm} placeholder="Repeat your password" />
          <div className="flex gap-3">
            <button type="button" onClick={() => setStep(1)} className="flex-1 py-3.5 border border-gray-200 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 text-sm transition-colors">
              ← Back
            </button>
            <button type="submit" disabled={loading} className="flex-1 flex items-center justify-center gap-2 py-3.5 bg-[#2563EB] text-white font-bold rounded-xl hover:bg-[#1D4ED8] disabled:opacity-60 disabled:cursor-not-allowed transition-colors shadow-blue text-sm">
              {loading ? <><Loader2 size={16} className="animate-spin" /> Creating…</> : 'Create Account →'}
            </button>
          </div>
        </>
      )}

      <p className="text-center text-xs text-gray-500">
        Already have an account?{' '}
        <Link to="/login" className="text-[#2563EB] font-semibold hover:underline">Sign in</Link>
      </p>
    </form>
  );
}
