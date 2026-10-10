import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence, useReducedMotion } from 'motion/react';
import { Link } from 'react-router-dom';
import {
  IndianRupee,
  Wallet,
  TrendingUp,
  TrendingDown,
  HelpCircle,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  ShieldCheck,
  PieChart,
  BarChart3,
  CreditCard,
  ShoppingBag,
  Receipt,
  Target,
  Play,
  Pause,
  AlertCircle,
  Clock,
  ArrowUpRight,
  Zap,
} from 'lucide-react';

// ─── Scene metadata ──────────────────────────────────────────
const SCENES = [
  {
    id: 'confusion',
    stepNumber: '01',
    navTitle: 'Financial Confusion',
    heading: 'Financial Confusion',
    subtitle: 'Money comes in. Expenses add up. But where does it all go?',
    badge: 'Stage 1 • Uncertainty',
  },
  {
    id: 'transform',
    stepNumber: '02',
    navTitle: 'Fin4You Brings Clarity',
    heading: 'Fin4You Brings Clarity',
    subtitle: 'Turn scattered financial information into insights you can understand and use.',
    badge: 'Stage 2 • Transformation',
  },
  {
    id: 'clarity',
    stepNumber: '03',
    navTitle: 'Financial Clarity',
    heading: 'Financial Clarity',
    subtitle: 'Understand your money, make informed choices, and plan your next move with confidence.',
    badge: 'Stage 3 • Confidence & Growth',
  },
];

