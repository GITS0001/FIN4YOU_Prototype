import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, ArrowRight, ShieldCheck, LayoutDashboard } from 'lucide-react';
import { supabase } from '../../lib/supabase';

const navLinks = [
  { label: 'Overview', to: '/#top' },
  { label: 'Story', to: '/#animation' },
  { label: 'Artha AI', to: '/#artha-ai' },
  { label: 'Features', to: '/#features' },
  { label: 'How It Works', to: '/#how-it-works' },
  { label: 'FAQ', to: '/#faq' },
];

export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [user, setUser] = useState(null);
  const { pathname } = useLocation();

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 12);
    window.addEventListener('scroll', handler, { passive: true });
    return () => window.removeEventListener('scroll', handler);
  }, []);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user || null);
    });
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_, s) => {
      setUser(s?.user || null);
    });
    return () => subscription.unsubscribe();
  }, []);

  // Close mobile nav on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  // Lock body scroll when mobile menu is open
  useEffect(() => {
    if (mobileOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [mobileOpen]);

  const handleAnchor = (e, href) => {
    if (href.startsWith('/#') && pathname === '/') {
      e.preventDefault();
      const id = href.slice(2);
      const el = document.getElementById(id);
      if (el) {
        const top = el.getBoundingClientRect().top + window.scrollY - 74;
        window.scrollTo({ top, behavior: 'smooth' });
        setMobileOpen(false);
      }
    }
  };

  return (
    <>
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2.5 focus:bg-[#2563EB] focus:text-white focus:font-semibold focus:rounded-xl focus:shadow-xl focus:outline-none focus:ring-4 focus:ring-blue-300"
      >
        Skip to main content
      </a>

      <header
        className={`sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-gray-100 transition-all duration-200 ${
          scrolled ? 'shadow-xs border-gray-200/80 bg-white/98' : ''
        }`}
      >
        <div className="max-w-[1200px] mx-auto px-4 sm:px-6 h-[70px] flex items-center justify-between gap-4">
          {/* Logo */}
          <Link
            to="/"
            className="flex items-center gap-2.5 font-bold text-lg tracking-tight text-[#0B0F19] flex-shrink-0 group focus:outline-none focus-visible:ring-2 focus-visible:ring-[#2563EB] rounded-lg"
          >
            <div className="w-9 h-9 bg-[#2563EB] text-white rounded-xl grid place-items-center font-black text-sm shadow-blue group-hover:scale-105 transition-transform">
              F
            </div>
            <span className="font-display">
              Fin4<strong className="text-[#2563EB]">You</strong>
            </span>
            <span className="hidden sm:inline-flex items-center gap-1 text-[10px] font-semibold tracking-wide text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200/60 ml-1">
              <ShieldCheck size={11} className="text-emerald-600" />
              Verified
            </span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((l) => (
              <a
                key={l.label}
                href={l.to}
                onClick={(e) => handleAnchor(e, l.to)}
                className="px-3.5 py-2 rounded-lg text-sm font-medium text-gray-600 hover:text-[#2563EB] hover:bg-[#EFF6FF] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#2563EB]"
              >
                {l.label}
              </a>
            ))}
          </nav>

          {/* Desktop Action CTAs */}
          <div className="hidden md:flex items-center gap-2.5 flex-shrink-0">
            {user ? (
              <Link
                to="/dashboard"
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold bg-[#2563EB] text-white hover:bg-[#1D4ED8] transition-all shadow-blue"
              >
                <LayoutDashboard size={16} />
                Open Dashboard
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  className="px-4 py-2.5 rounded-xl text-sm font-semibold text-gray-700 hover:text-[#2563EB] hover:bg-gray-50 border border-gray-200 hover:border-blue-200 transition-all"
                >
                  Log In
                </Link>
                <Link
                  to="/signup"
                  className="flex items-center gap-1.5 px-4.5 py-2.5 rounded-xl text-sm font-semibold bg-[#2563EB] text-white hover:bg-[#1D4ED8] transition-all shadow-blue"
                >
                  <span>Get Started</span>
                  <ArrowRight size={15} />
                </Link>
              </>
            )}
          </div>

          {/* Mobile Hamburger Button with comfortable 44px tap target */}
          <button
            className="md:hidden p-2.5 rounded-xl text-gray-700 hover:text-[#2563EB] hover:bg-gray-100 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#2563EB] touch-target"
            onClick={() => setMobileOpen((v) => !v)}
            aria-label={mobileOpen ? 'Close navigation menu' : 'Open navigation menu'}
            aria-expanded={mobileOpen}
          >
            {mobileOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </header>

      {/* Mobile Backdrop & Drawer */}
      {mobileOpen && (
        <div
          className="md:hidden fixed inset-0 z-40 bg-black/40 backdrop-blur-xs animate-fade-in"
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      <div
        className={`md:hidden fixed top-[70px] inset-x-0 z-50 bg-white border-b border-gray-200 shadow-xl transition-all duration-250 ease-out max-h-[calc(100vh-70px)] overflow-y-auto ${
          mobileOpen ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-3 pointer-events-none'
        }`}
      >
        <div className="px-5 py-5 flex flex-col gap-1.5">
          {navLinks.map((l) => (
            <a
              key={l.label}
              href={l.to}
              onClick={(e) => handleAnchor(e, l.to)}
              className="px-4 py-3 rounded-xl text-base font-semibold text-gray-800 hover:text-[#2563EB] hover:bg-[#EFF6FF] active:bg-blue-100 transition-colors touch-target flex items-center justify-between"
            >
              <span>{l.label}</span>
              <span className="text-gray-400 text-xs">→</span>
            </a>
          ))}

          <div className="flex flex-col gap-2.5 pt-4 mt-2 border-t border-gray-100">
            {user ? (
              <Link
                to="/dashboard"
                onClick={() => setMobileOpen(false)}
                className="w-full flex items-center justify-center gap-2 py-3.5 px-4 rounded-xl text-sm font-bold bg-[#2563EB] text-white shadow-blue active:scale-[0.99] touch-target"
              >
                <LayoutDashboard size={18} />
                Go to Dashboard
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  onClick={() => setMobileOpen(false)}
                  className="w-full text-center py-3.5 px-4 rounded-xl text-sm font-bold text-gray-800 border border-gray-200 hover:bg-gray-50 active:bg-gray-100 touch-target"
                >
                  Log In
                </Link>
                <Link
                  to="/signup"
                  onClick={() => setMobileOpen(false)}
                  className="w-full flex items-center justify-center gap-2 py-3.5 px-4 rounded-xl text-sm font-bold bg-[#2563EB] text-white shadow-blue active:scale-[0.99] touch-target"
                >
                  <span>Create Free Account</span>
                  <ArrowRight size={16} />
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
