import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="bg-[#0B0F19] text-white/60 pt-16 pb-8">
      <div className="max-w-[1160px] mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          <div className="md:col-span-1">
            <Link to="/" className="flex items-center gap-2.5 font-bold text-lg text-white mb-4">
              <span className="w-8 h-8 bg-[#2563EB] text-white rounded-lg grid place-items-center font-black text-sm">F</span>
              <span>Fin4<strong className="text-[#93C5FD]">You</strong></span>
            </Link>
            <p className="text-sm leading-relaxed max-w-[240px]">Your personal financial assistant for smarter saving, spending and analysis.</p>
          </div>
          <div>
            <h4 className="text-xs font-bold tracking-widest uppercase text-white mb-5">Product</h4>
            <div className="flex flex-col gap-3">
              {[['Features','/#features'],['How It Works','/#how-it-works'],['Insights','/#insights'],['FAQ','/#faq']].map(([l,h])=>(
                <a key={l} href={h} className="text-sm hover:text-white transition-colors">{l}</a>
              ))}
            </div>
          </div>
          <div>
            <h4 className="text-xs font-bold tracking-widest uppercase text-white mb-5">Account</h4>
            <div className="flex flex-col gap-3">
              <Link to="/login" className="text-sm hover:text-white transition-colors">Log In</Link>
              <Link to="/signup" className="text-sm hover:text-white transition-colors">Sign Up</Link>
              <Link to="/forgot-password" className="text-sm hover:text-white transition-colors">Reset Password</Link>
            </div>
          </div>
          <div>
            <h4 className="text-xs font-bold tracking-widest uppercase text-white mb-5">Company</h4>
            <div className="flex flex-col gap-3">
              {['About','Privacy Policy','Terms of Use'].map(l=>(
                <a key={l} href="#top" className="text-sm hover:text-white transition-colors">{l}</a>
              ))}
            </div>
          </div>
        </div>
        <div className="flex flex-col md:flex-row justify-between items-center gap-2 pt-6 border-t border-white/[0.07] text-xs">
          <span>© 2026 Fin4You. All rights reserved.</span>
          <span>Made for clearer financial decisions.</span>
        </div>
      </div>
    </footer>
  );
}
