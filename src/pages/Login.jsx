import { Link } from 'react-router-dom';
import { LoginForm } from '../components/auth/AuthForms';
import AuthVideoPanel from '../components/auth/AuthVideoPanel';
import { ShieldCheck } from 'lucide-react';

export default function Login() {
  return (
    <div className="min-h-screen lg:h-screen lg:overflow-hidden grid grid-cols-1 lg:grid-cols-2 bg-white">
      {/* Left 50% Video Panel */}
      <div className="w-full h-[190px] sm:h-[240px] lg:h-full lg:max-h-screen">
        <AuthVideoPanel
          badgeText="Financial Transformation"
          heading="Welcome back to clarity."
          subheading="Log in to view your financial overview, track budgets, and consult Artha AI."
        />
      </div>

      {/* Right 50% Login Form Panel */}
      <div className="w-full h-full flex flex-col justify-center items-center p-5 sm:p-8 lg:p-14 overflow-y-auto bg-white">
        <div className="w-full max-w-[420px] my-auto py-4">
          {/* Mobile-only logo */}
          <div className="lg:hidden mb-5 flex items-center justify-between">
            <Link to="/" className="inline-flex items-center gap-2 font-bold text-base text-[#0B0F19]">
              <span className="w-7 h-7 bg-[#2563EB] text-white rounded-lg grid place-items-center text-xs font-black">
                F
              </span>
              <span className="font-display">
                Fin4<strong className="text-[#2563EB]">You</strong>
              </span>
            </Link>
            <span className="text-xs text-gray-400 font-medium">Personal Finance</span>
          </div>

          {/* Form Header */}
          <div className="mb-6 sm:mb-8">
            <span className="inline-block text-xs font-bold text-[#2563EB] uppercase tracking-wider mb-1.5">
              Secure Sign In
            </span>
            <h1 className="text-2xl sm:text-3xl font-black text-[#0B0F19] tracking-tight mb-2 font-display">
              Welcome back
            </h1>
            <p className="text-sm text-gray-500 leading-relaxed">
              Enter your credentials to access your Fin4You dashboard and financial assistant.
            </p>
          </div>

          {/* Existing Working Login Form */}
          <LoginForm />

          {/* Bottom Security Assurance */}
          <div className="mt-8 pt-6 border-t border-gray-100 flex items-center justify-between text-xs text-gray-400">
            <span>© 2026 Fin4You</span>
            <span className="inline-flex items-center gap-1 text-emerald-600 font-medium">
              <ShieldCheck size={13} />
              256-bit Secure
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
