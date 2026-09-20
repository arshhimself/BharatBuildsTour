'use client';

import React from 'react';
import { Navbar } from '@/components/landing/navbar';
import { Hero } from '@/components/landing/hero';
import { FounderVideoSection } from '@/components/landing/FounderVideoSection';
import { MessageToMoneyWorkflow } from '@/components/landing/MessageToMoneyWorkflow';
import { VoiceAISection } from '@/components/landing/VoiceAISection';
import { MultiAgentSection } from '@/components/landing/MultiAgentSection';
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
        {/* Hero Section with Dual 3D iPhones & Agent Proof Strip */}
        <Hero />

        {/* Founder Story & Video Section */}
        <FounderVideoSection />

        {/* Scroll-Linked Product Story Workflow (01 Customer Message -> 08 Invoice Shared) */}
        <MessageToMoneyWorkflow />

        {/* Voice AI Engine Section */}
        <VoiceAISection />

        {/* The AI Team Architecture Map */}
        <MultiAgentSection />

        {/* One Simple Interface / Asymmetric Bento Grid */}
        <BentoCanvas />

        {/* Control Room / Manager Briefing Dashboard Mockup */}
        <ControlRoomPreview />

        {/* Primary Business Story (Local Women's Clothing Store) */}
        <WomensFashionStorySection />

        {/* A Day With BizMate Timeline */}
        <DayOneTimeline />

        {/* Early Access Prebook Section */}
        <EarlyAccessSection />

        {/* Final CTA Banner */}
        <FinalCTASection />
      </main>

      {/* Global Footer */}
      <Footer />
    </div>
  );
}