// ─── Expressive Vector Cartoon Character ─────────────────────
function CartoonCharacter({ expression = 'confused', scale = 1 }) {
  const isHappy = expression === 'clarity' || expression === 'happy';
  const isTransform = expression === 'transform';

  return (
    <div className="relative flex flex-col items-center justify-center select-none" style={{ transform: `scale(${scale})` }}>
      <svg
        width="170"
        height="230"
        viewBox="0 0 170 230"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="drop-shadow-lg"
        aria-hidden="true"
      >
        {/* Soft ground shadow */}
        <ellipse cx="85" cy="222" rx="55" ry="8" fill="#0B0F19" fillOpacity="0.08" />

        {/* Legs / Trousers */}
        <rect x="62" y="156" width="20" height="58" rx="8" fill="#0B0F19" />
        <rect x="88" y="156" width="20" height="58" rx="8" fill="#0B0F19" />

        {/* Shoes */}
        <path d="M56 214 C56 210 64 208 76 208 C84 208 85 213 85 218 C85 222 78 224 64 224 C57 224 56 220 56 214 Z" fill="#1E293B" />
        <path d="M85 218 C85 213 86 208 94 208 C106 208 114 210 114 214 C114 220 113 224 106 224 C92 224 85 222 85 218 Z" fill="#1E293B" />

        {/* Left Arm */}
        {expression === 'confused' && (
          <motion.g
            animate={{ rotate: [-4, 6, -4], originX: '45px', originY: '110px' }}
            transition={{ repeat: Infinity, duration: 2.8, ease: 'easeInOut' }}
          >
            {/* Left arm scratch head */}
            <path d="M52 108 C34 116 26 100 36 80 C40 72 52 70 56 74" stroke="#2563EB" strokeWidth="16" strokeLinecap="round" fill="none" />
            <circle cx="56" cy="74" r="8" fill="#FBBF24" />
          </motion.g>
        )}

        {isTransform && (
          <motion.g
            animate={{ rotate: [0, 4, 0], originX: '48px', originY: '110px' }}
            transition={{ repeat: Infinity, duration: 2.4, ease: 'easeInOut' }}
          >
            <path d="M52 108 C38 120 30 135 34 148" stroke="#2563EB" strokeWidth="15" strokeLinecap="round" fill="none" />
            <circle cx="34" cy="148" r="7.5" fill="#FBBF24" />
          </motion.g>
        )}

        {isHappy && (
          <motion.g
            initial={{ scale: 0.9 }}
            animate={{ rotate: [0, -3, 0], originX: '48px', originY: '110px' }}
            transition={{ repeat: Infinity, duration: 3, ease: 'easeInOut' }}
          >
            {/* Hand on hip */}
            <path d="M52 108 C36 116 32 134 44 144" stroke="#2563EB" strokeWidth="15" strokeLinecap="round" fill="none" />
            <circle cx="44" cy="144" r="7.5" fill="#FBBF24" />
          </motion.g>
        )}

        {/* Right Arm */}
        {expression === 'confused' && (
          <motion.g
            animate={{ rotate: [5, -5, 5], originX: '120px', originY: '110px' }}
            transition={{ repeat: Infinity, duration: 2.5, ease: 'easeInOut', delay: 0.2 }}
          >
            {/* Questioning raised palm */}
            <path d="M118 108 C136 118 144 104 140 88" stroke="#2563EB" strokeWidth="16" strokeLinecap="round" fill="none" />
            <circle cx="140" cy="88" r="8" fill="#FBBF24" />
          </motion.g>
        )}

        {isTransform && (
          <motion.g
            animate={{ x: [0, 4, 0] }}
            transition={{ repeat: Infinity, duration: 1.8, ease: 'easeInOut' }}
          >
            {/* Arm pointing forward at dashboard */}
            <path d="M118 108 C136 104 150 96 162 86" stroke="#2563EB" strokeWidth="15" strokeLinecap="round" fill="none" />
            <circle cx="162" cy="86" r="7.5" fill="#FBBF24" />
          </motion.g>
        )}

        {isHappy && (
          <motion.g
            animate={{ y: [0, -3, 0] }}
            transition={{ repeat: Infinity, duration: 2.5, ease: 'easeInOut' }}
          >
            {/* Thumbs up arm */}
            <path d="M118 108 C136 102 144 86 142 68" stroke="#2563EB" strokeWidth="15" strokeLinecap="round" fill="none" />
            <circle cx="142" cy="68" r="7.5" fill="#FBBF24" />
            {/* Thumbs up hand vector */}
            <path d="M142 62 L142 54" stroke="#FBBF24" strokeWidth="5" strokeLinecap="round" />
          </motion.g>
        )}

        {/* Main Body Jacket (Tailored Fintech Blue Suit) */}
        <rect x="52" y="100" width="66" height="64" rx="14" fill="#2563EB" />
        {/* Subtle shadow gradient on jacket */}
        <path d="M52 136 C68 152 102 152 118 136 L118 150 C118 158 112 164 104 164 L66 164 C58 164 52 158 52 150 Z" fill="#1D4ED8" />

        {/* White Shirt & Tie */}
        <polygon points="85,100 76,128 94,128" fill="#FFFFFF" />
        <polygon points="85,110 82,142 85,148 88,142" fill="#0B0F19" />
        {/* Lapel V cut */}
        <path d="M72 100 L85 128 L98 100" stroke="#1D4ED8" strokeWidth="3" fill="none" />

        {/* Fin4You subtle lapel badge */}
        <circle cx="64" cy="116" r="4.5" fill="#60A5FA" />
        <circle cx="64" cy="116" r="2" fill="#FFFFFF" />

        {/* Neck */}
        <rect x="75" y="86" width="20" height="18" rx="4" fill="#FBBF24" />

        {/* Head */}
        <ellipse cx="85" cy="62" rx="33" ry="34" fill="#FBBF24" />

        {/* Modern styled hair */}
        <path
          d="M52 58 C52 38 65 24 85 24 C105 24 118 38 118 58 C118 61 115 62 112 56 C105 44 95 38 85 38 C75 38 65 44 58 56 C55 62 52 61 52 58 Z"
          fill="#0B0F19"
        />
        <path d="M60 36 C72 26 96 26 112 36 C104 32 82 30 68 36" fill="#1E293B" />

        {/* Ears */}
        <circle cx="52" cy="64" r="6" fill="#F59E0B" />
        <circle cx="118" cy="64" r="6" fill="#F59E0B" />

        {/* Cheeks blush */}
        <circle cx="66" cy="72" r="5" fill="#F43F5E" fillOpacity={isHappy ? 0.35 : 0.15} />
        <circle cx="104" cy="72" r="5" fill="#F43F5E" fillOpacity={isHappy ? 0.35 : 0.15} />

        {/* Eyes & Eyebrows based on state */}
        {expression === 'confused' && (
          <>
            {/* Confused asymmetric eyebrows */}
            <path d="M63 48 Q71 42 79 50" stroke="#0B0F19" strokeWidth="3.5" strokeLinecap="round" fill="none" />
            <path d="M91 52 Q99 44 107 46" stroke="#0B0F19" strokeWidth="3.5" strokeLinecap="round" fill="none" />

            {/* Puzzled swirly/blinking eyes */}
            <motion.ellipse
              cx="71"
              cy="58"
              rx="5"
              ry="5"
              fill="#0B0F19"
              animate={{ scaleY: [1, 0.2, 1], y: [0, -1, 0] }}
              transition={{ repeat: Infinity, duration: 2.8 }}
            />
            <motion.ellipse
              cx="99"
              cy="58"
              rx="5"
              ry="5"
              fill="#0B0F19"
              animate={{ scaleY: [1, 0.2, 1], y: [0, 1, 0] }}
              transition={{ repeat: Infinity, duration: 2.8, delay: 0.1 }}
            />
            {/* Eye white highlights */}
            <circle cx="69.5" cy="56.5" r="1.5" fill="#FFFFFF" />
            <circle cx="97.5" cy="56.5" r="1.5" fill="#FFFFFF" />

            {/* Confused wavy mouth */}
            <path d="M72 79 Q80 74 88 80 Q94 83 98 78" stroke="#0B0F19" strokeWidth="3" strokeLinecap="round" fill="none" />
          </>
        )}

        {isTransform && (
          <>
            {/* Curious raised brows */}
            <path d="M63 46 Q71 40 79 45" stroke="#0B0F19" strokeWidth="3.5" strokeLinecap="round" fill="none" />
            <path d="M91 45 Q99 40 107 46" stroke="#0B0F19" strokeWidth="3.5" strokeLinecap="round" fill="none" />

            {/* Wide curious eyes looking rightward */}
            <ellipse cx="73" cy="57" rx="5.5" ry="5.5" fill="#0B0F19" />
            <ellipse cx="101" cy="57" rx="5.5" ry="5.5" fill="#0B0F19" />
            <circle cx="75" cy="55.5" r="2" fill="#FFFFFF" />
            <circle cx="103" cy="55.5" r="2" fill="#FFFFFF" />

            {/* Impressed O mouth */}
            <ellipse cx="85" cy="78" rx="6" ry="7" fill="#0B0F19" />
            <ellipse cx="85" cy="79" rx="4" ry="4" fill="#F43F5E" />
          </>
        )}

        {isHappy && (
          <>
            {/* Confident arched brows */}
            <path d="M63 46 Q71 40 79 46" stroke="#0B0F19" strokeWidth="3.5" strokeLinecap="round" fill="none" />
            <path d="M91 46 Q99 40 107 46" stroke="#0B0F19" strokeWidth="3.5" strokeLinecap="round" fill="none" />

            {/* Happy smiling eyes (curved arcs) */}
            <path d="M65 58 Q72 51 79 58" stroke="#0B0F19" strokeWidth="3.5" strokeLinecap="round" fill="none" />
            <path d="M91 58 Q98 51 105 58" stroke="#0B0F19" strokeWidth="3.5" strokeLinecap="round" fill="none" />

            {/* Big confident open smile */}
            <path d="M69 74 Q85 91 101 74" fill="#0B0F19" />
            <path d="M72 75 Q85 86 98 75" fill="#FFFFFF" />
            <path d="M78 84 Q85 89 92 84" fill="#F43F5E" />
          </>
        )}
      </svg>
    </div>
  );
}

