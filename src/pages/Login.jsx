import { Link } from 'react-router-dom';
import { LoginForm } from '../components/auth/AuthForms';

export default function Login() {
  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left brand panel */}
      <div className="hidden lg:flex flex-col justify-between p-12 bg-[#0B0F19] text-white relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute w-80 h-80 rounded-full blur-[80px] bg-[#2563EB]/20 -left-20 top-0" />
          <div className="absolute w-64 h-64 rounded-full blur-[80px] bg-[#1D4ED8]/15 right-0 bottom-0" />
        </div>
        <Link to="/" className="relative flex items-center gap-2.5 font-bold text-lg">
          <span className="w-9 h-9 bg-[#2563EB] rounded-xl grid place-items-center font-black">F</span>
          Fin4<strong className="text-[#93C5FD]">You</strong>
        </Link>
        <div className="relative">
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 mb-8 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold text-white/60 uppercase tracking-wider">Overview</span>
              <span className="text-xs text-green-400">● Live</span>
            </div>
            <div className="text-3xl font-black tracking-tight mb-1">₹24,580</div>
            <div className="text-xs text-white/50 mb-3">This month · ↑ 18.4%</div>
            <div className="flex items-end gap-1.5 h-14">
              {[40,62,38,78,52,88].map((h,i)=>(
                <div key={i} className="flex-1 bg-[#2563EB] rounded-t-sm" style={{height:`${h}%`,opacity:.4+i*.1}} />
              ))}
            </div>
            <p className="text-[10px] text-white/30 italic mt-2">* Illustrative data only</p>
          </div>
          <h2 className="text-2xl font-black leading-tight mb-3">
            Welcome back.<br />
            <em className="not-italic text-[#93C5FD]">Your finances await.</em>
          </h2>
          <p className="text-sm text-white/55 leading-relaxed">Log in to view your financial overview, spending insights, and summaries.</p>
        </div>
        <p className="relative text-xs text-white/30">© 2026 Fin4You</p>
      </div>

      {/* Right form panel */}
      <div className="flex items-center justify-center p-6 md:p-12 bg-white">
        <div className="w-full max-w-[400px]">
          <Link to="/" className="lg:hidden flex items-center gap-2 font-bold text-base mb-8 text-[#0B0F19]">
            <span className="w-7 h-7 bg-[#2563EB] text-white rounded-lg grid place-items-center text-xs font-black">F</span>
            Fin4<strong className="text-[#2563EB]">You</strong>
          </Link>
          <div className="mb-8">
            <h1 className="text-2xl font-black text-[#0B0F19] tracking-tight mb-2">Sign in</h1>
            <p className="text-sm text-gray-500">Enter your email and password to access your account.</p>
          </div>
          <LoginForm />
        </div>
      </div>
    </div>
  );
}
