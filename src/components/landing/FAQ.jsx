import { useState, useRef } from 'react';
import { useInView } from 'motion/react';
import { ChevronDown } from 'lucide-react';

const faqs = [
  { q: 'What is Fin4You?', a: 'Fin4You is a personal financial assistant that helps you understand your money better. It provides a dashboard to view your financial overview, track recorded transactions, explore spending patterns, and review financial summaries — all in one clear, organised place.' },
  { q: 'How do I get started?', a: 'Simply create an account with your email address and a password. No bank account connection or financial history is required to sign up. Once logged in, you can explore the dashboard and available features at your own pace.' },
  { q: 'How can I understand my spending?', a: 'Fin4You breaks down your recorded expenses by category and presents them visually. You can see where your money goes each month, compare periods, and identify patterns through the Spending Insights section.' },
  { q: 'What can I view on my dashboard?', a: 'Your dashboard shows your financial overview — including income, expenses, savings summary, and spending breakdowns. It is your central hub for reviewing your complete financial picture at a glance.' },
  { q: 'How do financial summaries and forecasts help?', a: 'Financial summaries give you a clear picture of any period\'s activity, making it easy to spot trends over time. Forecasts use your recorded patterns to explore potential future financial trajectories, helping you make more informed decisions.' },
  { q: 'How do I access my account?', a: 'Visit the Login page and enter your email address and password. If you forget your password, use the Forgot Password option. Your session is securely maintained so you stay logged in across visits.' },
];

function FAQItem({ q, a }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border-b border-gray-200 last:border-0">
      <button
        className="flex items-center justify-between w-full py-5 text-left group"
        onClick={() => setOpen(v => !v)}
        aria-expanded={open}
      >
        <span className={`text-sm font-semibold transition-colors ${open ? 'text-[#2563EB]' : 'text-[#0B0F19] group-hover:text-[#2563EB]'}`}>{q}</span>
        <ChevronDown
          size={18}
          className={`flex-shrink-0 ml-4 text-gray-400 transition-transform duration-300 ${open ? 'rotate-180 text-[#2563EB]' : ''}`}
        />
      </button>
      <div className={`overflow-hidden transition-all duration-400 ease-in-out ${open ? 'max-h-48 pb-4' : 'max-h-0'}`}>
        <p className="text-sm text-gray-500 leading-relaxed">{a}</p>
      </div>
    </div>
  );
}

export default function FAQ() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-80px' });

  return (
    <section className="py-24 bg-white" id="faq">
      <div className="max-w-[1160px] mx-auto px-6">
        <div
          ref={ref}
          className={`text-center max-w-[580px] mx-auto mb-12 transition-all duration-700 ${inView ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-7'}`}
        >
          <span className="inline-flex items-center gap-2 text-xs font-bold tracking-widest uppercase text-[#2563EB] mb-4">
            <span className="w-6 h-0.5 bg-[#2563EB] rounded" />
            FAQ
          </span>
          <h2 className="text-3xl md:text-4xl font-black tracking-tight text-[#0B0F19] leading-tight mb-4">
            Common Questions<br /><em className="not-italic text-[#2563EB]">Answered.</em>
          </h2>
        </div>
        <div className="max-w-[720px] mx-auto bg-white rounded-2xl border border-gray-100 shadow-card px-6">
          {faqs.map(f => <FAQItem key={f.q} {...f} />)}
        </div>
      </div>
    </section>
  );
}