// ─── Scene 1: Financial Confusion ────────────────────────────
function SceneConfusion() {
  return (
    <div className="w-full relative min-h-[460px] md:min-h-[480px] flex flex-col lg:flex-row items-center justify-between gap-8 md:gap-12 px-2 md:px-6">
      {/* Left Column: Character with Thought Clouds & Disarray Orbitals */}
      <div className="relative flex-1 flex flex-col items-center justify-center min-w-[280px]">
        {/* Radial faint glow */}
        <div className="absolute w-72 h-72 rounded-full bg-blue-100/50 blur-3xl -z-10" />

        {/* Floating Question & Confusion Orbitals */}
        <motion.div
          className="absolute -top-6 -left-4 md:-left-8 bg-white/95 border border-red-200/80 rounded-2xl shadow-card px-3.5 py-2 flex items-center gap-2 z-20"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: [0, -8, 0] }}
          transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
        >
          <div className="w-7 h-7 rounded-xl bg-red-50 flex items-center justify-center text-red-600 font-bold text-xs">
            <HelpCircle className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[11px] font-bold text-gray-800">Where did it go?</div>
            <div className="text-[10px] text-red-500 font-semibold">₹34,800 Unaccounted</div>
          </div>
        </motion.div>

        <motion.div
          className="absolute -top-10 right-0 md:-right-6 bg-white/95 border border-blue-200/80 rounded-2xl shadow-card px-3 py-1.5 flex items-center gap-2 z-20"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1, y: [0, 6, 0] }}
          transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut', delay: 0.4 }}
        >
          <span className="text-blue-600 font-black text-sm">₹???</span>
          <span className="text-[11px] font-medium text-gray-600">Savings: ₹0</span>
        </motion.div>

        <motion.div
          className="absolute bottom-8 -left-6 md:-left-12 bg-white/90 border border-gray-200 rounded-xl shadow-card px-3 py-1.5 flex items-center gap-2 z-20"
          animate={{ x: [0, 6, 0], y: [0, -4, 0] }}
          transition={{ duration: 4.2, repeat: Infinity, ease: 'easeInOut', delay: 0.8 }}
        >
          <ShoppingBag className="w-3.5 h-3.5 text-gray-500" />
          <span className="text-[11px] text-gray-600 font-medium">Daily Outflows: -₹2,850</span>
        </motion.div>

        {/* Scattered Rupee coins floating */}
        <motion.div
          className="absolute top-28 -right-8 w-9 h-9 rounded-full bg-amber-50 border border-amber-200 flex items-center justify-center shadow-sm text-amber-700 font-black text-xs"
          animate={{ y: [0, -10, 0], rotate: [0, 15, 0] }}
          transition={{ duration: 3.2, repeat: Infinity, ease: 'easeInOut' }}
        >
          ₹500
        </motion.div>

        <motion.div
          className="absolute bottom-2 right-4 w-8 h-8 rounded-full bg-amber-50 border border-amber-200 flex items-center justify-center shadow-sm text-amber-700 font-black text-[10px]"
          animate={{ y: [0, 8, 0], rotate: [0, -12, 0] }}
          transition={{ duration: 3.8, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
        >
          ₹1k
        </motion.div>

        {/* Character */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="z-10 py-4"
        >
          <CartoonCharacter expression="confused" scale={1.12} />
        </motion.div>
      </div>

      {/* Right Column: Chaotic Financial Disarray Representation */}
      <div className="flex-1 w-full max-w-lg flex flex-col gap-3.5 z-10">
        {/* Status Chip */}
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-200/60">
            <AlertCircle className="w-3.5 h-3.5 text-red-600" />
            Unorganized Financial State
          </span>
          <span className="text-xs text-gray-400 font-medium">* Illustrative scenario</span>
        </div>

        {/* Chaotic Card 1: Jagged Volatility Expense Chart */}
        <div className="bg-white rounded-2xl p-4 md:p-5 border border-red-100 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between mb-2">
            <div>
              <div className="text-xs font-bold text-gray-700">Monthly Cash Drain</div>
              <div className="text-[11px] text-gray-400">Irregular transactions, zero category tracking</div>
            </div>
            <span className="text-xs font-bold text-red-600 bg-red-50 px-2 py-0.5 rounded-md">-₹48,200</span>
          </div>

          {/* Jagged unpredictable red SVG graph */}
          <div className="h-16 w-full relative mt-3 flex items-center">
            <svg className="w-full h-full overflow-visible" viewBox="0 0 300 60" preserveAspectRatio="none">
              <path
                d="M0 30 L40 10 L80 48 L120 18 L160 52 L200 8 L240 45 L280 20 L300 55"
                fill="none"
                stroke="#DC2626"
                strokeWidth="2.5"
                strokeDasharray="4 2"
              />
              <circle cx="80" cy="48" r="4" fill="#DC2626" />
              <circle cx="160" cy="52" r="4" fill="#DC2626" />
              <circle cx="240" cy="45" r="4" fill="#DC2626" />
            </svg>
          </div>
          <div className="flex justify-between text-[10px] text-gray-400 font-medium mt-1">
            <span>Week 1</span>
            <span>Week 2 (Spike?)</span>
            <span>Week 3</span>
            <span>Week 4 (Overbudget)</span>
          </div>
        </div>

        {/* Scattered Micro Cards Grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white rounded-2xl p-3.5 border border-gray-200/80 shadow-xs flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gray-100 flex items-center justify-center text-gray-600 flex-shrink-0">
              <CreditCard className="w-4 h-4 text-red-500" />
            </div>
            <div className="min-w-0">
              <div className="text-[11px] text-gray-500 truncate">Credit Card EMI</div>
              <div className="text-xs font-bold text-gray-800">₹14,500 due?</div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-3.5 border border-gray-200/80 shadow-xs flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gray-100 flex items-center justify-center text-gray-600 flex-shrink-0">
              <Receipt className="w-4 h-4 text-amber-500" />
            </div>
            <div className="min-w-0">
              <div className="text-[11px] text-gray-500 truncate">Bills & Subs</div>
              <div className="text-xs font-bold text-gray-800">₹6,800 scattered</div>
            </div>
          </div>
        </div>

        {/* Confusion Quote Banner */}
        <div className="bg-red-50/70 border border-red-200/50 rounded-2xl p-3 flex items-start gap-2.5">
          <HelpCircle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
          <p className="text-xs text-red-900 leading-relaxed font-medium">
            "I earn a decent salary, but by month-end I have no idea how much went into rent, food, or mindless shopping."
          </p>
        </div>
      </div>
    </div>
  );
}

// ─── Scene 2: Fin4You Brings Clarity (The Transformation) ─────
function SceneTransform() {
  return (
    <div className="w-full relative min-h-[460px] md:min-h-[480px] flex flex-col lg:flex-row items-center justify-between gap-8 md:gap-12 px-2 md:px-6">
      {/* Left Column: Intrigued Character pointing to the organizing system */}
      <div className="relative flex-1 flex flex-col items-center justify-center min-w-[280px]">
        {/* Soft Blue Radial Pulse */}
        <motion.div
          className="absolute w-80 h-80 rounded-full bg-blue-200/40 blur-3xl -z-10"
          animate={{ scale: [0.9, 1.1, 0.9] }}
          transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
        />

        {/* Transformation connecting lines */}
        <motion.div
          className="hidden md:flex absolute top-16 right-[-20px] z-20 items-center gap-2 bg-[#2563EB] text-white px-3.5 py-1.5 rounded-full shadow-blue text-xs font-bold"
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Structuring Data...</span>
        </motion.div>

        {/* Character */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="z-10 py-4"
        >
          <CartoonCharacter expression="transform" scale={1.12} />
        </motion.div>
      </div>

      {/* Right Column: Emerging Structured Fin4You Dashboard */}
      <div className="flex-1 w-full max-w-lg z-10">
        <motion.div
          className="bg-white rounded-3xl p-5 md:p-6 border border-blue-200/90 shadow-xl shadow-blue-900/5 relative overflow-hidden"
          initial={{ opacity: 0, y: 20, scale: 0.96 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.55, ease: [0.4, 0, 0.2, 1] }}
        >
          {/* Header of Preview Dashboard */}
          <div className="flex items-center justify-between pb-3.5 border-b border-gray-100">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-[#2563EB] flex items-center justify-center text-white font-black text-xs">
                F
              </div>
              <div>
                <div className="text-xs font-bold text-gray-900">Fin4You Smart Sync</div>
                <div className="text-[10px] text-gray-400">Automated ledger grouping</div>
              </div>
            </div>
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-50 border border-blue-200/60 text-[11px] text-blue-700 font-semibold">
              <span className="w-2 h-2 rounded-full bg-[#2563EB] animate-pulse" />
              Live Organizing
            </div>
          </div>

          {/* 3 Grouped Metric Cards */}
          <div className="grid grid-cols-3 gap-2.5 my-4">
            <motion.div
              className="bg-blue-50/70 border border-blue-100 rounded-2xl p-2.5 text-center"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
            >
              <div className="text-[10px] text-gray-500 font-medium">Income</div>
              <div className="text-xs md:text-sm font-black text-[#2563EB] mt-0.5">₹75,000</div>
              <span className="text-[9px] text-green-600 font-bold">Salary</span>
            </motion.div>

            <motion.div
              className="bg-gray-50 border border-gray-100 rounded-2xl p-2.5 text-center"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 }}
            >
              <div className="text-[10px] text-gray-500 font-medium">Expenses</div>
              <div className="text-xs md:text-sm font-black text-gray-800 mt-0.5">₹42,200</div>
              <span className="text-[9px] text-gray-400 font-medium">Categorized</span>
            </motion.div>

            <motion.div
              className="bg-green-50/80 border border-green-200/70 rounded-2xl p-2.5 text-center"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35 }}
            >
              <div className="text-[10px] text-green-700 font-medium">Saved</div>
              <div className="text-xs md:text-sm font-black text-green-700 mt-0.5">₹32,800</div>
              <span className="text-[9px] text-green-700 font-bold">43.7% Rate</span>
            </motion.div>
          </div>

          {/* Clean Categorization Progress Bar */}
          <div className="bg-gray-50/80 rounded-2xl p-3 border border-gray-100 mb-3.5">
            <div className="flex justify-between items-center text-[11px] mb-1.5 font-semibold">
              <span className="text-gray-700">Expense Allocation</span>
              <span className="text-[#2563EB]">100% Sorted</span>
            </div>
            <div className="h-2.5 w-full bg-gray-200 rounded-full flex overflow-hidden">
              <motion.div
                className="h-full bg-[#2563EB]"
                initial={{ width: 0 }}
                animate={{ width: '45%' }}
                transition={{ duration: 0.8, delay: 0.2 }}
                title="Essentials 45%"
              />
              <motion.div
                className="h-full bg-blue-400"
                initial={{ width: 0 }}
                animate={{ width: '25%' }}
                transition={{ duration: 0.8, delay: 0.4 }}
                title="Housing 25%"
              />
              <motion.div
                className="h-full bg-blue-300"
                initial={{ width: 0 }}
                animate={{ width: '15%' }}
                transition={{ duration: 0.8, delay: 0.6 }}
                title="Leisure 15%"
              />
              <motion.div
                className="h-full bg-green-500"
                initial={{ width: 0 }}
                animate={{ width: '15%' }}
                transition={{ duration: 0.8, delay: 0.7 }}
                title="Savings 15%"
              />
            </div>
            <div className="flex justify-between text-[10px] text-gray-500 mt-2">
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-[#2563EB]" /> Essentials (₹18.9k)
              </span>
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-400" /> Housing (₹10.5k)
              </span>
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500" /> Savings (₹32.8k)
              </span>
            </div>
          </div>

          {/* Fin4You Smart Insight Pill */}
          <div className="bg-[#EFF6FF] border border-blue-200/80 rounded-2xl p-3 flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-xl bg-[#2563EB] flex items-center justify-center text-white flex-shrink-0">
              <Sparkles className="w-3.5 h-3.5" />
            </div>
            <div>
              <div className="text-[11px] font-bold text-[#2563EB]">Smart Financial Insight</div>
              <p className="text-[11px] text-gray-700 leading-tight">
                Discretionary shopping reduced by 14%. You are on track to save ₹32,800 this month!
              </p>
            </div>
          </div>

          <div className="text-right mt-2 text-[9px] text-gray-400 font-medium">* Illustrative data for demonstration</div>
        </motion.div>
      </div>
    </div>
  );
}

