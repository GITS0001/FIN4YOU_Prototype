import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  Bot,
  Send,
  ArrowRight,
  TrendingUp,
  Shield,
  HelpCircle,
  PieChart,
  IndianRupee,
  CheckCircle2,
  Lightbulb,
  MessageSquare,
  RefreshCw,
  Sliders,
  Compass,
} from 'lucide-react';

// ─── Preset Interactive Conversations ─────────────────────────
const PRESET_CONVERSATIONS = [
  {
    id: 'budget',
    prompt: 'Help me create a monthly budget for ₹45,000 salary',
    userMessage: 'I earn ₹45,000/month. How should I structure my monthly budget to save consistently?',
    botResponse: {
      headline: 'The 50 / 30 / 20 Framework for ₹45,000',
      summary:
        'A balanced monthly allocation tailored to cover all essential living costs while securing ₹9,000 in monthly savings.',
      breakdown: [
        { category: 'Essentials (50%)', amount: '₹22,500', detail: 'Rent, groceries, utilities, transit' },
        { category: 'Flexible / Lifestyle (30%)', amount: '₹13,500', detail: 'Dining, personal care, subscriptions' },
        { category: 'Savings & Reserve (20%)', amount: '₹9,000', detail: 'Emergency fund SIP & investments' },
      ],
      insight: '✦ Pro-Tip: Automate the ₹9,000 transfer on salary day to prevent accidental discretionary overspending.',
      suggestedFollowUp: 'How much should I keep in an emergency fund?',
    },
  },
  {
    id: 'spending',
    prompt: 'Where did my money go this month?',
    userMessage: 'I feel like my salary vanished within 15 days. How do I track where it went?',
    botResponse: {
      headline: '3 Step Leak Audit with Fin4You',
      summary:
        'Most unaccounted cash drains occur in untracked micro-transactions rather than large bills.',
      breakdown: [
        { category: 'Micro-Deliveries & Quick Snacks', amount: '~₹4,200', detail: 'Daily food delivery apps & snacks' },
        { category: 'Unused Subscriptions', amount: '~₹1,499', detail: 'Auto-renewed streaming & gym plans' },
        { category: 'Impulse Shopping', amount: '~₹5,800', detail: 'Flash sale e-commerce purchases' },
      ],
      insight: '✦ Fin4You automatically tags these into recurring vs discretionary buckets so you see trends instantly.',
      suggestedFollowUp: 'Help me set spending limits for dining out',
    },
  },
  {
    id: 'emergency',
    prompt: 'Explain emergency funds simply',
    userMessage: 'What is an emergency fund, and why do I need one before investing?',
    botResponse: {
      headline: 'Your Financial Shock Absorber',
      summary:
        'An emergency fund is 3 to 6 months of mandatory living expenses kept in an easily accessible, risk-free account.',
      breakdown: [
        { category: 'Ideal Target Size', amount: '₹60,000 – ₹1,20,000', detail: 'Calculated as 3× to 6× your monthly essentials' },
        { category: 'Where to Store It', amount: 'High-Yield / Liquid', detail: 'Savings account or liquid mutual fund' },
        { category: 'When to Use', amount: 'Only Emergencies', detail: 'Job gap, sudden medical bill, urgent home repair' },
      ],
      insight: '✦ Having this fund prevents you from borrowing expensive personal loans or selling long-term investments in distress.',
      suggestedFollowUp: 'Help me plan a savings goal',
    },
  },
  {
    id: 'needs-wants',
    prompt: 'Difference between needs and wants',
    userMessage: 'How do I clearly distinguish between essential needs and discretionary wants?',
    botResponse: {
      headline: 'The 48-Hour Decision Rule',
      summary:
        'Needs are required for survival and livelihood; wants enhance comfort and entertainment.',
      breakdown: [
        { category: 'Needs (Non-Negotiable)', amount: 'Fixed Outflow', detail: 'Shelter, medicine, basic food, debt EMIs' },
        { category: 'Wants (Flexible)', amount: 'Discretionary', detail: 'Upgraded gadgets, café dining, vacations' },
        { category: 'The 48h Test', amount: 'Psychological Buffer', detail: 'Wait 48 hours before any non-essential purchase over ₹1,500' },
      ],
      insight: '✦ Categorizing transactions upon entry cuts impulse spending by an average of 22% within 60 days.',
      suggestedFollowUp: 'Help me create a monthly budget for ₹45,000 salary',
    },
  },
];

