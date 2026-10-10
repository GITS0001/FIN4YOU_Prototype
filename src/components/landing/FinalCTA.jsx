import { Link } from 'react-router-dom';
import { ArrowUpRight, ArrowRight, ShieldCheck } from 'lucide-react';

export default function FinalCTA() {
  return (
    <section className="relative bg-[#0B0F19] text-white py-20 sm:py-28 overflow-hidden text-center" id="start">
      {/* Background radial glows */}
      <div className="absolute w-[500px] h-[500px] rounded-full blur-[110px] bg-[#2563EB]/25 -left-32 -top-32 pointer-events-none" />
      <div className="absolute w-[450px] h-[450px] rounded-full blur-[110px] bg-[#059669]/15 -right-20 -bottom-20 pointer-events-none" />

      <div className="relative max-w-[680px] mx-auto px-4 sm:px-6">
        <span className="inline-flex items-center gap-2 text-xs font-bold tracking-widest uppercase text-[#93C5FD] mb-4 bg-white/5 border border-white/10 px-3 py-1 rounded-full">
          <span className="w-1.5 h-1.5 bg-[#60A5FA] rounded-full animate-pulse" />
          Financial Confidence & Clarity
        </span>

        <h2 className="text-3xl sm:text-4xl md:text-5xl font-black tracking-tight leading-[1.12] mb-5 font-display">
          Your Financial Journey <br />
          Starts <span className="text-[#93C5FD]">Today.</span>
        </h2>

        <p className="text-gray-300 text-base sm:text-lg leading-relaxed mb-8 max-w-[500px] mx-auto">
          Join Fin4You and take your first step toward greater clarity, verified runway, and full control over your personal finances.
        </p>

        <div className="flex flex-col sm:flex-row gap-3.5 justify-center items-stretch sm:items-center max-w-sm sm:max-w-none mx-auto mb-8">
          <Link
            to="/signup"
            className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-[#2563EB] text-white font-bold rounded-xl shadow-blue hover:bg-[#1D4ED8] active:scale-[0.99] transition-all text-base touch-target"
          >
            <span>Get Started Free</span>
            <ArrowUpRight size={18} />
          </Link>
          <Link
            to="/login"
            className="inline-flex items-center justify-center gap-2 px-7 py-4 bg-white/10 hover:bg-white/15 text-white font-bold rounded-xl border border-white/20 transition-all text-base touch-target"
          >
            Sign In
          </Link>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-4 text-xs text-gray-300">
          <span className="flex items-center gap-1.5">
            <ShieldCheck size={14} className="text-emerald-400" /> Free personal tier
          </span>
          <span>•</span>
          <span>No credit card required</span>
          <span>•</span>
          <span>Setup in under 60 seconds</span>
        </div>
      </div>
    </section>
  );
}
