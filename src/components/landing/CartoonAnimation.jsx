import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence, useReducedMotion } from 'motion/react';
import { Link } from 'react-router-dom';

// ─── Scene constants ──────────────────────────────────────────
const SCENES = ['confusion', 'transform', 'clarity'];

// ─── Reusable animation variants ─────────────────────────────
const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (d = 0) => ({ opacity: 1, y: 0, transition: { delay: d, duration: 0.55, ease: [0.4, 0, 0.2, 1] } }),
  exit: { opacity: 0, y: -16, transition: { duration: 0.3 } },
};

const fadeIn = {
  hidden: { opacity: 0 },
  visible: (d = 0) => ({ opacity: 1, transition: { delay: d, duration: 0.5 } }),
  exit: { opacity: 0, transition: { duration: 0.3 } },
};

// ─── Cartoon Man SVG ──────────────────────────────────────────
function CartoonMan({ expression = 'confused', scale = 1 }) {
  const isHappy = expression === 'happy';
  return (
    <svg
      width={120 * scale}
      height={160 * scale}
      viewBox="0 0 120 160"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      {/* Body */}
      <rect x="38" y="72" width="44" height="52" rx="10" fill="#2563EB" />
      {/* Collar */}
      <path d="M54 72 L60 84 L66 72" fill="#1D4ED8" />
      {/* Left arm */}
      <motion.rect
        x="20" y="74" width="20" height="10" rx="5" fill="#2563EB"
        animate={expression === 'confused'
          ? { rotate: [0, 15, -15, 10, 0], originX: '100%', originY: '50%' }
          : { rotate: 0 }}
        transition={{ repeat: expression === 'confused' ? Infinity : 0, duration: 2, ease: 'easeInOut' }}
      />
      {/* Right arm */}
      <motion.rect
        x="80" y="74" width="20" height="10" rx="5" fill="#2563EB"
        animate={expression === 'confused'
          ? { rotate: [0, -15, 15, -10, 0], originX: '0%', originY: '50%' }
          : { rotate: 0 }}
        transition={{ repeat: expression === 'confused' ? Infinity : 0, duration: 2.3, ease: 'easeInOut', delay: 0.2 }}
      />
      {/* Legs */}
      <rect x="44" y="122" width="14" height="32" rx="7" fill="#0B0F19" />
      <rect x="62" y="122" width="14" height="32" rx="7" fill="#0B0F19" />
      {/* Shoes */}
      <ellipse cx="51" cy="154" rx="10" ry="6" fill="#0B0F19" />
      <ellipse cx="69" cy="154" rx="10" ry="6" fill="#0B0F19" />
      {/* Neck */}
      <rect x="52" y="58" width="16" height="16" rx="4" fill="#FBBF24" />
      {/* Head */}
      <ellipse cx="60" cy="46" rx="26" ry="28" fill="#FBBF24" />
      {/* Hair */}
      <ellipse cx="60" cy="20" rx="24" ry="10" fill="#0B0F19" />
      {/* Eyes */}
      <motion.ellipse
        cx="48" cy="42"
        rx={isHappy ? 4 : 5} ry={isHappy ? 3 : 5}
        fill="#0B0F19"
        animate={isHappy ? {} : { scaleY: [1, 0.3, 1] }}
        transition={{ repeat: Infinity, duration: 3, delay: 1 }}
      />
      <motion.ellipse
        cx="72" cy="42"
        rx={isHappy ? 4 : 5} ry={isHappy ? 3 : 5}
        fill="#0B0F19"
        animate={isHappy ? {} : { scaleY: [1, 0.3, 1] }}
        transition={{ repeat: Infinity, duration: 3, delay: 1 }}
      />
      {/* Eyebrows */}
      {isHappy ? (
        <>
          <path d="M42 34 Q48 30 54 34" stroke="#0B0F19" strokeWidth="2.5" strokeLinecap="round" fill="none" />
          <path d="M66 34 Q72 30 78 34" stroke="#0B0F19" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        </>
      ) : (
        <>
          <path d="M42 36 Q48 31 54 35" stroke="#0B0F19" strokeWidth="2.5" strokeLinecap="round" fill="none" />
          <path d="M66 35 Q72 31 78 36" stroke="#0B0F19" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        </>
      )}
      {/* Mouth */}
      {isHappy ? (
        <path d="M48 56 Q60 66 72 56" stroke="#0B0F19" strokeWidth="2.5" strokeLinecap="round" fill="none" />
      ) : (
        <path d="M48 60 Q60 54 72 60" stroke="#0B0F19" strokeWidth="2.5" strokeLinecap="round" fill="none" />
      )}
    </svg>
  );
}

