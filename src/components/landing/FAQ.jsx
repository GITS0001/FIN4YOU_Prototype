import { useState, useRef } from 'react';
import { useInView } from 'motion/react';
import { ChevronDown } from 'lucide-react';

const faqs = [
  { q: 'What is Fin4You?', a: 'Fin4You is a personal financial health copilot and decision engine that helps you understand your money better. It provides a real-time dashboard to view your financial overview, track recorded transactions, explore spending patterns, and simulate 90-day cash-flow runway.' },
  { q: 'How do I get started?', a: 'Simply create an account with your email address and password. No bank integration or card is needed to start. Once logged in, you can explore the dashboard, test what-if scenarios, and consult Artha AI immediately.' },
  { q: 'How does Fin4You protect my data?', a: 'All data is secured with enterprise 256-bit encryption and Supabase row-level security. We strictly utilize verified, deterministic calculations — never passing confidential financial arithmetic to stochastic hallucinations.' },
  { q: 'What is Artha AI?', a: 'Artha AI is our built-in educational financial assistant. You can ask natural-language questions about 50/30/20 budgeting, emergency reserves, spending leaks, and affordability before making large purchases.' },
  { q: 'How do financial summaries and forecasts help?', a: 'Summaries turn fragmented transactions into intuitive category allocations. Forward forecasts model your recurring bills and income runs over 30, 60, and 90 days so you can foresee cash deficits before they happen.' },
  { q: 'Can I access Fin4You on mobile devices?', a: 'Yes! Fin4You is designed mobile-first with responsive interfaces, touch-optimized controls, and dedicated bottom navigation on smart phones and tablets.' },
];

function FAQItem({ q, a, index }) {
  const [open, setOpen] = useState(false);
  const panelId = `faq-panel-${index}`;
  const buttonId = `faq-button-${index}`;

  return (
    <div className="border-b border-gray-100 last:border-0">
      <button
        id={buttonId}
        className="flex items-center justify-between w-full py-5 text-left group focus:outline-none focus-visible:ring-2 focus-visible:ring-[#2563EB] rounded-lg touch-target"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls={panelId}
      >
        <span
          className={`text-sm sm:text-base font-semibold transition-colors pr-4 ${
            open ? 'text-[#2563EB]' : 'text-[#0B0F19] group-hover:text-[#2563EB]'
          }`}
        >
          {q}
        </span>
        <div
          className={`w-7 h-7 rounded-full flex items-center justify-center transition-all duration-300 flex-shrink-0 ${
            open ? 'bg-blue-50 text-[#2563EB] rotate-180' : 'bg-gray-100 text-gray-700 group-hover:text-gray-900'
          }`}
        >
          <ChevronDown size={17} />
        </div>
      </button>
      <div
        id={panelId}
        role="region"
        aria-labelledby={buttonId}
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          open ? 'max-h-56 pb-5 opacity-100' : 'max-h-0 pb-0 opacity-0'
        }`}
      >
        <p className="text-sm text-gray-700 leading-relaxed pl-1">{a}</p>
      </div>
    </div>
  );
}

export default function FAQ() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-60px' });

  return (
    <section className="py-16 sm:py-24 bg-white" id="faq">
      <div className="max-w-[1200px] mx-auto px-4 sm:px-6">
        <div
          ref={ref}
          className={`text-center max-w-[620px] mx-auto mb-12 sm:mb-16 transition-all duration-700 ${
            inView ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'
          }`}
        >
          <span className="inline-flex items-center gap-2 text-xs font-bold tracking-widest uppercase text-[#2563EB] mb-3">
            <span className="w-5 h-0.5 bg-[#2563EB] rounded" />
            Frequently Asked Questions
          </span>
          <h2 className="text-3xl md:text-4xl font-black tracking-tight text-[#0B0F19] leading-tight mb-4 font-display">
            Common Questions <br />
            <span className="text-gradient">Answered Simply.</span>
          </h2>
          <p className="text-gray-600 text-sm sm:text-base leading-relaxed">
            Have questions about your data, security, or getting started? Here is everything you need to know.
          </p>
        </div>

        <div className="max-w-[760px] mx-auto bg-white rounded-2xl sm:rounded-3xl border border-gray-200/80 shadow-card p-4 sm:p-8">
          {faqs.map((f, i) => (
            <FAQItem key={f.q} {...f} index={i} />
          ))}
        </div>
      </div>
    </section>
  );
}
