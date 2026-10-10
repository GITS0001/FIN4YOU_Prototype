import { useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles } from 'lucide-react';

export default function AuthVideoPanel({
  badgeText = 'Financial Transformation',
  heading = 'From Financial Confusion to Financial Clarity.',
  subheading = 'See how scattered expenses and untracked bills transform into organized financial clarity.',
}) {
  const videoRef = useRef(null);

  useEffect(() => {
    // Attempt autoPlay reliably across modern browser security policies
    if (videoRef.current) {
      videoRef.current.defaultMuted = true;
      videoRef.current.muted = true;
      const playPromise = videoRef.current.play();
      if (playPromise !== undefined) {
        playPromise.catch(() => {
          // Auto-play was prevented by browser policy
        });
      }
    }
  }, []);

  return (
    <div className="relative w-full h-full min-h-[190px] sm:min-h-[240px] lg:min-h-full bg-[#0B0F19] text-white overflow-hidden flex flex-col justify-between">
      {/* Background Ambient Glows */}
      <div className="absolute inset-0 pointer-events-none z-10">
        <div className="absolute top-0 left-0 w-80 h-80 rounded-full blur-[100px] bg-[#2563EB]/25" />
        <div className="absolute bottom-0 right-0 w-96 h-96 rounded-full blur-[120px] bg-[#1D4ED8]/20" />
        {/* Vignette gradient overlays to ensure text readability */}
        <div className="absolute inset-x-0 top-0 h-28 bg-gradient-to-b from-[#0B0F19]/90 via-[#0B0F19]/40 to-transparent" />
        <div className="absolute inset-x-0 bottom-0 h-36 bg-gradient-to-t from-[#0B0F19]/95 via-[#0B0F19]/50 to-transparent" />
      </div>

      {/* Top Bar with Fin4You Brand */}
      <div className="relative z-20 p-4 sm:p-6 lg:p-10 flex items-center justify-between">
        <Link
          to="/"
          className="flex items-center gap-2.5 font-bold text-base sm:text-lg text-white group transition-opacity hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 rounded-lg"
        >
          <span className="w-8 h-8 sm:w-9 sm:h-9 bg-[#2563EB] text-white rounded-xl grid place-items-center font-black text-sm shadow-blue">
            F
          </span>
          <span className="tracking-tight font-display">
            Fin4<strong className="text-[#60A5FA]">You</strong>
          </span>
        </Link>

        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/15 text-[10px] sm:text-[11px] font-semibold text-blue-200">
          <Sparkles className="w-3.5 h-3.5 text-[#60A5FA]" />
          <span>{badgeText}</span>
        </div>
      </div>

      {/* Center Background Video */}
      <div className="absolute inset-0 w-full h-full flex items-center justify-center bg-[#0B0F19]">
        <video
          ref={videoRef}
          autoPlay
          muted
          loop
          playsInline
          preload="metadata"
          className="w-full h-full object-cover object-center opacity-85"
          aria-hidden="true"
        >
          <source src="/videos/fin4you-financial-transformation.mp4" type="video/mp4" />
          <source src="/videos/Video Project.mp4" type="video/mp4" />
        </video>
      </div>

      {/* Bottom Context Caption (Shows on tablet/desktop, compact on mobile) */}
      <div className="relative z-20 p-4 sm:p-6 lg:p-10 max-w-xl">
        <div className="hidden sm:inline-block mb-2">
          <span className="text-[10px] uppercase tracking-widest font-extrabold text-[#60A5FA] bg-[#2563EB]/20 px-2.5 py-1 rounded-md border border-[#2563EB]/40">
            Intelligent Personal Finance
          </span>
        </div>
        <h2 className="text-lg sm:text-2xl lg:text-3xl font-black text-white leading-tight tracking-tight drop-shadow-md font-display">
          {heading}
        </h2>
        <p className="hidden sm:block mt-2 text-xs sm:text-sm text-gray-300/90 leading-relaxed max-w-md drop-shadow">
          {subheading}
        </p>

        <div className="mt-2 sm:mt-4 flex items-center gap-2 text-[10px] sm:text-[11px] text-gray-300">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Deterministic math & verified runway</span>
        </div>
      </div>
    </div>
  );
}
