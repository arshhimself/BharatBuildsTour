'use client';

import React from 'react';
import { Navbar } from '@/components/landing/navbar';
import { Hero } from '@/components/landing/hero';
import { FounderVideoSection } from '@/components/landing/FounderVideoSection';
import { ProductMotionSection } from '@/components/landing/ProductMotionSection';
import { RealProductDemosSection } from '@/components/landing/RealProductDemosSection';
import { MessageToMoneyWorkflow } from '@/components/landing/MessageToMoneyWorkflow';
import { VoiceAISection } from '@/components/landing/VoiceAISection';
import { MultiAgentSection } from '@/components/landing/MultiAgentSection';
import { AgentOfficePreviewSection } from '@/components/landing/AgentOfficePreviewSection';
import { BentoCanvas } from '@/components/landing/BentoCanvas';
import { ControlRoomPreview } from '@/components/landing/control-room-preview';
import { WomensFashionStorySection } from '@/components/landing/WomensFashionStorySection';
import { DayOneTimeline } from '@/components/landing/DayOneTimeline';
import { EarlyAccessSection } from '@/components/landing/EarlyAccessSection';
import { FinalCTASection } from '@/components/landing/FinalCTASection';
import { Footer } from '@/components/landing/Footer';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#F8FAFF] text-slate-900 font-sans overflow-x-hidden">
      {/* Floating Glass Navigation */}
      <Navbar />

      <main>
        {/* 1. Hero Section with Dual 3D iPhones & Agent Proof Strip */}
        <Hero />

        {/* 2. Founder Story & Video Section */}
        <FounderVideoSection />

        {/* 3. Product Motion Video Slot / Overview */}
        <ProductMotionSection />

        {/* 4. Real Product Demo Videos (Sales Agent, Voice AI, Social Agent) */}
        <RealProductDemosSection />

        {/* 5. Scroll-Linked Product Story Workflow (01 Customer Message -> 08 Invoice Shared) */}
        <MessageToMoneyWorkflow />

        {/* 6. Voice AI Engine Section */}
        <VoiceAISection />

        {/* 7. The AI Team Architecture Map */}
        <MultiAgentSection />

        {/* 8. Agent Office Video Preview & Product Walkthrough (Video 4) */}
        <AgentOfficePreviewSection />

        {/* 9. One Simple Interface / Asymmetric Bento Grid */}
        <BentoCanvas />

        {/* 10. Control Room / Manager Briefing Dashboard Mockup */}
        <ControlRoomPreview />

        {/* 11. Real Business Stories (Zeliora, Crodlin Tech, SA Collection, Kraft) */}
        <WomensFashionStorySection />

        {/* 12. A Day With BizMate Timeline */}
        <DayOneTimeline />

        {/* 13. Early Access Prebook Section */}
        <EarlyAccessSection />

        {/* 14. Final CTA Banner */}
        <FinalCTASection />
      </main>

      {/* Global Footer */}
      <Footer />
    </div>
  );
}