// ─── Scene A: Confusion ───────────────────────────────────────
function SceneConfusion() {
  const bubbles = [
    { text: '?', x: -90, y: -20, size: 52, delay: 0 },
    { text: '₹?', x: 80, y: -40, size: 48, delay: 0.3 },
    { text: '📊', x: -80, y: 60, size: 44, delay: 0.6 },
    { text: '💸', x: 90, y: 40, size: 44, delay: 0.2 },
    { text: '??', x: 20, y: -70, size: 40, delay: 0.8 },
  ];
  return (
    <div className="relative flex flex-col items-center justify-center min-h-[320px]">
      {bubbles.map((b, i) => (
        <motion.div
          key={i}
          className="absolute bg-white border-2 border-[#BFDBFE] rounded-full flex items-center justify-center text-[#2563EB] font-bold shadow-card select-none"
          style={{
            width: b.size,
            height: b.size,
            position: 'absolute',
            left: `calc(50% + ${b.x}px)`,
            top: `calc(50% + ${b.y}px)`,
            transform: 'translate(-50%,-50%)',
          }}
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1, y: [0, -8, 0] }}
          transition={{ delay: b.delay, duration: 0.5, y: { repeat: Infinity, duration: 2 + i * 0.3, ease: 'easeInOut', delay: b.delay } }}
        >
          <span style={{ fontSize: b.size * 0.35 }}>{b.text}</span>
        </motion.div>
      ))}
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
        className="relative z-10"
      >
        <CartoonMan expression="confused" />
      </motion.div>
    </div>
  );
}

// ─── Scene B: Transform ───────────────────────────────────────
function SceneTransform() {
  return (
    <div className="relative flex items-center justify-center gap-8 min-h-[320px]">
      <motion.div
        initial={{ x: 0 }}
        animate={{ x: -20 }}
        transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
      >
        <CartoonMan expression="confused" />
      </motion.div>

      {/* Arrow */}
      <motion.div
        className="text-[#2563EB] text-4xl font-black"
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.4, duration: 0.4 }}
      >
        →
      </motion.div>

      {/* Dashboard appearing */}
      <motion.div
        className="bg-white rounded-2xl shadow-lg border border-gray-100 p-4 w-48"
        initial={{ opacity: 0, x: 40, scale: 0.8 }}
        animate={{ opacity: 1, x: 0, scale: 1 }}
        transition={{ delay: 0.5, duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
      >
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-bold text-gray-700">Overview</span>
          <span className="text-xs text-green-600 font-semibold">● Live</span>
        </div>
        {[['Income','₹45,000','text-[#2563EB]'],['Expenses','₹28,400','text-gray-700'],['Saved','₹16,600','text-green-600']].map(([l,v,c])=>(
          <motion.div
            key={l}
            className="flex justify-between items-center py-1.5 border-b border-gray-100 last:border-0"
            initial={{ opacity: 0, x: 12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.8 + ['Income','Expenses','Saved'].indexOf(l) * 0.12 }}
          >
            <span className="text-xs text-gray-500">{l}</span>
            <span className={`text-xs font-bold ${c}`}>{v}</span>
          </motion.div>
        ))}
        <motion.div
          className="mt-3 h-1 bg-[#EFF6FF] rounded-full overflow-hidden"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
        >
          <motion.div
            className="h-full bg-[#2563EB] rounded-full"
            initial={{ width: 0 }}
            animate={{ width: '37%' }}
            transition={{ delay: 1.3, duration: 0.8 }}
          />
        </motion.div>
        <p className="text-[10px] text-gray-400 mt-1 text-center">37% savings rate</p>
      </motion.div>
    </div>
  );
}

// ─── Scene C: Clarity ─────────────────────────────────────────
function SceneClarity() {
  return (
    <div className="relative flex items-center justify-center gap-10 min-h-[320px]">
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
        className="relative"
      >
        <CartoonMan expression="happy" />
        {/* Checkmark badge */}
        <motion.div
          className="absolute -top-2 -right-2 w-8 h-8 bg-[#2563EB] rounded-full flex items-center justify-center text-white font-bold text-sm shadow-blue"
          initial={{ scale: 0 }}
          animate={{ scale: 1, rotate: [0, 10, -5, 0] }}
          transition={{ delay: 0.4, duration: 0.5, type: 'spring', stiffness: 300 }}
        >
          ✓
        </motion.div>
      </motion.div>

      {/* Full dashboard */}
      <motion.div
        className="bg-white rounded-2xl shadow-lg border border-gray-100 p-5 w-52"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
      >
        <p className="text-xs font-bold text-gray-700 mb-3">Financial Overview</p>
        <div className="flex items-end gap-1.5 h-20 mb-3">
          {[45, 62, 38, 75, 55, 88].map((h, i) => (
            <motion.div
              key={i}
              className="flex-1 bg-[#2563EB] rounded-t-sm"
              style={{ height: `${h}%`, opacity: 0.6 + i * 0.07, transformOrigin: 'bottom' }}
              initial={{ scaleY: 0 }}
              animate={{ scaleY: 1 }}
              transition={{ delay: 0.2 + i * 0.08, duration: 0.5 }}
            />
          ))}
        </div>
        <motion.div
          className="bg-[#EFF6FF] rounded-lg p-2.5"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <p className="text-[10px] font-bold text-[#2563EB]">✦ Insight</p>
          <p className="text-[10px] text-gray-600 mt-0.5">You're on track this month!</p>
        </motion.div>
      </motion.div>
    </div>
  );
}

