import { Link } from 'react-router-dom';
import { SignupForm } from '../components/auth/AuthForms';
import AuthVideoPanel from '../components/auth/AuthVideoPanel';

export default function Signup() {
  return (
    <div className="min-h-screen lg:h-screen lg:overflow-hidden grid grid-cols-1 lg:grid-cols-2 bg-white">
      {/* Left 50% Video Panel */}
      <div className="w-full h-[280px] sm:h-[340px] lg:h-full lg:max-h-screen">
        <AuthVideoPanel
          badgeText="Financial Clarity Journey"
          heading="Start with clear financial direction."
          subheading="Watch your finances organize effortlessly. Create an account to begin tracking and chat with Artha AI."
        />
      </div>

      {/* Right 50% Signup Form Panel */}
      <div className="w-full h-full flex flex-col justify-center items-center p-6 sm:p-10 lg:p-14 overflow-y-auto bg-white">
        <div className="w-full max-w-[420px] my-auto">
          {/* Mobile-only logo */}
          <div className="lg:hidden mb-6 flex items-center justify-between">
            <Link to="/" className="inline-flex items-center gap-2 font-bold text-base text-[#0B0F19]">
              <span className="w-7 h-7 bg-[#2563EB] text-white rounded-lg grid place-items-center text-xs font-black">
                F
              </span>
              <span>
                Fin4<strong className="text-[#2563EB]">You</strong>
              </span>
            </Link>
            <span className="text-xs text-gray-400 font-medium">Get Started</span>
          </div>

          {/* Form Header */}
          <div className="mb-6">
            <span className="inline-block text-xs font-bold text-[#2563EB] uppercase tracking-wider mb-2">
              Free Personal Account
            </span>
            <h1 className="text-2xl sm:text-3xl font-black text-[#0B0F19] tracking-tight mb-2">
              Create your account
            </h1>
            <p className="text-sm text-gray-500 leading-relaxed">
              No credit card or bank login required. Set up your profile and password in under a minute.
            </p>
          </div>

          {/* Existing Working Signup Form (Supabase Auth) */}
          <SignupForm />

          {/* Bottom Security Assurance */}
          <div className="mt-8 pt-6 border-t border-gray-100 flex items-center justify-between text-xs text-gray-400">
            <span>© 2026 Fin4You</span>
            <span>Privacy & Terms Compliant</span>
          </div>
        </div>
      </div>
    </div>
  );
}
