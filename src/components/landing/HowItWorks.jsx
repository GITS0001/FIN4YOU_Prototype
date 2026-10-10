import { useState, useRef } from 'react';
import { motion, AnimatePresence, useInView } from 'motion/react';
import { Link } from 'react-router-dom';
import { UserPlus, LayoutDashboard, BookOpen, Target, ChevronLeft, ChevronRight } from 'lucide-react';

const steps = [
  {
    num: '01',
    icon: UserPlus,
    title: 'Create Your Account',
    desc: 'Sign up for Fin4You to begin your personal financial journey. All you need is an email address and a password — no bank integration required.',
    cta: 'Create Account',
    ctaTo: '/signup',
    visual: (
      <div className="bg-white rounded-2xl shadow-card border border-gray-100 p-5 w-full max-w-[240px]">
        <div className="text-3xl text-center mb-4">👤</div>
        <div className="space-y-3">
          <div>
            <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">Email</div>
            <div className="h-8 bg-gray-100 rounded-lg border border-gray-200" />
          </div>
          <div>
            <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">Password</div>
            <div className="h-8 bg-gray-100 rounded-lg border border-gray-200" />
          </div>
          <div className="bg-[#2563EB] text-white text-center py-2 rounded-lg text-xs font-bold mt-2">
            Create Account →
          </div>
        </div>
        <div className="mt-3 inline-flex items-center gap-1.5 bg-green-50 text-green-600 text-[10px] font-bold px-2.5 py-1 rounded-full">
          <span>✓</span> Account Created!
        </div>
      </div>
    ),
  },
  {
    num: '02',
    icon: LayoutDashboard,
    title: 'Explore Your Dashboard',
    desc: "Get familiar with your financial overview and available tools. Your dashboard is your control centre — clear, organised, and always up to date.",
    cta: 'View Dashboard',
    ctaTo: '/signup',
    visual: (
      <div className="bg-white rounded-2xl shadow-card border border-gray-100 p-4 w-full max-w-[240px]">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-bold text-gray-700">Overview</span>
          <span className="text-[10px] text-green-600 font-semibold">● Live</span>
        </div>
        <div className="grid grid-cols-3 gap-2 mb-3">
          {[['Income','₹45K','text-[#2563EB]'],['Spent','₹28K','text-gray-700'],['Saved','₹17K','text-green-600']].map(([l,v,c])=>(
            <div key={l} className="text-center">
              <div className="text-[9px] text-gray-400 uppercase tracking-wide">{l}</div>
              <div className={`text-sm font-black ${c}`}>{v}</div>
            </div>
          ))}
        </div>
        <div className="flex items-end gap-1 h-16">
          {[40,65,35,78,50,88].map((h,i)=>(
            <div key={i} className="flex-1 bg-[#2563EB] rounded-t-sm" style={{height:`${h}%`,opacity:0.5+i*0.1}} />
          ))}
        </div>
      </div>
    ),
  },
  {
    num: '03',
    icon: BookOpen,
    title: 'Understand Your Money',
    desc: 'Review your recorded income, expenses, and spending patterns. Fin4You presents your financial data in simple visual formats that make sense at a glance.',
    cta: 'See Insights',
    ctaTo: '/signup',
    visual: (
      <div className="bg-white rounded-2xl shadow-card border border-gray-100 p-4 w-full max-w-[240px]">
        <div className="text-xs font-bold text-gray-700 mb-3">Spending by Category</div>
        <div className="space-y-2.5">
          {[['Food & Dining',64,'#2563EB','₹3,240'],['Transport',38,'#1D4ED8','₹1,920'],['Shopping',28,'#3B82F6','₹1,400'],['Utilities',18,'#BFDBFE','₹900']].map(([l,w,c,v])=>(
            <div key={l} className="grid grid-cols-[1fr_auto] items-center gap-2">
              <div>
                <div className="text-[10px] text-gray-600 mb-1">{l}</div>
                <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full rounded-full" style={{width:`${w}%`,background:c}} />
                </div>
              </div>
              <div className="text-[10px] font-bold text-gray-700">{v}</div>
            </div>
          ))}
        </div>
      </div>
    ),
  },
  {
    num: '04',
    icon: Target,
    title: 'Plan With More Clarity',
    desc: 'Use available summaries and forecasts to understand trends and make informed decisions. See where you\'ve been and where you\'re heading financially.',
    cta: 'Start Planning',
    ctaTo: '/signup',
    visual: (
      <div className="bg-white rounded-2xl shadow-card border border-gray-100 p-4 w-full max-w-[240px]">
        <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Projected Savings</div>
        <svg className="w-full mb-3" viewBox="0 0 200 80" fill="none">
          <path d="M5 72 C40 64,50 60,80 48 S120 40,148 28 S180 18,195 6" stroke="#2563EB" strokeWidth="2.5" strokeLinecap="round"/>
          <circle cx="195" cy="6" r="4" fill="#2563EB"/>
          <path d="M5 80V72 C40 64,50 60,80 48 S120 40,148 28 S180 18,195 6 V80Z" fill="#2563EB" opacity="0.07"/>
        </svg>
        <div className="text-center">
          <div className="text-[10px] text-gray-400 uppercase tracking-wide">By year end</div>
          <div className="text-2xl font-black text-[#2563EB]">₹1.2L</div>
          <div className="text-[10px] text-gray-400">at current pace</div>
        </div>
      </div>
    ),
  },
];

