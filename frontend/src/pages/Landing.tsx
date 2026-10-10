import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Shield, TrendingUp, Bot, ArrowRight, LayoutDashboard, Target, CheckCircle2, Lock, PieChart, BellRing, UserCheck, Menu, X, Sun, Moon } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';
import { motion } from 'framer-motion';
import fin4youLogo from '../assets/fin4you_logo.jpg';
import arthaAiLogo from '../assets/artha_ai_logo.jpg';

export const Landing: React.FC = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    e.preventDefault();
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const staggerContainer = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const slideUp = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  };

  return (
    <div className="min-h-screen bg-transparent text-primary-dark overflow-hidden relative">
      {/* Animated Greenish Background with Texture */}
      <div className="fixed inset-0 z-[-1] bg-gradient-to-br from-teal/15 via-background to-positive/15 bg-animated-gradient"></div>
      <div className="fixed inset-0 z-[-1] noise-filter"></div>

      {/* Navbar for Landing */}
      <nav
        className={`fixed w-full top-0 z-50 transition-all duration-300 ${
          scrolled
            ? 'bg-card-bg/70 backdrop-blur-xl border-b border-border shadow-sm py-2'
            : 'bg-transparent py-4'
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-12">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full overflow-hidden bg-primary-dark flex items-center justify-center shadow-md">
                <img src={fin4youLogo} alt="FIN4YOU Logo" className="w-full h-full object-cover" />
              </div>
              <span className="font-bold text-primary-dark text-xl tracking-tight">FIN4YOU</span>
            </div>

            {/* Top Navigation - Center */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" onClick={(e) => scrollToSection(e, 'features')} className="text-muted hover:text-primary-dark transition-colors font-medium text-sm">Features</a>
              <a href="#how-it-works" onClick={(e) => scrollToSection(e, 'how-it-works')} className="text-muted hover:text-primary-dark transition-colors font-medium text-sm">How it works</a>
              <a href="#security" onClick={(e) => scrollToSection(e, 'security')} className="text-muted hover:text-primary-dark transition-colors font-medium text-sm">Security</a>
            </div>

            {/* Login / Profile - Center/Right side in this context */}
            <div className="hidden md:flex items-center space-x-4">
              <button onClick={toggleTheme} className="p-2 text-muted hover:text-primary-dark transition-colors">
                {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
              </button>
              <Link to="/dashboard" className="btn-secondary">Log in</Link>
              <Link to="/dashboard" className="btn-primary bg-gradient-to-r from-primary-accent to-purple border-0">
                Get Started <ArrowRight size={16} />
              </Link>
            </div>

            {/* Mobile Menu Toggle */}
            <div className="md:hidden flex items-center">
              <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="text-primary-dark p-2">
                {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-card-bg border-b border-border shadow-lg absolute w-full left-0 top-full flex flex-col p-4 space-y-4">
            <a href="#features" onClick={(e) => { scrollToSection(e, 'features'); setMobileMenuOpen(false); }} className="text-primary-dark font-medium">Features</a>
            <a href="#how-it-works" onClick={(e) => { scrollToSection(e, 'how-it-works'); setMobileMenuOpen(false); }} className="text-primary-dark font-medium">How it works</a>
            <a href="#security" onClick={(e) => { scrollToSection(e, 'security'); setMobileMenuOpen(false); }} className="text-primary-dark font-medium">Security</a>
            <div className="flex flex-col space-y-2 pt-4 border-t border-border">
              <Link to="/dashboard" className="btn-secondary justify-center">Log in</Link>
              <Link to="/dashboard" className="btn-primary bg-gradient-to-r from-primary-accent to-purple border-0 justify-center">
                Get Started <ArrowRight size={16} />
              </Link>
            </div>
          </div>
        )}
      </nav>

      <main>
        {/* Hero Section */}
        <section className="pt-32 pb-32 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto text-center relative">
          <motion.div initial="hidden" animate="show" variants={staggerContainer} className="relative z-10">
            <motion.h1 variants={slideUp} className="text-5xl md:text-6xl font-bold text-primary-dark tracking-tight mb-6">
              Your personal financial <br className="hidden md:block" />
              <span className="text-primary-accent">copilot and strategist</span>
            </motion.h1>
            <motion.p variants={slideUp} className="text-lg md:text-xl text-muted max-w-2xl mx-auto mb-10">
              FIN4YOU simplifies your finances with AI-driven insights, forecasting, and affordability checks. Take control of your money, stress-free.
            </motion.p>
            <motion.div variants={slideUp} className="flex items-center justify-center gap-4">
              <Link to="/dashboard" className="btn-primary bg-gradient-to-r from-primary-accent to-purple border-0 text-base px-8 py-3 rounded-full hover:scale-105 transition-transform">
                Enter App <ArrowRight size={18} className="ml-2" />
              </Link>
            </motion.div>
          </motion.div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-24 bg-card-bg/40 backdrop-blur-md px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial="hidden" whileInView="show" viewport={{ once: true, margin: "-100px" }} variants={slideUp}
              className="text-center mb-16"
            >
              <h2 className="text-3xl font-bold text-primary-dark mb-4">Everything you need to grow your wealth</h2>
              <p className="text-muted max-w-2xl mx-auto">Powerful tools designed to help you understand, manage, and project your financial future.</p>
            </motion.div>

            <motion.div
              initial="hidden" whileInView="show" viewport={{ once: true, margin: "-100px" }} variants={staggerContainer}
              className="grid md:grid-cols-3 gap-8"
            >
              <motion.div variants={slideUp} whileHover={{ scale: 1.02, y: -5 }} className="card p-8 transition-all duration-300 cursor-pointer bg-card-bg">
                <div className="w-12 h-12 rounded-xl overflow-hidden bg-purple/10 flex items-center justify-center mb-6 shadow-sm">
                  <img src={arthaAiLogo} alt="Artha AI Logo" className="w-full h-full object-cover" />
                </div>
                <h3 className="text-xl font-semibold text-primary-dark mb-3">Artha AI Assistant</h3>
                <p className="text-muted mb-4">Ask questions about your spending, get personalized advice, and understand your financial health instantly with our trained AI.</p>
                <ul className="text-sm text-muted space-y-2">
                  <li className="flex items-center gap-2"><CheckCircle2 size={16} className="text-purple"/> Conversational queries</li>
                  <li className="flex items-center gap-2"><CheckCircle2 size={16} className="text-purple"/> Tailored financial advice</li>
                </ul>
              </motion.div>

              <motion.div variants={slideUp} whileHover={{ scale: 1.02, y: -5 }} className="card p-8 transition-all duration-300 cursor-pointer bg-card-bg">
                <div className="w-12 h-12 rounded-xl bg-positive/10 flex items-center justify-center mb-6">
                  <TrendingUp size={24} className="text-positive" />
                </div>
                <h3 className="text-xl font-semibold text-primary-dark mb-3">Smart Forecasting</h3>
                <p className="text-muted mb-4">See exactly where your money will be in the next 6-12 months based on your current habits and predictable recurring transactions.</p>
                <ul className="text-sm text-muted space-y-2">
                  <li className="flex items-center gap-2"><CheckCircle2 size={16} className="text-positive"/> Predictive balance modeling</li>
                  <li className="flex items-center gap-2"><CheckCircle2 size={16} className="text-positive"/> Expense trend analysis</li>
                </ul>
              </motion.div>

              <motion.div variants={slideUp} whileHover={{ scale: 1.02, y: -5 }} className="card p-8 transition-all duration-300 cursor-pointer bg-card-bg">
                <div className="w-12 h-12 rounded-xl bg-primary-accent/10 flex items-center justify-center mb-6">
                  <PieChart size={24} className="text-primary-accent" />
                </div>
                <h3 className="text-xl font-semibold text-primary-dark mb-3">Comprehensive Analytics</h3>
                <p className="text-muted mb-4">Connect all your accounts in one place for a complete, bird's-eye view of your net worth, budget allocation, and category breakdowns.</p>
                <ul className="text-sm text-muted space-y-2">
                  <li className="flex items-center gap-2"><CheckCircle2 size={16} className="text-primary-accent"/> Visual spending charts</li>
                  <li className="flex items-center gap-2"><CheckCircle2 size={16} className="text-primary-accent"/> Goal tracking integrations</li>
                </ul>
              </motion.div>
            </motion.div>
          </div>
        </section>

        {/* How It Works Section */}
        <section id="how-it-works" className="py-24 bg-soft-blue/30 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial="hidden" whileInView="show" viewport={{ once: true }} variants={slideUp}
              className="text-center mb-20"
            >
              <h2 className="text-3xl font-bold text-primary-dark mb-4">How it works</h2>
              <p className="text-muted max-w-2xl mx-auto">Three simple steps to take complete control of your financial life. We've optimized the onboarding process so you can get valuable insights in under 5 minutes.</p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-12 relative">
              {/* Connector line */}
              <div className="hidden md:block absolute top-12 left-[15%] right-[15%] h-0.5 bg-gradient-to-r from-primary-accent/10 via-primary-accent/40 to-primary-accent/10 z-0"></div>

              {[
                {
                  step: '1',
                  title: 'Connect Accounts Securely',
                  desc: 'Link your bank accounts, credit cards, and investments using our bank-grade secure Plaid integration. We never see your credentials.',
                  icon: <UserCheck size={24} className="text-primary-accent mb-2" />
                },
                {
                  step: '2',
                  title: 'AI Analysis & Categorization',
                  desc: 'Our intelligent engine instantly downloads your history, categorizes transactions, and identifies recurring bills to build a baseline.',
                  icon: <Bot size={24} className="text-primary-accent mb-2" />
                },
                {
                  step: '3',
                  title: 'Actionable Insights & Growth',
                  desc: 'Receive proactive alerts about overspending, get answers from Artha AI, and use our scenario planning to safely afford big purchases.',
                  icon: <TrendingUp size={24} className="text-primary-accent mb-2" />
                }
              ].map((item, i) => (
                <motion.div
                  key={item.step}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{ duration: 0.5, delay: i * 0.2 }}
                  className="relative z-10 flex flex-col items-center text-center group"
                >
                  <div className="w-24 h-24 rounded-full bg-card-bg border-4 border-card-bg flex flex-col items-center justify-center font-bold text-primary-accent mb-6 shadow-xl group-hover:scale-110 transition-transform duration-300">
                    <span className="text-2xl">{item.step}</span>
                  </div>
                  <h3 className="text-xl font-semibold text-primary-dark mb-3 flex flex-col items-center">
                    {item.icon}
                    {item.title}
                  </h3>
                  <p className="text-muted leading-relaxed">{item.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Security Section */}
        <section id="security" className="py-24 bg-transparent px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <div className="grid md:grid-cols-2 gap-16 items-center">
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
              >
                <div className="w-16 h-16 rounded-2xl bg-teal/10 flex items-center justify-center mb-8">
                  <Shield size={32} className="text-teal" />
                </div>
                <h2 className="text-3xl md:text-4xl font-bold text-primary-dark mb-6 leading-tight">
                  Bank-level security protecting your sensitive data
                </h2>
                <p className="text-lg text-muted mb-8">
                  Trust is our foundation. We treat your financial data with the highest level of security, compliance, and encryption protocols available in the industry. Your data is yours, and we never sell it to third parties.
                </p>

                <ul className="space-y-5">
                  {[
                    { title: 'Military-Grade Encryption', desc: '256-bit AES encryption for all data at rest and in transit.' },
                    { title: 'Read-Only Access', desc: 'We can only view your data. We cannot move funds or make changes to your accounts.' },
                    { title: 'Enterprise Compliance', desc: 'SOC 2 Type II certified infrastructure adhering to strict privacy laws.' },
                    { title: 'Continuous Monitoring', desc: '24/7 automated threat detection and regular third-party security audits.' }
                  ].map((feature, i) => (
                    <motion.li
                      key={i}
                      initial={{ opacity: 0, x: -20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.4, delay: i * 0.1 }}
                      className="flex items-start gap-4"
                    >
                      <div className="mt-1">
                        <CheckCircle2 size={24} className="text-teal" />
                      </div>
                      <div>
                        <span className="font-semibold text-primary-dark block mb-1">{feature.title}</span>
                        <span className="text-muted text-sm">{feature.desc}</span>
                      </div>
                    </motion.li>
                  ))}
                </ul>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
                className="relative"
              >
                <div className="aspect-square rounded-full bg-teal/10 absolute -inset-8 blur-3xl animate-pulse"></div>
                <div className="card p-12 relative bg-card-bg/80 backdrop-blur-2xl border border-border/50 shadow-2xl flex flex-col items-center justify-center text-center overflow-hidden">

                  {/* Decorative background element */}
                  <div className="absolute top-0 right-0 w-32 h-32 bg-teal/5 rounded-bl-full"></div>

                  <motion.div
                    animate={{ y: [0, -10, 0] }}
                    transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
                  >
                    <Lock size={80} className="text-teal mb-8" />
                  </motion.div>

                  <h3 className="text-2xl font-bold text-primary-dark mb-4">Safe & Secure</h3>
                  <p className="text-muted mb-6">
                    We partner with Plaid, the industry leader in financial data connectivity, to securely access your transaction history.
                  </p>
                  <div className="flex items-center justify-center gap-2 text-sm font-medium text-teal bg-teal/10 px-4 py-2 rounded-full">
                    <Shield size={16} /> Credentials never touch our servers
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </section>
      </main>

      <footer className="bg-primary-dark text-white/60 py-12 px-4 text-center border-t border-border">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center gap-2 mb-6 md:mb-0">
            <div className="w-8 h-8 rounded-full overflow-hidden bg-white/10 flex items-center justify-center shadow-md">
              <img src={fin4youLogo} alt="FIN4YOU Logo" className="w-full h-full object-cover" />
            </div>
            <span className="font-bold text-white tracking-tight text-lg">FIN4YOU</span>
          </div>

          <div className="flex gap-6 mb-6 md:mb-0 text-sm">
            <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-white transition-colors">Contact Support</a>
          </div>

          <p className="text-sm">© 2026 FIN4YOU. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};
