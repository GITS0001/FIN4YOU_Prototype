import { useRef } from 'react';
import { motion, useInView } from 'motion/react';
import { LayoutDashboard, ArrowRightLeft, PieChart, FileText, TrendingUp, BarChart3, Bot, ShieldCheck } from 'lucide-react';

const features = [
  { icon: LayoutDashboard, title: 'Financial Dashboard', desc: 'View your complete financial overview in one place — income, expenses, savings, and summaries at a glance.', delay: 0 },
  { icon: ArrowRightLeft, title: 'Transaction Tracking', desc: 'Understand your recorded income and expenses clearly. See exactly what came in and what went out with automated category tags.', delay: 0.08 },
  { icon: PieChart, title: 'Spending Insights', desc: 'Explore where your money is going with clear category breakdowns, leak audits, and visual spending patterns.', delay: 0.16 },
  { icon: FileText, title: 'Financial Summaries', desc: 'Review your financial activity over any period with clear, concise summaries that are easy to understand.', delay: 0.24 },
  { icon: TrendingUp, title: '90-Day Cash-Flow Forecasting', desc: 'Explore potential future financial trends and liquidity trajectories based on deterministic arithmetic.', delay: 0.32 },
  { icon: Bot, title: 'Artha AI Assistant', desc: 'Ask natural-language questions about your budget, emergency funds, and affordability with an educational co-pilot.', delay: 0.40 },
];

function FeatureCard({ icon: Icon, title, desc, delay }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-40px' });
  return (
    <motion.article
      ref={ref}
      initial={{ opacity: 0, y: 24 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ delay, duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
      className="group bg-white rounded-2xl p-5 sm:p-7 border border-gray-100 shadow-card hover:-translate-y-1 hover:shadow-card-hover hover:border-[#BFDBFE] transition-all duration-300 flex flex-col justify-between"
    >
      <div>
        <div className="w-12 h-12 rounded-xl bg-[#EFF6FF] grid place-items-center text-[#2563EB] mb-5 group-hover:bg-[#2563EB] group-hover:text-white transition-colors duration-300">
          <Icon size={22} strokeWidth={1.8} />
        </div>
        <h3 className="text-base font-bold text-[#0B0F19] mb-2 font-display">{title}</h3>
        <p className="text-sm text-gray-600 leading-relaxed">{desc}</p>
      </div>
      <div className="pt-4 mt-4 border-t border-gray-100 flex items-center justify-between text-[11px] font-semibold text-[#2563EB]">
        <span>Included in core tier</span>
        <span className="opacity-0 group-hover:opacity-100 transition-opacity" aria-hidden="true">→</span>
      </div>
    </motion.article>
  );
}

export default function Features() {
  const headerRef = useRef(null);
  const headerInView = useInView(headerRef, { once: true, margin: '-40px' });

  return (
    <section className="py-16 sm:py-24 bg-gray-50/70 border-y border-gray-100" id="features">
      <div className="max-w-[1200px] mx-auto px-4 sm:px-6">
        <motion.div
          ref={headerRef}
          initial={{ opacity: 0, y: 24 }}
          animate={headerInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.55 }}
          className="text-center max-w-[620px] mx-auto mb-12 sm:mb-16"
        >
          <span className="inline-flex items-center gap-2 text-xs font-bold tracking-widest uppercase text-[#2563EB] mb-3">
            <span className="w-5 h-0.5 bg-[#2563EB] rounded" />
            Core Capabilities
          </span>
          <h2 className="text-3xl md:text-4xl font-black tracking-tight text-[#0B0F19] leading-tight mb-4 font-display">
            Everything You Need to<br />
            <span className="text-gradient">Understand Your Money.</span>
          </h2>
          <p className="text-gray-600 text-base sm:text-[1.05rem] leading-relaxed">
            Fin4You brings your financial information into one clear, organized place — so you always know where you stand without confusing jargon.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {features.map((f) => (
            <FeatureCard key={f.title} {...f} />
          ))}
        </div>
      </div>
    </section>
  );
}