export default function ArthaAIShowcase() {
  const [selectedConversation, setSelectedConversation] = useState(PRESET_CONVERSATIONS[0]);
  const [isTyping, setIsTyping] = useState(false);
  const [customInput, setCustomInput] = useState('');
  const [activeMessage, setActiveMessage] = useState(PRESET_CONVERSATIONS[0]);
  const chatScrollRef = useRef(null);

  const handleSelectPrompt = (conv) => {
    if (conv.id === activeMessage.id && !isTyping) return;
    setSelectedConversation(conv);
    setIsTyping(true);

    // Simulate realistic conversational AI thinking time
    setTimeout(() => {
      setActiveMessage(conv);
      setIsTyping(false);
    }, 650);
  };

  const handleCustomSubmit = (e) => {
    e.preventDefault();
    if (!customInput.trim()) return;

    const query = customInput.trim();
    setCustomInput('');
    setIsTyping(true);

    // Generate responsive demo explanation
    const customResponse = {
      id: 'custom-' + Date.now(),
      prompt: query,
      userMessage: query,
      botResponse: {
        headline: 'Financial Guidance: ' + query,
        summary:
          'Artha AI breaks down complex financial choices into structured, bite-sized decisions you can implement right away.',
        breakdown: [
          { category: '1. Establish Current Baseline', amount: 'Step 1', detail: 'Log current income, fixed liabilities, and cash flow' },
          { category: '2. Determine Trade-offs', amount: 'Step 2', detail: 'Compare short-term pleasure against long-term financial security' },
          { category: '3. Automate Execution', amount: 'Step 3', detail: 'Set automatic transfers so discipline happens by default' },
        ],
        insight: '✦ Sign up for Fin4You to connect your real tracking and unlock ongoing conversational coaching.',
        suggestedFollowUp: 'Help me create a monthly budget for ₹45,000 salary',
      },
    };

    setTimeout(() => {
      setActiveMessage(customResponse);
      setIsTyping(false);
    }, 700);
  };

  return (
    <section
      className="relative py-24 md:py-32 bg-white overflow-hidden border-t border-gray-100"
      id="artha-ai"
      aria-label="Artha AI Showcase"
    >
      {/* Background radial glow accents */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/3 left-1/4 w-[600px] h-[500px] bg-gradient-to-tr from-blue-100/40 via-blue-50/20 to-transparent rounded-full blur-3xl -z-10" />
        <div className="absolute bottom-10 right-10 w-[500px] h-[400px] bg-blue-50/60 rounded-full blur-3xl -z-10" />
      </div>

      <div className="max-w-[1340px] mx-auto px-4 sm:px-6 lg:px-8 relative">
        {/* Section Pill Badge & Main Title */}
        <div className="text-center max-w-3xl mx-auto mb-16 md:mb-20">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-50 border border-blue-200/80 text-[#2563EB] text-xs font-bold tracking-wider uppercase mb-4 shadow-xs">
            <Sparkles className="w-4 h-4 text-[#2563EB]" />
            CONVERSATIONAL FINANCIAL INTELLIGENCE
          </div>

          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-[#0B0F19] leading-[1.14]">
            Your Money. Your Questions. <br className="hidden sm:inline" />
            <span className="text-gradient">Clearer Answers with Artha AI.</span>
          </h2>

          <p className="mt-4 text-base sm:text-lg text-gray-600 leading-relaxed max-w-2xl mx-auto">
            Meet <strong>Artha AI</strong>, the conversational financial co-pilot inside Fin4You. Ask questions in natural language, understand your spending leaks, explore budgeting rules, and make confident financial decisions.
          </p>
        </div>

        {/* Dual Area Showcase Container: Left Messaging + Right Chat Interface */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-start">
          {/* ── Left Area: Product Messaging & Core Capabilities (5 cols) ── */}
          <div className="lg:col-span-5 flex flex-col gap-6">
            <div className="bg-[#F8FAFC] rounded-3xl p-6 md:p-8 border border-gray-100 shadow-sm">
              {/* Artha AI Brand Badge */}
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#2563EB] to-[#1D4ED8] flex items-center justify-center text-white shadow-blue">
                  <Bot className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-xl font-black text-[#0B0F19]">Artha AI</h3>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#EFF6FF] text-[#2563EB] border border-blue-200">
                      Co-Pilot
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 font-medium">Fin4You Conversational Assistant</p>
                </div>
              </div>

              <h4 className="text-lg font-bold text-[#0B0F19] mb-3">
                Why Talk to a Financial Assistant?
              </h4>
              <p className="text-sm text-gray-600 leading-relaxed mb-6">
                Spreadsheets and complex charts often leave people confused. Artha AI lets you ask regular questions like you would to a trusted friend, receiving calm, educational, step-by-step guidance.
              </p>

              {/* 4 Concrete Capabilities */}
              <div className="space-y-4">
                <div className="flex items-start gap-3.5 p-3 rounded-2xl bg-white border border-gray-100/90 shadow-xs">
                  <div className="w-8 h-8 rounded-xl bg-blue-50 text-[#2563EB] flex items-center justify-center flex-shrink-0 mt-0.5">
                    <MessageSquare className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-gray-900">Natural-Language Inquiries</div>
                    <p className="text-[11px] text-gray-500 mt-0.5 leading-relaxed">
                      No jargon required. Ask "How do I split my ₹35,000 salary?" and get clear allocations.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3.5 p-3 rounded-2xl bg-white border border-gray-100/90 shadow-xs">
                  <div className="w-8 h-8 rounded-xl bg-blue-50 text-[#2563EB] flex items-center justify-center flex-shrink-0 mt-0.5">
                    <PieChart className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-gray-900">Expense & Leak Sensemaking</div>
                    <p className="text-[11px] text-gray-500 mt-0.5 leading-relaxed">
                      Understand where your money is draining without doing manual math or wrestling with formulas.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3.5 p-3 rounded-2xl bg-white border border-gray-100/90 shadow-xs">
                  <div className="w-8 h-8 rounded-xl bg-blue-50 text-[#2563EB] flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Compass className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-gray-900">Financial Concepts Made Simple</div>
                    <p className="text-[11px] text-gray-500 mt-0.5 leading-relaxed">
                      Accessible explanations of emergency funds, SIPs, inflation, needs vs wants, and debt snowballs.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3.5 p-3 rounded-2xl bg-white border border-gray-100/90 shadow-xs">
                  <div className="w-8 h-8 rounded-xl bg-blue-50 text-[#2563EB] flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Sliders className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-gray-900">Conversational Follow-ups</div>
                    <p className="text-[11px] text-gray-500 mt-0.5 leading-relaxed">
                      Dig deeper without restarting. Adjust for rent increases, variable bonuses, or life changes.
                    </p>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-8 flex flex-col sm:flex-row gap-3">
                <Link
                  to="/signup"
                  className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3.5 bg-[#2563EB] text-white font-bold rounded-xl shadow-blue hover:bg-[#1D4ED8] transition-all hover:-translate-y-0.5 text-sm"
                >
                  Explore Artha AI
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <Link
                  to="/login"
                  className="inline-flex items-center justify-center px-5 py-3.5 bg-white text-gray-700 font-bold rounded-xl border border-gray-200 hover:border-blue-300 hover:text-[#2563EB] transition-colors text-sm"
                >
                  Sign In
                </Link>
              </div>

              <div className="mt-4 flex items-center gap-2 text-[11px] text-gray-400">
                <Shield className="w-3.5 h-3.5 text-gray-400" />
                <span>Conversational guidance tool • Clear educational insights</span>
              </div>
            </div>
          </div>

          {/* ── Right Area: Interactive Conversational AI Interface Preview (7 cols) ── */}
          <div className="lg:col-span-7 w-full">
            <div className="bg-white rounded-3xl border border-blue-200/80 shadow-2xl shadow-blue-900/5 overflow-hidden flex flex-col">
              {/* Chat Header */}
              <div className="bg-[#0B0F19] text-white px-5 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#2563EB] to-blue-400 flex items-center justify-center font-black text-sm">
                      ✦
                    </div>
                    <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-green-500 border-2 border-[#0B0F19]" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm">Artha AI Assistant</span>
                      <span className="px-2 py-0.2 rounded-full text-[9px] font-bold bg-blue-500/20 text-blue-300 border border-blue-400/30">
                        Demo Sandbox
                      </span>
                    </div>
                    <span className="text-[11px] text-gray-400">Fin4You Intelligent Guidance System</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleSelectPrompt(PRESET_CONVERSATIONS[0])}
                    className="text-[11px] text-gray-400 hover:text-white flex items-center gap-1 transition-colors px-2 py-1 rounded-md hover:bg-white/10"
                    title="Reset chat"
                  >
                    <RefreshCw className="w-3 h-3" />
                    Reset
                  </button>
                </div>
              </div>

              {/* Suggested Prompt Chips Carousel */}
              <div className="bg-[#F8FAFC] border-b border-gray-100 p-3.5">
                <div className="text-[11px] font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <Lightbulb className="w-3.5 h-3.5 text-[#2563EB]" />
                  Try Sample Questions (Click to Ask):
                </div>
                <div className="flex flex-wrap gap-2">
                  {PRESET_CONVERSATIONS.map((c) => {
                    const isSelected = selectedConversation.id === c.id;
                    return (
                      <button
                        key={c.id}
                        onClick={() => handleSelectPrompt(c)}
                        className={`text-xs px-3 py-1.5 rounded-xl font-medium transition-all text-left flex items-center gap-1.5 ${
                          isSelected
                            ? 'bg-[#2563EB] text-white shadow-xs'
                            : 'bg-white text-gray-700 hover:bg-blue-50 border border-gray-200/80 hover:border-blue-200'
                        }`}
                      >
                        <Sparkles className={`w-3 h-3 ${isSelected ? 'text-white' : 'text-[#2563EB]'}`} />
                        <span>{c.prompt}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Chat Messages Body */}
              <div
                ref={chatScrollRef}
                className="p-5 md:p-6 min-h-[360px] max-h-[460px] overflow-y-auto flex flex-col gap-5 bg-gradient-to-b from-white via-white to-[#F8FAFC]"
              >
                {/* Welcome intro notice */}
                <div className="text-center my-1">
                  <span className="inline-block px-3 py-1 rounded-full bg-gray-100 text-gray-500 text-[10px] font-medium">
                    Today • Interactive AI Demo Experience
                  </span>
                </div>

                {/* User Message Bubble */}
                <div className="flex justify-end items-end gap-2.5">
                  <div className="bg-[#0B0F19] text-white text-xs sm:text-sm font-medium px-4 py-3 rounded-2xl rounded-br-sm max-w-[85%] shadow-sm leading-relaxed">
                    {activeMessage.userMessage}
                  </div>
                  <div className="w-7 h-7 rounded-full bg-gray-200 flex items-center justify-center text-[10px] font-bold text-gray-700 flex-shrink-0">
                    You
                  </div>
                </div>

                {/* Assistant Message Bubble with Interactive Typing State */}
                <div className="flex justify-start items-start gap-2.5">
                  <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-[#2563EB] to-blue-400 text-white flex items-center justify-center text-xs font-black flex-shrink-0 mt-1">
                    ✦
                  </div>

                  <div className="flex-1 max-w-[92%]">
                    {isTyping ? (
                      /* Typing Indicator */
                      <div className="bg-[#F0F6FF] border border-blue-100 rounded-2xl rounded-tl-sm p-4 inline-flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-[#2563EB] animate-bounce" />
                        <span className="w-2 h-2 rounded-full bg-[#2563EB] animate-bounce [animation-delay:0.15s]" />
                        <span className="w-2 h-2 rounded-full bg-[#2563EB] animate-bounce [animation-delay:0.3s]" />
                        <span className="text-xs text-blue-700 font-medium ml-1">Artha AI is analyzing...</span>
                      </div>
                    ) : (
                      /* Response Container */
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.35 }}
                        className="bg-white border border-blue-100/90 rounded-2xl rounded-tl-sm p-4 md:p-5 shadow-sm space-y-3.5"
                      >
                        {/* Title & Summary */}
                        <div>
                          <div className="text-xs sm:text-sm font-bold text-gray-900 flex items-center gap-2">
                            <span>{activeMessage.botResponse.headline}</span>
                            <span className="w-1.5 h-1.5 rounded-full bg-[#2563EB]" />
                          </div>
                          <p className="text-xs text-gray-600 mt-1 leading-relaxed">
                            {activeMessage.botResponse.summary}
                          </p>
                        </div>

                        {/* Structured Category Breakdown Table */}
                        <div className="bg-[#F8FAFC] rounded-xl border border-gray-100 overflow-hidden divide-y divide-gray-100">
                          {activeMessage.botResponse.breakdown.map((row, idx) => (
                            <div key={idx} className="p-2.5 sm:px-3 flex items-center justify-between gap-3 text-xs">
                              <div className="min-w-0">
                                <div className="font-bold text-gray-800">{row.category}</div>
                                <div className="text-[11px] text-gray-500 truncate">{row.detail}</div>
                              </div>
                              <span className="font-mono font-bold text-[#2563EB] flex-shrink-0 text-right">
                                {row.amount}
                              </span>
                            </div>
                          ))}
                        </div>

                        {/* Smart Insight Banner */}
                        <div className="bg-[#EFF6FF] border border-blue-200/80 rounded-xl p-2.5 text-xs text-blue-900 leading-relaxed font-medium">
                          {activeMessage.botResponse.insight}
                        </div>

                        {/* Suggested Follow Up Button */}
                        {activeMessage.botResponse.suggestedFollowUp && (
                          <div className="pt-1 flex items-center gap-2">
                            <span className="text-[10px] text-gray-400 font-semibold uppercase">Follow-up:</span>
                            <button
                              onClick={() => {
                                const match = PRESET_CONVERSATIONS.find((c) =>
                                  c.prompt.toLowerCase().includes('emergency') ||
                                  c.prompt.toLowerCase().includes('budget')
                                );
                                if (match) handleSelectPrompt(match);
                              }}
                              className="text-[11px] text-[#2563EB] font-bold hover:underline flex items-center gap-1"
                            >
                              "{activeMessage.botResponse.suggestedFollowUp}" ↗
                            </button>
                          </div>
                        )}
                      </motion.div>
                    )}
                  </div>
                </div>
              </div>

              {/* Chat Composer Bar */}
              <div className="p-3.5 bg-gray-50 border-t border-gray-100">
                <form onSubmit={handleCustomSubmit} className="flex items-center gap-2">
                  <div className="relative flex-1">
                    <input
                      type="text"
                      value={customInput}
                      onChange={(e) => setCustomInput(e.target.value)}
                      placeholder="Ask Artha about budgets, savings, or spending (e.g. 'How to start saving?')..."
                      className="w-full bg-white border border-gray-200 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#2563EB] focus:border-transparent transition-all shadow-xs"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={!customInput.trim()}
                    className="px-4 py-2.5 bg-[#2563EB] disabled:bg-gray-200 text-white disabled:text-gray-400 font-bold rounded-xl shadow-xs hover:bg-[#1D4ED8] transition-all flex items-center gap-1.5 text-xs sm:text-sm"
                  >
                    <span>Send</span>
                    <Send className="w-3.5 h-3.5" />
                  </button>
                </form>
                <div className="flex items-center justify-between mt-2 px-1 text-[10px] text-gray-400">
                  <span>✦ Interactive demonstration • Connect real data inside Fin4You</span>
                  <span>* Educational finance co-pilot</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