export default function HowItWorks() {
  const [active, setActive] = useState(0);
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-80px' });

  const go = (i) => setActive(Math.max(0, Math.min(steps.length - 1, i)));

  return (
    <section className="py-24 bg-white" id="how-it-works">
      <div className="max-w-[1160px] mx-auto px-6">
        <motion.div
          ref={ref}
          initial={{ opacity: 0, y: 28 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center max-w-[600px] mx-auto mb-14"
        >
          <span className="inline-flex items-center gap-2 text-xs font-bold tracking-widest uppercase text-[#2563EB] mb-4">
            <span className="w-6 h-0.5 bg-[#2563EB] rounded" />
            How It Works
          </span>
          <h2 className="text-3xl md:text-4xl font-black tracking-tight text-[#0B0F19] leading-tight mb-4">
            Four Simple Steps to<br /><em className="not-italic text-[#2563EB]">Financial Clarity.</em>
          </h2>
          <p className="text-gray-500 text-[1.02rem] leading-relaxed">
            Getting started with Fin4You is straightforward. Here's how your journey unfolds.
          </p>
        </motion.div>

        {/* Desktop stepper track */}
        <div className="hidden md:block mb-10">
          <div className="relative">
            {/* Track line */}
            <div className="absolute top-5 left-[12.5%] right-[12.5%] h-0.5 bg-gray-200 rounded">
              <div
                className="h-full bg-[#2563EB] rounded stepper-progress"
                style={{ width: `${(active / (steps.length - 1)) * 100}%` }}
              />
            </div>
            {/* Nodes */}
            <div className="relative grid grid-cols-4 gap-0">
              {steps.map((s, i) => (
                <button
                  key={i}
                  onClick={() => setActive(i)}
                  className="flex flex-col items-center gap-2 group"
                >
                  <div className={`w-10 h-10 rounded-full border-2 grid place-items-center font-bold text-sm transition-all duration-300 ${
                    i <= active ? 'bg-[#2563EB] border-[#2563EB] text-white shadow-blue' : 'bg-white border-gray-200 text-gray-400 group-hover:border-[#2563EB] group-hover:text-[#2563EB]'
                  }`}>
                    {i < active ? '✓' : i + 1}
                  </div>
                  <span className={`text-xs font-semibold transition-colors ${i === active ? 'text-[#2563EB]' : 'text-gray-400'}`}>
                    {s.title.split(' ').slice(0, 2).join(' ')}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Panel */}
        <AnimatePresence mode="wait">
          <motion.div
            key={active}
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -16 }}
            transition={{ duration: 0.35, ease: [0.4, 0, 0.2, 1] }}
            className="grid grid-cols-1 md:grid-cols-2 gap-10 items-center bg-[#EFF6FF] rounded-3xl p-8 md:p-12"
          >
            <div>
              <div className="text-6xl font-black text-[#BFDBFE] leading-none mb-4">{steps[active].num}</div>
              <h3 className="text-2xl md:text-3xl font-black text-[#0B0F19] tracking-tight mb-4">{steps[active].title}</h3>
              <p className="text-gray-600 leading-relaxed mb-6 text-[0.97rem]">{steps[active].desc}</p>
              <Link
                to={steps[active].ctaTo}
                className="inline-flex items-center gap-2 px-5 py-3 bg-[#2563EB] text-white font-bold rounded-xl text-sm hover:bg-[#1D4ED8] transition-colors shadow-blue"
              >
                {steps[active].cta} →
              </Link>
            </div>
            <div className="flex justify-center">
              {steps[active].visual}
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Controls */}
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-100">
          <button
            onClick={() => go(active - 1)}
            disabled={active === 0}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg border border-gray-200 text-sm font-semibold text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft size={16} /> Previous
          </button>
          <div className="flex gap-2">
            {steps.map((_, i) => (
              <button
                key={i}
                onClick={() => setActive(i)}
                className={`rounded-full transition-all duration-300 ${i === active ? 'w-6 h-2 bg-[#2563EB]' : 'w-2 h-2 bg-gray-200 hover:bg-gray-300'}`}
                aria-label={`Step ${i + 1}`}
              />
            ))}
          </div>
          {active === steps.length - 1 ? (
            <Link
              to="/signup"
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-[#2563EB] text-white text-sm font-semibold hover:bg-[#1D4ED8] transition-colors"
            >
              Get Started →
            </Link>
          ) : (
            <button
              onClick={() => go(active + 1)}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-[#2563EB] text-white text-sm font-semibold hover:bg-[#1D4ED8] transition-colors"
            >
              Next <ChevronRight size={16} />
            </button>
          )}
        </div>
      </div>
    </section>
  );
}
