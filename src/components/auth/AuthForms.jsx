import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, User, CheckCircle2, ArrowRight, ArrowLeft, Loader2 } from 'lucide-react';
import { supabase } from '../../lib/supabase';

function Input({ icon: Icon, type = 'text', id, label, value, onChange, error, placeholder, right, autoComplete }) {
  return (
    <div>
      <label htmlFor={id} className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5">
        {label}
      </label>
      <div className="relative">
        {Icon && (
          <Icon
            size={17}
            className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
            aria-hidden="true"
          />
        )}
        <input
          id={id}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          autoComplete={autoComplete}
          aria-invalid={!!error}
          aria-describedby={error ? `${id}-error` : undefined}
          className={`w-full min-h-[46px] ${Icon ? 'pl-10' : 'pl-3.5'} ${right ? 'pr-11' : 'pr-3.5'} py-2.5 rounded-xl border text-sm transition-all outline-none
            ${
              error
                ? 'border-red-400 bg-red-50/50 text-red-900 focus:border-red-500 focus:ring-2 focus:ring-red-200'
                : 'border-gray-200 bg-gray-50/70 hover:bg-white text-gray-900 focus:border-[#2563EB] focus:bg-white focus:ring-2 focus:ring-[#2563EB]/15'
            }`}
        />
        {right}
      </div>
      {error && (
        <p id={`${id}-error`} className="text-xs text-red-600 mt-1.5 font-medium flex items-center gap-1">
          <span>●</span> {error}
        </p>
      )}
    </div>
  );
}

