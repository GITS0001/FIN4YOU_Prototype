import { useRef, useEffect } from 'react';
import { motion, useInView } from 'motion/react';
import { LayoutDashboard, ArrowRightLeft, PieChart, FileText, TrendingUp, BarChart3 } from 'lucide-react';

const features = [
  { icon: LayoutDashboard, title: 'Financial Dashboard', desc: 'View your complete financial overview in one place — income, expenses, savings, and summaries at a glance.', delay: 0 },
  { icon: ArrowRightLeft, title: 'Transaction Tracking', desc: 'Understand your recorded income and expenses clearly. See exactly what came in and what went out.', delay: 0.08 },
  { icon: PieChart, title: 'Spending Insights', desc: 'Explore where your money is going with clear category breakdowns and visual spending patterns.', delay: 0.16 },
  { icon: FileText, title: 'Financial Summaries', desc: 'Review your financial activity over any period with clear, concise summaries that are easy to understand.', delay: 0.24 },
  { icon: TrendingUp, title: 'Forecasting', desc: 'Explore potential future financial trends based on your recorded patterns and historical data.', delay: 0.32 },
  { icon: BarChart3, title: 'Monthly Reports', desc: 'Review your monthly financial performance with detailed breakdowns to understand your progress over time.', delay: 0.40 },
];

function FeatureCard({ icon: Icon, title, desc, delay }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-60px' });
  return (
    <motion.article
      ref={ref}
      initial={{ opacity: 0, y: 28 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ delay, duration: 0.55, ease: [0.4, 0, 0.2, 1] }}
      className="group bg-white rounded-2xl p-7 border border-gray-100 shadow-card hover:-translate-y-1 hover:shadow-lg hover:border-[#BFDBFE] transition-all duration-300"
    >
      <div className="w-12 h-12 rounded-xl bg-[#EFF6FF] grid place-items-center text-[#2563EB] mb-5 group-hover:bg-[#2563EB] group-hover:text-white transition-colors duration-300">
        <Icon size={22} strokeWidth={1.8} />
      </div>
      <h3 className="text-base font-bold text-[#0B0F19] mb-2.5">{title}</h3>
      <p className="text-sm text-gray-500 leading-relaxed">{desc}</p>
    </motion.article>
  );
}

export default function Features() {
  const headerRef = useRef(null);
  const headerInView = useInView(headerRef, { once: true, margin: '-60px' });

  return (
    <section className="py-24 bg-gray-50 border-y border-gray-100" id="features">
      <div className="max-w-[1160px] mx-auto px-6">
        <motion.div
          ref={headerRef}
          initial={{ opacity: 0, y: 28 }}
          animate={headerInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center max-w-[600px] mx-auto mb-14"
        >
          <span className="inline-flex items-center gap-2 text-xs font-bold tracking-widest uppercase text-[#2563EB] mb-4">
            <span className="w-6 h-0.5 bg-[#2563EB] rounded" />
            Features
          </span>
          <h2 className="text-3xl md:text-4xl font-black tracking-tight text-[#0B0F19] leading-tight mb-4">
            Everything You Need to<br /><em className="not-italic text-[#2563EB]">Understand Your Money.</em>
          </h2>
          <p className="text-gray-500 text-[1.02rem] leading-relaxed">
            Fin4You brings your financial information into one clear, organised place — so you always know where you stand.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map(f => <FeatureCard key={f.title} {...f} />)}
        </div>
      </div>
    </section>
  );
}
