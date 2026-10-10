import { Link } from 'react-router-dom';
import { SignupForm } from '../components/auth/AuthForms';

export default function Signup() {
  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left brand panel */}
      <div className="hidden lg:flex flex-col justify-between p-12 bg-[#EFF6FF] relative overflow-hidden">
        <div className="absolute w-96 h-96 rounded-full blur-[100px] bg-[#2563EB]/12 -right-24 -top-24 pointer-events-none" />
        <Link to="/" className="relative flex items-center gap-2.5 font-bold text-lg text-[#0B0F19]">
          <span className="w-9 h-9 bg-[#2563EB] text-white rounded-xl grid place-items-center font-black">F</span>
          Fin4<strong className="text-[#2563EB]">You</strong>
        </Link>
        <div className="relative">
          <div className="flex gap-3 mb-6 flex-wrap">
            {['📊 Track Spending','💡 Get Insights','📈 Plan Ahead'].map(t=>(
              <span key={t} className="bg-white border border-gray-200 text-[#2563EB] text-xs font-bold px-3 py-1.5 rounded-full shadow-sm">{t}</span>
            ))}
          </div>
          <h2 className="text-3xl font-black text-[#0B0F19] leading-tight mb-4">
            Start with a<br />
            <em className="not-italic text-[#2563EB]">clearer financial future.</em>
          </h2>
          <p className="text-gray-500 text-sm leading-relaxed max-w-[340px]">
            Create your Fin4You account in seconds. No credit card, no bank link required — just your email and a password.
          </p>
          <div className="mt-8 grid grid-cols-3 gap-3">
            {[['📊','Dashboard','Full overview'],['◒','Spending','Category breakdown'],['↗','Forecasts','Future trends']].map(([i,t,s])=>(
              <div key={t} className="bg-white rounded-xl p-3 border border-gray-100 shadow-sm">
                <div className="text-xl mb-1">{i}</div>
                <div className="text-xs font-bold text-[#0B0F19]">{t}</div>
                <div className="text-[10px] text-gray-400">{s}</div>
              </div>
            ))}
          </div>
        </div>
        <p className="relative text-xs text-gray-400">© 2026 Fin4You</p>
      </div>

      {/* Right form panel */}
      <div className="flex items-center justify-center p-6 md:p-12 bg-white">
        <div className="w-full max-w-[400px]">
          <Link to="/" className="lg:hidden flex items-center gap-2 font-bold text-base mb-8 text-[#0B0F19]">
            <span className="w-7 h-7 bg-[#2563EB] text-white rounded-lg grid place-items-center text-xs font-black">F</span>
            Fin4<strong className="text-[#2563EB]">You</strong>
          </Link>
          <div className="mb-8">
            <h1 className="text-2xl font-black text-[#0B0F19] tracking-tight mb-2">Create your account</h1>
            <p className="text-sm text-gray-500">Join Fin4You and start making smarter financial decisions.</p>
          </div>
          <SignupForm />
        </div>
      </div>
    </div>
  );
}