// ─── Main CartoonAnimation component ─────────────────────────
export default function CartoonAnimation() {
  const [scene, setScene] = useState(0);
  const [auto, setAuto] = useState(true);
  const prefersReduced = useReducedMotion();
  const timerRef = useRef(null);

  const SCENE_DURATION = prefersReduced ? 0 : 4000;

  useEffect(() => {
    if (!auto || prefersReduced) return;
    timerRef.current = setInterval(() => {
      setScene(s => (s + 1) % SCENES.length);
    }, SCENE_DURATION);
    return () => clearInterval(timerRef.current);
  }, [auto, prefersReduced]);

  const goTo = (i) => {
    clearInterval(timerRef.current);
    setAuto(false);
    setScene(i);
  };

  const sceneComponents = [<SceneConfusion />, <SceneTransform />, <SceneClarity />];
  const sceneTitles = ['Financial Confusion', 'Fin4You Brings Clarity', 'Financial Clarity'];
  const sceneSubtitles = [
    'Feeling lost about where your money goes?',
    'Fin4You organises your financial information clearly.',
    'Make informed decisions with confidence.',
  ];

  return (
    <section className="py-24 bg-[#EFF6FF]" id="animation">
      <div className="max-w-[1160px] mx-auto px-6">
        <div className="text-center mb-12">
          <span className="inline-flex items-center gap-2 text-xs font-bold tracking-widest uppercase text-[#2563EB] mb-4">
            <span className="w-6 h-0.5 bg-[#2563EB] rounded" />
            See It In Action
          </span>
          <h2 className="text-3xl md:text-4xl font-black tracking-tight text-[#0B0F19] leading-tight">
            From Financial Confusion<br />
            <em className="not-italic text-[#2563EB]">to Financial Clarity.</em>
          </h2>
          <p className="text-gray-500 mt-4 max-w-lg mx-auto text-[1.02rem] leading-relaxed">
            Fin4You helps you understand your financial activity and plan with greater clarity.
          </p>
        </div>

        {/* Animation stage */}
        <div className="bg-white rounded-3xl shadow-card border border-gray-100 overflow-hidden">
          {/* Scene label bar */}
          <div className="flex border-b border-gray-100">
            {SCENES.map((s, i) => (
              <button
                key={s}
                onClick={() => goTo(i)}
                className={`flex-1 py-3 text-xs font-bold tracking-wide uppercase transition-all ${scene === i ? 'text-[#2563EB] bg-[#EFF6FF] border-b-2 border-[#2563EB]' : 'text-gray-400 hover:text-gray-600'}`}
              >
                {i + 1}. {sceneTitles[i]}
              </button>
            ))}
          </div>

          {/* Scene area */}
          <div className="relative p-8 md:p-12 min-h-[380px] flex flex-col items-center justify-center">
            <AnimatePresence mode="wait">
              <motion.div
                key={scene}
                className="w-full flex flex-col items-center"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.35 }}
              >
                {sceneComponents[scene]}
                <motion.div
                  className="text-center mt-6"
                  variants={fadeUp}
                  initial="hidden"
                  animate="visible"
                  custom={0.2}
                >
                  <h3 className="text-xl font-bold text-[#0B0F19]">{sceneTitles[scene]}</h3>
                  <p className="text-gray-500 text-sm mt-1">{sceneSubtitles[scene]}</p>
                </motion.div>
              </motion.div>
            </AnimatePresence>

            {/* Auto-play progress bar */}
            {auto && !prefersReduced && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gray-100">
                <motion.div
                  key={scene}
                  className="h-full bg-[#2563EB]"
                  initial={{ width: '0%' }}
                  animate={{ width: '100%' }}
                  transition={{ duration: SCENE_DURATION / 1000, ease: 'linear' }}
                />
              </div>
            )}
          </div>

          {/* Scene dots */}
          <div className="flex items-center justify-center gap-2 pb-5 pt-1">
            {SCENES.map((_, i) => (
              <button
                key={i}
                onClick={() => goTo(i)}
                className={`rounded-full transition-all duration-300 ${scene === i ? 'w-6 h-2 bg-[#2563EB]' : 'w-2 h-2 bg-gray-200 hover:bg-gray-300'}`}
                aria-label={`Scene ${i + 1}`}
              />
            ))}
          </div>
        </div>

        {/* CTA after animation */}
        <div className="text-center mt-10">
          <Link
            to="/signup"
            className="inline-flex items-center gap-2 px-8 py-4 bg-[#2563EB] text-white font-bold rounded-xl shadow-blue hover:bg-[#1D4ED8] transition-all hover:-translate-y-0.5 text-base"
          >
            Start Your Financial Clarity Journey <span>↗</span>
          </Link>
        </div>
      </div>
    </section>
  );
}