// ─── Scene 3: Financial Clarity ──────────────────────────────
function SceneClarity() {
  return (
    <div className="w-full relative min-h-[460px] md:min-h-[480px] flex flex-col lg:flex-row items-center justify-between gap-8 md:gap-12 px-2 md:px-6">
      {/* Left Column: Happy Confident Character with Verified Badge */}
      <div className="relative flex-1 flex flex-col items-center justify-center min-w-[280px]">
        {/* Soft Golden/Blue Celebration Aura */}
        <div className="absolute w-80 h-80 rounded-full bg-blue-100/60 blur-3xl -z-10" />

        {/* Floating Confidence Badges */}
        <motion.div
          className="absolute -top-4 -left-4 md:-left-8 bg-white/95 border border-green-200 rounded-2xl shadow-card px-3.5 py-2 flex items-center gap-2.5 z-20"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1, y: [0, -6, 0] }}
          transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut' }}
        >
          <div className="w-7 h-7 rounded-xl bg-green-50 flex items-center justify-center text-green-600 font-bold">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[11px] font-bold text-gray-900">Health Score: 94/100</div>
            <div className="text-[10px] text-green-600 font-semibold">Tier: Excellent</div>
          </div>
        </motion.div>

        <motion.div
          className="absolute -top-6 right-0 md:-right-6 bg-white/95 border border-blue-200 rounded-2xl shadow-card px-3 py-1.5 flex items-center gap-2 z-20"
          animate={{ y: [0, 6, 0] }}
          transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut', delay: 0.3 }}
        >
          <span className="w-2 h-2 rounded-full bg-green-500" />
          <span className="text-[11px] font-bold text-gray-800">+18.4% YoY Savings</span>
        </motion.div>

        {/* Character */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="z-10 py-4"
        >
          <CartoonCharacter expression="clarity" scale={1.12} />
        </motion.div>

        {/* Big Check Badge on Character */}
        <motion.div
          className="absolute bottom-6 right-12 w-10 h-10 bg-green-600 text-white rounded-full flex items-center justify-center font-bold shadow-lg shadow-green-600/30 border-2 border-white z-20"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 350, delay: 0.3 }}
        >
          <CheckCircle2 className="w-6 h-6" />
        </motion.div>
      </div>

      {/* Right Column: Full Organised Financial Clarity Command Center */}
      <div className="flex-1 w-full max-w-lg z-10">
        <motion.div
          className="bg-white rounded-3xl p-5 md:p-6 border border-blue-100 shadow-xl shadow-blue-900/5 relative"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55 }}
        >
          <div className="flex items-center justify-between pb-3 border-b border-gray-100">
            <div>
              <div className="text-xs font-bold text-gray-900 flex items-center gap-1.5">
                Financial Clarity Center
                <span className="px-2 py-0.5 rounded-full bg-green-50 text-green-700 text-[10px] font-bold border border-green-200">
                  Optimal
                </span>
              </div>
              <div className="text-[10px] text-gray-400">All streams synced & projected</div>
            </div>
            <div className="text-right">
              <div className="text-xs font-black text-[#2563EB]">₹1,85,000</div>
              <div className="text-[9px] text-gray-400 font-medium">Emergency Reserve</div>
            </div>
          </div>

          {/* Smooth Rising Growth Area Chart */}
          <div className="my-3.5 bg-[#F8FAFC] border border-gray-100 rounded-2xl p-3">
            <div className="flex justify-between items-center text-[10px] text-gray-500 mb-2">
              <span className="font-semibold text-gray-700">6-Month Wealth Trajectory</span>
              <span className="text-green-600 font-bold flex items-center gap-0.5">
                <TrendingUp className="w-3 h-3" /> Upward Growth
              </span>
            </div>

            <div className="h-20 w-full relative">
              <svg className="w-full h-full overflow-visible" viewBox="0 0 320 80" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="clarityAreaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#2563EB" stopOpacity="0.28" />
                    <stop offset="100%" stopColor="#2563EB" stopOpacity="0.0" />
                  </linearGradient>
                </defs>
                {/* Area fill */}
                <path
                  d="M0 65 Q50 60 100 48 T200 32 T320 10 L320 80 L0 80 Z"
                  fill="url(#clarityAreaGrad)"
                />
                {/* Main line curve */}
                <path
                  d="M0 65 Q50 60 100 48 T200 32 T320 10"
                  fill="none"
                  stroke="#2563EB"
                  strokeWidth="3"
                  strokeLinecap="round"
                />
                {/* Dots along line */}
                <circle cx="100" cy="48" r="3.5" fill="#2563EB" />
                <circle cx="200" cy="32" r="3.5" fill="#2563EB" />
                <circle cx="320" cy="10" r="4.5" fill="#1D4ED8" stroke="#FFFFFF" strokeWidth="2" />
              </svg>
            </div>

            <div className="flex justify-between text-[10px] text-gray-400 mt-1 font-medium">
              <span>May</span>
              <span>Jun</span>
              <span>Jul</span>
              <span>Aug</span>
              <span>Sep</span>
              <span className="text-[#2563EB] font-bold">Oct (Now)</span>
            </div>
          </div>

          {/* Goal Milestones & Automated Tracking */}
          <div className="space-y-2">
            <div className="flex items-center justify-between p-2.5 rounded-xl bg-blue-50/50 border border-blue-100/80">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-lg bg-[#2563EB] text-white flex items-center justify-center">
                  <Target className="w-3.5 h-3.5" />
                </div>
                <div>
                  <div className="text-[11px] font-bold text-gray-800">Emergency Fund Target</div>
                  <div className="text-[10px] text-gray-500">₹1,85,000 of ₹2,00,000</div>
                </div>
              </div>
              <span className="text-xs font-black text-green-700 bg-green-50 px-2 py-0.5 rounded-md border border-green-200/60">
                92% Done
              </span>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded-xl bg-gray-50 border border-gray-100">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-lg bg-gray-800 text-white flex items-center justify-center">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                </div>
                <div>
                  <div className="text-[11px] font-bold text-gray-800">Fixed Bills & SIP Payments</div>
                  <div className="text-[10px] text-gray-500">Auto-budgeted with zero stress</div>
                </div>
              </div>
              <span className="text-xs font-semibold text-gray-600">All Cleared ✓</span>
            </div>
          </div>

          <div className="text-right mt-2.5 text-[9px] text-gray-400 font-medium">* Illustrative visualization only</div>
        </motion.div>
      </div>
    </div>
  );
}