function PasswordInput({ id, label, value, onChange, error, placeholder, autoComplete }) {
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
      autoComplete={autoComplete}
      right={
        <button
          type="button"
          onClick={() => setShow((v) => !v)}
          className="absolute right-2.5 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 rounded-lg touch-target"
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
    <div
      role="alert"
      className="bg-red-50 border border-red-200 text-red-700 text-xs sm:text-sm px-4 py-3 rounded-xl font-medium leading-relaxed"
    >
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
    if (!email.trim()) e.email = 'Email is required.';
    else if (!/\S+@\S+\.\S+/.test(email.trim())) e.email = 'Enter a valid email address.';
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
    const { error } = await supabase.auth.signInWithPassword({
      email: email.trim(),
      password,
    });
    setLoading(false);
    if (error) {
      setApiError(
        error.message.includes('Invalid login credentials')
          ? 'Incorrect email or password. Please try again or reset your password.'
          : error.message
      );
    } else {
      navigate('/dashboard');
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-4">
      <ErrorBanner msg={apiError} />

      <Input
        icon={Mail}
        id="login-email"
        label="Email Address"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        error={errors.email}
        placeholder="name@example.com"
        autoComplete="email"
      />

      <PasswordInput
        id="login-password"
        label="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        error={errors.password}
        placeholder="Enter your password"
        autoComplete="current-password"
      />

      <div className="flex justify-end pt-0.5">
        <Link
          to="/forgot-password"
          className="text-xs text-[#2563EB] font-semibold hover:underline focus:outline-none focus-visible:ring-1 focus-visible:ring-blue-400 rounded py-1"
        >
          Forgot password?
        </Link>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full min-h-[46px] flex items-center justify-center gap-2 py-3 bg-[#2563EB] text-white font-bold rounded-xl hover:bg-[#1D4ED8] active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed transition-all shadow-blue text-sm touch-target"
      >
        {loading ? (
          <>
            <Loader2 size={16} className="animate-spin" /> Signing in…
          </>
        ) : (
          <>
            <span>Sign In to Fin4You</span>
            <ArrowRight size={16} />
          </>
        )}
      </button>

      <div className="text-center pt-2">
        <p className="text-xs text-gray-500">
          Don't have an account?{' '}
          <Link to="/signup" className="text-[#2563EB] font-bold hover:underline">
            Create an account
          </Link>
        </p>
      </div>
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

  const set = (k) => (e) => setFields((f) => ({ ...f, [k]: e.target.value }));

  const validateStep1 = () => {
    const e = {};
    if (!fields.name.trim()) e.name = 'Full name is required.';
    return e;
  };

  const validateStep2 = () => {
    const e = {};
    if (!fields.email.trim()) e.email = 'Email is required.';
    else if (!/\S+@\S+\.\S+/.test(fields.email.trim())) e.email = 'Enter a valid email address.';
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
      email: fields.email.trim(),
      password: fields.password,
      options: {
        data: {
          username: fields.username.trim() || fields.name.trim(),
          full_name: fields.name.trim(),
        },
      },
    });
    setLoading(false);
    if (error) {
      setApiError(
        error.message.includes('already registered')
          ? 'An account with this email already exists. Please log in.'
          : error.message
      );
    } else if (data.session) {
      navigate('/dashboard');
    } else {
      setSuccess(true);
    }
  };

  if (success) {
    return (
      <div className="text-center py-6 bg-blue-50/50 rounded-2xl p-6 border border-blue-100">
        <div className="w-14 h-14 bg-emerald-100 text-emerald-700 rounded-full grid place-items-center text-2xl mx-auto mb-4">
          ✓
        </div>
        <h3 className="text-xl font-bold text-[#0B0F19] mb-2 font-display">Account Created!</h3>
        <p className="text-gray-600 text-sm mb-6 leading-relaxed">
          Please check your email <strong className="text-gray-900">{fields.email}</strong> to verify your account, or sign in now.
        </p>
        <Link
          to="/login"
          className="inline-flex items-center gap-2 px-6 py-3.5 bg-[#2563EB] text-white font-bold rounded-xl text-sm shadow-blue hover:bg-[#1D4ED8] transition-all touch-target"
        >
          <span>Log In Now</span>
          <ArrowRight size={16} />
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={step === 1 ? (e) => { e.preventDefault(); nextStep(); } : handleSubmit} noValidate className="space-y-4">
      {/* 2-Step Segment Progress Indicator */}
      <div className="space-y-1.5 mb-2">
        <div className="flex gap-2">
          {[1, 2].map((s) => (
            <div
              key={s}
              className={`h-1.5 flex-1 rounded-full transition-all duration-300 ${
                s <= step ? 'bg-[#2563EB]' : 'bg-gray-200'
              }`}
            />
          ))}
        </div>
        <div className="flex justify-between items-center text-[11px] font-semibold text-gray-500">
          <span>Step {step} of 2</span>
          <span>{step === 1 ? 'Personal Profile' : 'Security & Credentials'}</span>
        </div>
      </div>

      <ErrorBanner msg={apiError} />

      {step === 1 && (
        <>
          <Input
            icon={User}
            id="signup-name"
            label="Full Name"
            value={fields.name}
            onChange={set('name')}
            error={errors.name}
            placeholder="e.g. Aditya Sharma"
            autoComplete="name"
          />
          <Input
            id="signup-username"
            label="Username (optional)"
            value={fields.username}
            onChange={set('username')}
            placeholder="e.g. aditya_s"
            autoComplete="username"
          />
          <button
            type="submit"
            className="w-full min-h-[46px] flex items-center justify-center gap-2 py-3 bg-[#2563EB] text-white font-bold rounded-xl hover:bg-[#1D4ED8] active:scale-[0.99] transition-all shadow-blue text-sm touch-target mt-2"
          >
            <span>Next: Account Details</span>
            <ArrowRight size={16} />
          </button>
        </>
      )}

      {step === 2 && (
        <>
          <Input
            icon={Mail}
            id="signup-email"
            label="Email Address"
            type="email"
            value={fields.email}
            onChange={set('email')}
            error={errors.email}
            placeholder="name@example.com"
            autoComplete="email"
          />
          <PasswordInput
            id="signup-password"
            label="Password"
            value={fields.password}
            onChange={set('password')}
            error={errors.password}
            placeholder="Min 8 characters"
            autoComplete="new-password"
          />
          <PasswordInput
            id="signup-confirm"
            label="Confirm Password"
            value={fields.confirm}
            onChange={set('confirm')}
            error={errors.confirm}
            placeholder="Repeat your password"
            autoComplete="new-password"
          />
          <div className="flex gap-2.5 pt-1">
            <button
              type="button"
              onClick={() => setStep(1)}
              className="flex-1 min-h-[46px] flex items-center justify-center gap-1.5 py-3 border border-gray-200 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 active:bg-gray-100 text-sm transition-colors touch-target"
            >
              <ArrowLeft size={16} /> Back
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-[2] min-h-[46px] flex items-center justify-center gap-2 py-3 bg-[#2563EB] text-white font-bold rounded-xl hover:bg-[#1D4ED8] active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed transition-all shadow-blue text-sm touch-target"
            >
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" /> Creating…
                </>
              ) : (
                <>
                  <span>Create Account</span>
                  <CheckCircle2 size={16} />
                </>
              )}
            </button>
          </div>
        </>
      )}

      <div className="text-center pt-2">
        <p className="text-xs text-gray-500">
          Already have an account?{' '}
          <Link to="/login" className="text-[#2563EB] font-bold hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </form>
  );
}
