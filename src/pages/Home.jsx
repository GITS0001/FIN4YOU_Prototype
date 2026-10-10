import Hero from '../components/landing/Hero';
import CartoonAnimation from '../components/landing/CartoonAnimation';
import ArthaAIShowcase from '../components/landing/ArthaAIShowcase';
import Features from '../components/landing/Features';
import HowItWorks from '../components/landing/HowItWorks';
import FAQ from '../components/landing/FAQ';
import FinalCTA from '../components/landing/FinalCTA';

export default function Home() {
  return (
    <>
      {/* Slide 1 — Make Sense of Your Money (Existing Hero) */}
      <Hero />

      {/* Slide 2 — From Financial Confusion to Financial Clarity (Animated Story) */}
      <CartoonAnimation />

      {/* Slide 3 — Artha AI — Your Personal AI Financial Assistant (Showcase) */}
      <ArthaAIShowcase />

      {/* Slide 4 — Existing Features Overview */}
      <Features />

      {/* Slide 5 — How It Works Stepper */}
      <HowItWorks />

      {/* Slide 6 — FAQ Accordion */}
      <FAQ />

      {/* Slide 7 — Final Call To Action */}
      <FinalCTA />
    </>
  );
}
