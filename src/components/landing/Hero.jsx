import { motion } from 'motion/react';
import { Link } from 'react-router-dom';

const reveal = {
  hidden: { opacity: 0, y: 28 },
  visible: (d = 0) => ({ opacity: 1, y: 0, transition: { delay: d, duration: 0.6, ease: [0.4, 0, 0.2, 1] } }),
};

export default function Hero() {
  return (
    <section className="relative pt-20 pb-16 md:pt-28 md:pb-24 bg-white overflow-hidden" id="top">
      {/* Background radial */}
      <div className="absolute inset-0 pointer-events-none" style={{ background: 'radial-gradient(ellipse 70% 60% at 75% 30%, #EFF6FF 0%, transparent 70%)' }} />

      <div className="max-w-[1160px] mx-auto px-6 relative">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">

          {/* Copy */}
          <motion.div variants={reveal} initial="hidden" animate="visible">
            <div className="inline-flex items-center gap-2 bg-[#EFF6FF] text-[#2563EB] px-3.5 py-1.5 rounded-full text-xs font-bold tracking-widest uppercase mb-6">
              <span className="w-1.5 h-1.5 bg-[#2563EB] rounded-full animate-pulse-dot" />
              Personal Financial Assistant
            </div>
            <h1 className="text-4xl md:text-5xl lg:text-[3.4rem] font-black leading-[1.08] tracking-tight text-[#0B0F19] mb-5">
              Make Sense of<br />
              <em className="not-italic text-[#2563EB]">Your Money.</em>
            </h1>
            <p className="text-lg text-gray-500 leading-relaxed max-w-[480px] mb-8">
              Understand your financial activity, explore spending patterns, and make more informed financial decisions with Fin4You.
            </p>
            <div className="flex flex-wrap gap-3 mb-10">
              <Link to="/signup" className="inline-flex items-center gap-2 px-6 py-3.5 bg-[#2563EB] text-white font-bold rounded-xl shadow-blue hover:bg-[#1D4ED8] transition-all hover:-translate-y-0.5 text-[0.95rem]">
                Get Started <span className="text-base">↗</span>
              </Link>
              <a href="#features" className="inline-flex items-center gap-2 px-6 py-3.5 bg-white text-[#2563EB] font-bold rounded-xl border-[1.5px] border-[#2563EB] hover:bg-[#EFF6FF] transition-colors text-[0.95rem]">
                Explore Features
              </a>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex">
                {['#2563EB','#1D4ED8','#3B82F6'].map((c, i) => (
                  <span key={i} className="w-8 h-8 rounded-full border-2 border-white grid place-items-center text-white text-xs font-bold -ml-2 first:ml-0" style={{ background: c }}>
                    {['Y','R','A'][i]}
                  </span>
                ))}
              </div>
              <p className="text-sm text-gray-500 leading-tight">
                Join users making smarter<br />financial decisions
              </p>
            </div>
          </motion.div>

          {/* Dashboard preview */}
          <motion.div
            variants={reveal}
            initial="hidden"
            animate="visible"
            custom={0.22}
            className="relative"
          >
            <div className="relative mx-auto max-w-[420px]">
              {/* Main card */}
              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-5 relative z-10">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-bold text-[#0B0F19]">Financial Overview</span>
                  <span className="text-xs font-semibold text-green-600 bg-green-50 px-2 py-0.5 rounded-full">● Live</span>
                </div>
                <div className="mb-1">
                  <span className="text-[10px] font-bold tracking-widest uppercase text-gray-400">THIS MONTH</span>
                </div>
                <div className="text-3xl font-black tracking-tight text-[#0B0F19] mb-1">₹24,580</div>
                <div className="text-xs font-semibold text-green-600 mb-4">↑ 18.4% from last month</div>
                <svg className="w-full mb-2" viewBox="0 0 280 70" fill="none">
                  <path d="M0 55 C30 48,40 58,60 44 S100 42,118 26 S150 44,175 30 S218 10,242 22 S268 12,280 4" stroke="#2563EB" strokeWidth="2.5" strokeLinecap="round"/>
                  <path d="M0 70V55 C30 48,40 58,60 44 S100 42,118 26 S150 44,175 30 S218 10,242 22 S268 12,280 4 V70Z" fill="url(#cg)" opacity="0.15"/>
                  <defs>
                    <linearGradient id="cg" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#2563EB"/>
                      <stop offset="100%" stopColor="#2563EB" stopOpacity="0"/>
                    </linearGradient>
                  </defs>
                </svg>
                <div className="flex justify-between text-[10px] text-gray-400 font-medium">
                  {['Jan','Feb','Mar','Apr','May'].map(m => <span key={m}>{m}</span>)}
                </div>
                <p className="text-[10px] text-gray-400 italic mt-2">* Illustrative data only</p>
              </div>

              {/* Floating savings card */}
              <motion.div
                className="absolute -left-8 bottom-4 bg-white rounded-xl shadow-card border border-gray-100 p-3 z-20 min-w-[140px] animate-float-1"
              >
                <div className="text-lg mb-1">⌁</div>
                <div className="text-[10px] font-bold tracking-widest uppercase text-gray-400">SAVINGS RATE</div>
                <div className="text-lg font-black text-[#0B0F19]">28%</div>
                <div className="h-1 bg-gray-100 rounded-full mt-2 overflow-hidden">
                  <div className="h-full bg-[#2563EB] rounded-full" style={{ width: '28%' }} />
                </div>
              </motion.div>

              {/* Floating insight card */}
              <motion.div
                className="absolute -right-6 top-8 bg-white rounded-xl shadow-card border border-gray-100 p-3 z-20 min-w-[148px] animate-float-2"
              >
                <div className="text-base mb-0.5">✦</div>
                <div className="text-[10px] font-bold tracking-widest uppercase text-gray-400">INSIGHT</div>
                <div className="text-xs font-bold text-[#0B0F19] mt-0.5">You're on track!</div>
              </motion.div>

              {/* Floating expense card */}
              <motion.div
                className="absolute -right-4 bottom-20 bg-white rounded-xl shadow-card border border-gray-100 p-3 z-20 min-w-[140px] animate-float-3"
              >
                <div className="text-[10px] font-bold tracking-widest uppercase text-gray-400">TOP EXPENSE</div>
                <div className="text-xs font-bold text-[#0B0F19] mt-0.5">Food & Dining</div>
                <div className="text-[10px] text-gray-400">₹3,240 · ↓ 8%</div>
              </motion.div>
            </div>
          </motion.div>
        </div>

        {/* Scroll cue */}
        <div className="flex flex-col items-center gap-2 pt-16 text-gray-400">
          <span className="text-[10px] tracking-[0.12em] uppercase font-medium">Scroll to discover</span>
          <div className="w-px h-12 bg-gradient-to-b from-gray-300 to-transparent animate-scroll" />
        </div>
      </div>
    </section>
  );
}
