import Hero from '../components/landing/Hero';
import Features from '../components/landing/Features';
import HowItWorks from '../components/landing/HowItWorks';
import CartoonAnimation from '../components/landing/CartoonAnimation';
import FAQ from '../components/landing/FAQ';
import FinalCTA from '../components/landing/FinalCTA';

export default function Home() {
  return (
    <>
      <Hero />
      <Features />
      <HowItWorks />
      <CartoonAnimation />
      <FAQ />
      <FinalCTA />
    </>
  );
}
