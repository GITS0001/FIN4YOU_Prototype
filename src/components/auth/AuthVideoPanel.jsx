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
    <div className="relative w-full h-full min-h-[260px] lg:min-h-full bg-[#0B0F19] text-white overflow-hidden flex flex-col justify-between">
      {/* Background Ambient Glows */}
      <div className="absolute inset-0 pointer-events-none z-10">
        <div className="absolute top-0 left-0 w-80 h-80 rounded-full blur-[100px] bg-[#2563EB]/25" />
        <div className="absolute bottom-0 right-0 w-96 h-96 rounded-full blur-[120px] bg-[#1D4ED8]/20" />
        {/* Subtle vignette gradient overlays to ensure text readability without hiding cartoon */}
        <div className="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-[#0B0F19]/90 via-[#0B0F19]/40 to-transparent" />
        <div className="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-t from-[#0B0F19]/95 via-[#0B0F19]/50 to-transparent" />
      </div>

      {/* Top Bar with Fin4You Brand */}
      <div className="relative z-20 p-6 md:p-8 lg:p-10 flex items-center justify-between">
        <Link
          to="/"
          className="flex items-center gap-2.5 font-bold text-lg text-white group transition-opacity hover:opacity-90"
        >
          <span className="w-9 h-9 bg-[#2563EB] text-white rounded-xl grid place-items-center font-black text-sm shadow-blue">
            F
          </span>
          <span className="tracking-tight">
            Fin4<strong className="text-[#60A5FA]">You</strong>
          </span>
        </Link>

        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/15 text-[11px] font-semibold text-blue-200">
          <Sparkles className="w-3.5 h-3.5 text-[#60A5FA]" />
          <span>{badgeText}</span>
        </div>
      </div>

      {/* Center Background Video (50% desktop canvas) */}
      <div className="absolute inset-0 w-full h-full flex items-center justify-center bg-[#0B0F19]">
        <video
          ref={videoRef}
          autoPlay
          muted
          loop
          playsInline
          className="w-full h-full object-cover object-center"
          aria-label="Fin4You Financial Transformation Animation"
        >
          <source src="/videos/fin4you-financial-transformation.mp4" type="video/mp4" />
          <source src="/videos/Video Project.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div>

      {/* Bottom Context Caption (Non-intrusive, clear of character) */}
      <div className="relative z-20 p-6 md:p-8 lg:p-10 max-w-xl">
        <div className="inline-block mb-2">
          <span className="text-[10px] uppercase tracking-widest font-extrabold text-[#60A5FA] bg-[#2563EB]/20 px-2.5 py-1 rounded-md border border-[#2563EB]/40">
            Intelligent Personal Finance
          </span>
        </div>
        <h2 className="text-xl sm:text-2xl lg:text-3xl font-black text-white leading-tight tracking-tight drop-shadow-md">
          {heading}
        </h2>
        <p className="mt-2 text-xs sm:text-sm text-gray-300/90 leading-relaxed max-w-md drop-shadow">
          {subheading}
        </p>

        <div className="mt-4 flex items-center gap-2 text-[11px] text-gray-400">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span>Automated clarity with Fin4You & Artha AI</span>
        </div>
      </div>
    </div>
  );
}
