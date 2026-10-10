import { motion } from 'motion/react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, TrendingUp, Sparkles, Shield, CheckCircle2 } from 'lucide-react';

const reveal = {
  hidden: { opacity: 0, y: 24 },
  visible: (d = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: d, duration: 0.55, ease: [0.4, 0, 0.2, 1] },
  }),
};

export default function Hero() {
  return (
    <section className="relative pt-12 pb-16 sm:pt-20 sm:pb-24 lg:pt-28 lg:pb-28 bg-white overflow-hidden" id="top">
      {/* Background Soft Glows */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 65% 55% at 75% 25%, #EFF6FF 0%, rgba(248, 250, 252, 0.5) 50%, transparent 80%)',
        }}
      />
      <div className="absolute top-1/4 -left-40 w-96 h-96 bg-blue-50/50 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-[1200px] mx-auto px-4 sm:px-6 relative">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 items-center">
          {/* Copy Column (7 cols on lg) */}
          <motion.div
            variants={reveal}
            initial="hidden"
            animate="visible"
            className="lg:col-span-7 flex flex-col items-start"
          >
            {/* Trust Pill */}
            <div className="inline-flex items-center gap-2 bg-[#EFF6FF] text-[#2563EB] px-3.5 py-1.5 rounded-full text-xs font-bold tracking-wider uppercase mb-5 border border-blue-200/50 shadow-xs">
              <span className="w-2 h-2 bg-[#2563EB] rounded-full animate-pulse-dot" />
              <span>Personal Financial Health Copilot</span>
            </div>

            {/* Headline */}
            <h1 className="text-3xl sm:text-5xl lg:text-[3.5rem] font-black leading-[1.1] tracking-tight text-[#0B0F19] mb-5 font-display">
              Make Sense of <br />
              <span className="text-gradient">Your Money.</span>
            </h1>

            {/* Supporting Copy */}
            <p className="text-base sm:text-lg text-gray-600 leading-relaxed max-w-[520px] mb-8">
              Understand your cash flow, explore spending patterns, and make verified financial decisions with deterministic arithmetic and Artha AI.
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 w-full sm:w-auto mb-10">
              <Link
                to="/signup"
                className="inline-flex items-center justify-center gap-2 px-7 py-4 bg-[#2563EB] text-white font-bold rounded-xl shadow-blue hover:bg-[#1D4ED8] active:scale-[0.99] transition-all text-base touch-target"
              >
                <span>Get Started Free</span>
                <ArrowUpRight size={18} />
              </Link>
              <a
                href="#animation"
                className="inline-flex items-center justify-center gap-2 px-6 py-4 bg-white text-gray-700 font-bold rounded-xl border border-gray-200 hover:border-blue-300 hover:text-[#2563EB] hover:bg-[#EFF6FF]/60 transition-all text-base touch-target"
              >
                <span>Watch How It Works</span>
              </a>
            </div>

            {/* Social Proof & Guarantees */}
            <div className="flex flex-wrap items-center gap-5 pt-2 border-t border-gray-100 w-full">
              <div className="flex items-center gap-2 text-xs font-semibold text-gray-700">
                <CheckCircle2 size={16} className="text-emerald-700 flex-shrink-0" />
                <span>No credit card needed</span>
              </div>
              <div className="flex items-center gap-2 text-xs font-semibold text-gray-700">
                <CheckCircle2 size={16} className="text-emerald-700 flex-shrink-0" />
                <span>256-bit secure encryption</span>
              </div>
              <div className="flex items-center gap-2 text-xs font-semibold text-gray-700">
                <CheckCircle2 size={16} className="text-emerald-700 flex-shrink-0" />
                <span>Deterministic financial math</span>
              </div>
            </div>
          </motion.div>

          {/* Interactive Financial Preview Card (5 cols on lg) */}
          <motion.div
            variants={reveal}
            initial="hidden"
            animate="visible"
            custom={0.2}
            className="lg:col-span-5 relative w-full flex justify-center"
          >
            <div className="relative w-full max-w-[430px]">
              {/* Main Financial Card */}
              <div className="bg-white rounded-2xl shadow-xl shadow-blue-900/5 border border-gray-200/90 p-5 sm:p-6 relative z-10">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-lg bg-blue-50 text-[#2563EB] grid place-items-center font-bold text-xs">
                      ₹
                    </div>
                    <div>
                      <span className="text-sm font-bold text-[#0B0F19] block leading-tight">Monthly Overview</span>
                      <span className="text-[10px] text-gray-600 font-medium">May 2026 Cycle</span>
                    </div>
                  </div>
                  <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200/60">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse" />
                    Verified
                  </span>
                </div>

                <div className="mb-1">
                  <span className="text-[10px] font-bold tracking-widest uppercase text-gray-700">NET AVAILABLE</span>
                </div>
                <div className="text-3xl sm:text-4xl font-black tracking-tight text-[#0B0F19] mb-1 font-display">
                  ₹24,580
                </div>
                <div className="text-xs font-bold text-emerald-700 mb-4 flex items-center gap-1">
                  <TrendingUp size={14} />
                  <span>+18.4% savings run-rate vs last cycle</span>
                </div>

                {/* SVG Trend Line */}
                <div className="relative py-1">
                  <svg className="w-full h-20" viewBox="0 0 280 70" fill="none" preserveAspectRatio="none">
                    <path
                      d="M0 55 C30 48, 45 58, 70 42 S110 38, 130 24 S165 42, 190 28 S230 10, 255 18 S270 12, 280 4"
                      stroke="#2563EB"
                      strokeWidth="2.75"
                      strokeLinecap="round"
                    />
                    <path
                      d="M0 70V55 C30 48, 45 58, 70 42 S110 38, 130 24 S165 42, 190 28 S230 10, 255 18 S270 12, 280 4 V70Z"
                      fill="url(#hero-gradient)"
                      opacity="0.18"
                    />
                    <defs>
                      <linearGradient id="hero-gradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#2563EB" />
                        <stop offset="100%" stopColor="#2563EB" stopOpacity="0" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="flex justify-between text-[11px] text-gray-600 font-medium pt-1">
                    {['Jan', 'Feb', 'Mar', 'Apr', 'May'].map((m) => (
                      <span key={m}>{m}</span>
                    ))}
                  </div>
                </div>

                {/* Inline Stats for Mobile & Desktop */}
                <div className="mt-4 pt-4 border-t border-gray-100 grid grid-cols-2 gap-3 text-left">
                  <div className="bg-gray-50/80 rounded-xl p-2.5 border border-gray-100">
                    <span className="text-[10px] font-bold tracking-wider uppercase text-gray-700 block mb-0.5">
                      Savings Ratio
                    </span>
                    <span className="text-base font-black text-[#0B0F19]">36.9%</span>
                    <span className="text-[10px] text-emerald-700 block mt-0.5 font-bold">Target &gt; 25%</span>
                  </div>
                  <div className="bg-gray-50/80 rounded-xl p-2.5 border border-gray-100">
                    <span className="text-[10px] font-bold tracking-wider uppercase text-gray-700 block mb-0.5">
                      Safety Buffer
                    </span>
                    <span className="text-base font-black text-emerald-800">Maintained</span>
                    <span className="text-[10px] text-gray-600 block mt-0.5 font-medium">90d risk: 0.0%</span>
                  </div>
                </div>

                <p className="text-[10px] text-gray-600 italic mt-3 text-center">
                  * Live interactive dashboard view
                </p>
              </div>

              {/* Desktop Floating Badges (Safely bounded to avoid mobile overflow) */}
              <motion.div
                className="hidden sm:block absolute -left-6 bottom-6 bg-white rounded-xl shadow-lg border border-gray-100 p-3.5 z-20 min-w-[145px] animate-float-1"
                aria-hidden="true"
              >
                <div className="flex items-center gap-1.5 text-xs text-emerald-800 font-bold mb-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-600" />
                  <span>ON TRACK</span>
                </div>
                <div className="text-[10px] font-bold tracking-widest uppercase text-gray-700">SAVINGS RATE</div>
                <div className="text-lg font-black text-[#0B0F19]">36.9%</div>
                <div className="h-1.5 bg-gray-100 rounded-full mt-2 overflow-hidden">
                  <div className="h-full bg-emerald-600 rounded-full" style={{ width: '36.9%' }} />
                </div>
              </motion.div>

              <motion.div
                className="hidden sm:block absolute -right-5 top-6 bg-white rounded-xl shadow-lg border border-gray-100 p-3.5 z-20 min-w-[155px] animate-float-2"
                aria-hidden="true"
              >
                <div className="flex items-center gap-1.5 text-[#2563EB] mb-1">
                  <Sparkles size={14} />
                  <span className="text-[10px] font-bold tracking-widest uppercase text-gray-700">ARTHA AI</span>
                </div>
                <div className="text-xs font-bold text-[#0B0F19]">Discretionary -8%</div>
                <span className="text-[10px] text-gray-600 font-medium">Optimized ₹2,400</span>
              </motion.div>
            </div>
          </motion.div>
        </div>

        {/* Scroll cue */}
        <div className="flex flex-col items-center gap-2 pt-12 text-gray-600">
          <span className="text-[10px] tracking-[0.14em] uppercase font-semibold">Scroll to explore</span>
          <div className="w-px h-10 bg-gradient-to-b from-gray-400 to-transparent animate-scroll" />
        </div>
      </div>
    </section>
  );
}
