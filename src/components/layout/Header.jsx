import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, TrendingUp } from 'lucide-react';

const navLinks = [
  { label: 'Home', to: '/#top' },
  { label: 'Story', to: '/#animation' },
  { label: 'Artha AI', to: '/#artha-ai' },
  { label: 'Features', to: '/#features' },
  { label: 'How It Works', to: '/#how-it-works' },
  { label: 'FAQ', to: '/#faq' },
];

export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { pathname } = useLocation();

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 12);
    window.addEventListener('scroll', handler, { passive: true });
    return () => window.removeEventListener('scroll', handler);
  }, []);

  // Close mobile nav on route change
  useEffect(() => { setMobileOpen(false); }, [pathname]);

  const handleAnchor = (e, href) => {
    if (href.startsWith('/#') && pathname === '/') {
      e.preventDefault();
      const id = href.slice(2);
      const el = document.getElementById(id);
      if (el) {
        const top = el.getBoundingClientRect().top + window.scrollY - 76;
        window.scrollTo({ top, behavior: 'smooth' });
        setMobileOpen(false);
      }
    }
  };

  return (
    <>
      <header className={`sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-100 transition-shadow duration-300 ${scrolled ? 'shadow-sm' : ''}`}>
        <div className="max-w-[1160px] mx-auto px-6 h-[68px] flex items-center gap-8">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 font-bold text-[1.1rem] tracking-tight text-[#0B0F19] flex-shrink-0">
            <span className="w-8 h-8 bg-[#2563EB] text-white rounded-lg grid place-items-center font-black text-sm">F</span>
            <span>Fin4<strong className="text-[#2563EB]">You</strong></span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-1 ml-auto">
            {navLinks.map(l => (
              <a
                key={l.label}
                href={l.to}
                onClick={e => handleAnchor(e, l.to)}
                className="px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-[#2563EB] hover:bg-[#EFF6FF] transition-colors"
              >
                {l.label}
              </a>
            ))}
          </nav>
          <div className="hidden md:flex items-center gap-2.5 flex-shrink-0">
            <Link to="/login" className="px-4 py-2 rounded-lg text-sm font-semibold text-gray-700 border border-gray-200 hover:bg-gray-50 transition-colors">
              Log In
            </Link>
            <Link to="/signup" className="px-4 py-2 rounded-lg text-sm font-semibold bg-[#2563EB] text-white hover:bg-[#1D4ED8] transition-colors shadow-blue">
              Get Started
            </Link>
          </div>

          {/* Hamburger */}
          <button
            className="md:hidden ml-auto p-2 rounded-lg hover:bg-gray-100 transition-colors"
            onClick={() => setMobileOpen(v => !v)}
            aria-label="Toggle menu"
            aria-expanded={mobileOpen}
          >
            {mobileOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </header>

      {/* Mobile drawer */}
      <div className={`md:hidden fixed top-[68px] inset-x-0 z-40 bg-white border-b border-gray-100 shadow-lg transition-all duration-300 ${mobileOpen ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-2 pointer-events-none'}`}>
        <div className="px-6 py-4 flex flex-col gap-1">
          {navLinks.map(l => (
            <a
              key={l.label}
              href={l.to}
              onClick={e => handleAnchor(e, l.to)}
              className="px-3 py-3 rounded-lg text-sm font-medium text-gray-700 hover:text-[#2563EB] hover:bg-[#EFF6FF] transition-colors"
            >
              {l.label}
            </a>
          ))}
          <div className="flex flex-col gap-2 pt-3 mt-2 border-t border-gray-100">
            <Link to="/login" className="text-center px-4 py-2.5 rounded-lg text-sm font-semibold text-gray-700 border border-gray-200">Log In</Link>
            <Link to="/signup" className="text-center px-4 py-2.5 rounded-lg text-sm font-semibold bg-[#2563EB] text-white">Get Started</Link>
          </div>
        </div>
      </div>
    </>
  );
}
