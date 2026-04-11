import Navbar from "@/components/landing/Navbar"
import HeroSection from "@/components/landing/HeroSection"
import StatsSection from "@/components/landing/StatsSection"
import ProblemSection from "@/components/landing/ProblemSection"
import SolutionSection from "@/components/landing/SolutionSection"
import HowItWorksSection from "@/components/landing/HowItWorksSection"
import AudienceSection from "@/components/landing/AudienceSection"
import MarketSection from "@/components/landing/MarketSection"
import PricingSection from "@/components/landing/PricingSection"
import ImpactSection from "@/components/landing/ImpactSection"
import CTASection from "@/components/landing/CTASection"
import Footer from "@/components/landing/Footer"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main>
        <HeroSection />
        <StatsSection />
        <ProblemSection />
        <SolutionSection />
        <HowItWorksSection />
        <AudienceSection />
        <MarketSection />
        <PricingSection />
        <ImpactSection />
        <CTASection />
      </main>
      <Footer />
    </div>
  )
}
