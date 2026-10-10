import { Link } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-[#0B0F19] text-gray-300 pt-16 pb-10 border-t border-white/[0.06]">
      <div className="max-w-[1200px] mx-auto px-4 sm:px-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-10 mb-12">
          {/* Brand Info */}
          <div className="sm:col-span-2">
            <Link to="/" className="flex items-center gap-2.5 font-bold text-lg text-white mb-4">
              <span className="w-8 h-8 bg-[#2563EB] text-white rounded-lg grid place-items-center font-black text-sm">F</span>
              <span className="font-display">Fin4<strong className="text-[#93C5FD]">You</strong></span>
            </Link>
            <p className="text-sm text-gray-300 leading-relaxed max-w-sm mb-4">
              Your intelligent personal financial health copilot. Transform raw transactions into deterministic insights, disciplined budgets, and forward-looking clarity.
            </p>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs text-gray-300">
              <ShieldCheck size={14} className="text-emerald-400" />
              <span>256-bit Secure Encryption • Bank-Grade Privacy</span>
            </div>
          </div>

          {/* Product */}
          <div>
            <h3 className="text-xs font-bold tracking-widest uppercase text-white mb-4">Product</h3>
            <div className="flex flex-col gap-2.5 text-sm">
              <a href="/#features" className="text-gray-300 hover:text-white transition-colors py-1">Features</a>
              <a href="/#animation" className="text-gray-300 hover:text-white transition-colors py-1">Financial Story</a>
              <a href="/#artha-ai" className="text-gray-300 hover:text-white transition-colors py-1">Artha AI Assistant</a>
              <a href="/#how-it-works" className="text-gray-300 hover:text-white transition-colors py-1">How It Works</a>
              <a href="/#faq" className="text-gray-300 hover:text-white transition-colors py-1">FAQ</a>
            </div>
          </div>

          {/* Account & App */}
          <div>
            <h3 className="text-xs font-bold tracking-widest uppercase text-white mb-4">Application</h3>
            <div className="flex flex-col gap-2.5 text-sm">
              <Link to="/dashboard" className="text-gray-300 hover:text-white transition-colors py-1">Dashboard Portal</Link>
              <Link to="/login" className="text-gray-300 hover:text-white transition-colors py-1">Sign In</Link>
              <Link to="/signup" className="text-gray-300 hover:text-white transition-colors py-1">Create Account</Link>
              <Link to="/forgot-password" className="text-gray-300 hover:text-white transition-colors py-1">Password Recovery</Link>
            </div>
          </div>

          {/* Legal / Company */}
          <div>
            <h3 className="text-xs font-bold tracking-widest uppercase text-white mb-4">Security & Legal</h3>
            <div className="flex flex-col gap-2.5 text-sm">
              <a href="/#top" className="text-gray-300 hover:text-white transition-colors py-1">Security Architecture</a>
              <a href="/#top" className="text-gray-300 hover:text-white transition-colors py-1">Privacy Policy</a>
              <a href="/#top" className="text-gray-300 hover:text-white transition-colors py-1">Terms of Service</a>
              <a href="/#top" className="text-gray-300 hover:text-white transition-colors py-1">Deterministic Engine</a>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="flex flex-col sm:flex-row justify-between items-center gap-3 pt-8 border-t border-white/[0.08] text-xs text-gray-300">
          <span>© 2026 Fin4You Personal Finance Engine. All rights reserved.</span>
          <div className="flex items-center gap-4 text-gray-400">
            <span>Verified Decision Engine</span>
            <span>•</span>
            <span>Deterministic Math Model</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