// ─── Main Redesigned Financial Story Section ───────────────────
export default function CartoonAnimation() {
  const [sceneIndex, setSceneIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const prefersReduced = useReducedMotion();
  const timerRef = useRef(null);

  // ~4.5 seconds per scene, ~14 seconds complete continuous story
  const SCENE_DURATION_MS = 4500;

  useEffect(() => {
    if (!isPlaying || prefersReduced) return;

    timerRef.current = setInterval(() => {
      setSceneIndex((current) => (current + 1) % SCENES.length);
    }, SCENE_DURATION_MS);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, prefersReduced]);

  const selectScene = (index) => {
    if (timerRef.current) clearInterval(timerRef.current);
    setSceneIndex(index);
    setIsPlaying(false); // Let user manually inspect
  };

  const togglePlay = () => {
    setIsPlaying((p) => !p);
  };

  const currentScene = SCENES[sceneIndex];

  return (
    <section
      className="relative py-20 md:py-28 overflow-hidden bg-gradient-to-b from-[#F0F6FF] via-[#F8FAFC] to-[#FFFFFF]"
      id="animation"
      aria-label="Financial Story Animation"
    >
      {/* Background Fintech Grid & Decorative Glows */}
      <div className="absolute inset-0 pointer-events-none -z-10">
        {/* Subtle dot grid */}
        <svg className="absolute inset-0 w-full h-full opacity-35" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="fin4you-dot-grid" width="32" height="32" patternUnits="userSpaceOnUse">
              <circle cx="2" cy="2" r="1.2" fill="#93C5FD" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#fin4you-dot-grid)" />
        </svg>

        {/* Ambient radial color washes */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[700px] h-[400px] bg-gradient-to-r from-blue-300/20 via-blue-200/25 to-blue-300/20 rounded-full blur-3xl" />
        <div className="absolute bottom-10 left-10 w-96 h-96 bg-blue-100/40 rounded-full blur-3xl" />
        <div className="absolute top-10 right-10 w-96 h-96 bg-blue-100/40 rounded-full blur-3xl" />
      </div>

      <div className="max-w-[1340px] mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-10 md:mb-14">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-100/70 border border-blue-200 text-[#2563EB] text-xs font-bold tracking-wider uppercase mb-4 shadow-xs">
            <Sparkles className="w-3.5 h-3.5 text-[#2563EB]" />
            FINANCIAL STORY EXPERIENCE
          </div>

          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-[#0B0F19] leading-[1.15]">
            From Financial Confusion <br className="hidden sm:inline" />
            <span className="text-gradient">to Financial Clarity.</span>
          </h2>

          <p className="mt-4 text-base sm:text-lg text-gray-600 leading-relaxed max-w-2xl mx-auto">
            See how Fin4You takes disorganized expenses, scattered bills, and guesswork—and turns them into structured insights you can understand and act upon.
          </p>
        </div>

        {/* Main Extended Animation Stage Container (Wide 1200-1400px composition) */}
        <div className="relative rounded-[28px] md:rounded-[36px] border border-blue-200/80 bg-white/95 backdrop-blur-xl shadow-2xl shadow-blue-900/5 overflow-hidden">
          {/* Subtle Top Stage Accent Light */}
          <div className="h-1.5 w-full bg-gradient-to-r from-transparent via-[#2563EB] to-transparent opacity-80" />

          {/* Dynamic Scene Stage Body */}
          <div className="p-6 sm:p-10 lg:p-12 relative flex flex-col items-center">
            {/* Synchronized Stage Narration Title */}
            <div className="text-center mb-6 z-20">
              <span className="inline-block text-xs font-bold tracking-widest uppercase text-[#2563EB] bg-blue-50 px-3 py-1 rounded-full mb-2 border border-blue-100">
                {currentScene.badge}
              </span>
              <h3 className="text-2xl sm:text-3xl font-black text-[#0B0F19] tracking-tight">
                {currentScene.heading}
              </h3>
              <p className="text-sm sm:text-base text-gray-500 mt-1.5 max-w-xl mx-auto leading-relaxed">
                {currentScene.subtitle}
              </p>
            </div>

            {/* Visual Scene Stage Display with AnimatePresence */}
            <div className="w-full relative flex items-center justify-center">
              <AnimatePresence mode="wait">
                <motion.div
                  key={currentScene.id}
                  className="w-full"
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -16 }}
                  transition={{ duration: 0.45, ease: [0.4, 0, 0.2, 1] }}
                >
                  {sceneIndex === 0 && <SceneConfusion />}
                  {sceneIndex === 1 && <SceneTransform />}
                  {sceneIndex === 2 && <SceneClarity />}
                </motion.div>
              </AnimatePresence>
            </div>

            {/* Seamless Bottom Progress Bar */}
            <div className="w-full max-w-2xl mt-8 pt-6 border-t border-gray-100 flex flex-col items-center gap-4">
              {/* 3 Continuous Segment Bars */}
              <div className="w-full flex items-center gap-2">
                {SCENES.map((s, idx) => {
                  const isCurrent = sceneIndex === idx;
                  const isPast = sceneIndex > idx;
                  return (
                    <div
                      key={s.id}
                      onClick={() => selectScene(idx)}
                      className="flex-1 h-2 rounded-full bg-gray-100 overflow-hidden cursor-pointer relative transition-all"
                      title={`Go to ${s.navTitle}`}
                    >
                      {isCurrent ? (
                        <motion.div
                          key={`progress-${idx}-${isPlaying}`}
                          className="h-full bg-[#2563EB] rounded-full"
                          initial={{ width: '0%' }}
                          animate={{ width: '100%' }}
                          transition={
                            isPlaying && !prefersReduced
                              ? { duration: SCENE_DURATION_MS / 1000, ease: 'linear' }
                              : { duration: 0 }
                          }
                        />
                      ) : (
                        <div
                          className={`h-full rounded-full transition-all duration-300 ${
                            isPast ? 'w-full bg-blue-300' : 'w-0'
                          }`}
                        />
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Refined Navigation Controls & Step Indicators (No huge top tab bar!) */}
              <div className="w-full flex flex-wrap items-center justify-between gap-3 text-xs text-gray-500">
                <div className="flex items-center gap-2">
                  <button
                    onClick={togglePlay}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-200 hover:border-blue-300 bg-white text-gray-700 font-medium hover:text-[#2563EB] transition-colors shadow-xs"
                    aria-label={isPlaying ? 'Pause animation' : 'Play animation'}
                  >
                    {isPlaying ? <Pause className="w-3.5 h-3.5 text-[#2563EB]" /> : <Play className="w-3.5 h-3.5 text-[#2563EB]" />}
                    <span>{isPlaying ? 'Pause Story' : 'Auto Play'}</span>
                  </button>
                  <span className="text-[11px] text-gray-400 hidden sm:inline">• Click steps to explore</span>
                </div>

                {/* Subtle Step Selector Pills */}
                <div className="flex items-center gap-1.5 sm:gap-2">
                  {SCENES.map((s, idx) => (
                    <button
                      key={s.id}
                      onClick={() => selectScene(idx)}
                      className={`px-3 py-1.5 rounded-xl font-bold text-[11px] sm:text-xs transition-all ${
                        sceneIndex === idx
                          ? 'bg-[#2563EB] text-white shadow-xs'
                          : 'bg-gray-50 hover:bg-gray-100 text-gray-600 hover:text-gray-900 border border-gray-200/60'
                      }`}
                    >
                      <span className="opacity-70 mr-1">{s.stepNumber}</span>
                      {s.navTitle}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Integrated Final Call-to-Action Panel (From Confusion to Clarity) */}
        <div className="mt-12 text-center max-w-2xl mx-auto flex flex-col items-center">
          <div className="flex items-center gap-2 text-xs font-bold text-[#2563EB] uppercase tracking-wider mb-2">
            <Sparkles className="w-4 h-4" />
            Your Financial Journey Starts Here
          </div>

          <h3 className="text-2xl sm:text-3xl font-black text-[#0B0F19] tracking-tight">
            Ready to replace confusion with absolute clarity?
          </h3>

          <p className="text-gray-600 text-sm sm:text-base mt-2 mb-6 leading-relaxed">
            Join thousands of smart individuals taking control of their money with Fin4You's intelligent insights.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 w-full sm:w-auto">
            <Link
              to="/signup"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-4 bg-[#2563EB] text-white font-bold rounded-2xl shadow-blue hover:bg-[#1D4ED8] transition-all hover:-translate-y-0.5 text-base"
            >
              Get Started with Fin4You
              <ArrowRight className="w-4 h-4" />
            </Link>

            <a
              href="#features"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-4 bg-white text-gray-700 font-bold rounded-2xl border border-gray-200 hover:border-blue-300 hover:text-[#2563EB] transition-all text-base"
            >
              Explore All Features
            </a>
          </div>

          <p className="text-[11px] text-gray-400 mt-4">
            Instant setup • No credit card required • Free personal tier
          </p>
        </div>
      </div>
    </section>
  );
}
