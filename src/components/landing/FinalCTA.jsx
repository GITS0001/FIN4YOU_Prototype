import { Link } from 'react-router-dom';

export default function FinalCTA() {
  return (
    <section className="relative bg-[#0B0F19] text-white py-24 overflow-hidden text-center" id="start">
      {/* Glow blobs */}
      <div className="absolute w-96 h-96 rounded-full blur-[80px] bg-[#2563EB]/20 -left-24 -top-24 pointer-events-none" />
      <div className="absolute w-80 h-80 rounded-full blur-[80px] bg-[#1D4ED8]/15 -right-16 -bottom-16 pointer-events-none" />

      <div className="relative max-w-[640px] mx-auto px-6">
        <span className="inline-flex items-center gap-2 text-xs font-bold tracking-widest uppercase text-[#93C5FD] mb-5">
          <span className="w-6 h-0.5 bg-[#93C5FD] rounded" />
          Start Today
        </span>
        <h2 className="text-3xl md:text-5xl font-black tracking-tight leading-[1.1] mb-5">
          Your Financial Journey<br />
          Starts <em className="not-italic text-[#93C5FD]">Here.</em>
        </h2>
        <p className="text-white/65 text-lg leading-relaxed mb-10 max-w-[480px] mx-auto">
          Join Fin4You and take your first step toward greater clarity, confidence, and control over your personal finances.
        </p>
        <div className="flex flex-wrap gap-3 justify-center">
          <Link
            to="/signup"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-[#2563EB] font-bold rounded-xl hover:bg-[#EFF6FF] transition-all hover:-translate-y-0.5 text-base"
          >
            Get Started <span>↗</span>
          </Link>
          <Link
            to="/login"
            className="inline-flex items-center gap-2 px-8 py-4 bg-transparent text-white font-bold rounded-xl border border-white/30 hover:bg-white/10 transition-colors text-base"
          >
            Sign In
          </Link>
        </div>
      </div>
    </section>
  );
}
