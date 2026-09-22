'use client';

import React from 'react';
import { Sparkles, MessageCircle, Clock3, Wallet } from 'lucide-react';
import { PremiumVideoFrame } from '@/components/landing/PremiumVideoFrame';

const FOUNDER_VIDEO_ID = 'QTemHF4NwCs';

const FOUNDER_POINTS = [
  { label: 'Less chasing', icon: Sparkles },
  { label: 'More selling', icon: MessageCircle },
  { label: 'More time to grow', icon: Clock3 },
  { label: 'Clearer decisions', icon: Wallet },
];

export function FounderVideoSection() {
  return (
    <section id="founder-story" className="scroll-mt-24 relative py-16 sm:py-24 bg-white border-t border-slate-200/60 overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[850px] h-[450px] bg-gradient-to-r from-indigo-50/40 via-purple-50/40 to-blue-50/40 rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3.5 mb-10 sm:mb-14">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-50 border border-indigo-200/80 text-indigo-700 text-[11px] font-extrabold uppercase tracking-wider shadow-xs">
            <Sparkles className="h-3.5 w-3.5 text-indigo-600 animate-pulse" />
            <span>WHY WE BUILT BIZMATE</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900 leading-[1.15]">
            We built BizMate for the businesses<br className="hidden sm:inline" /> already doing everything manually.
          </h2>

          <p className="text-base sm:text-lg text-slate-600 font-medium max-w-2xl mx-auto leading-relaxed">
            WhatsApp messages. Stock checks. Customer follow-ups. Vendor updates. Payments. Bills. Too many things to remember.
          </p>
        </div>

        {/* 16:9 Product Theater Stage for Founder Video */}
        <div className="max-w-5xl mx-auto">
          <div className="relative p-1.5 sm:p-2.5 rounded-[32px] bg-gradient-to-b from-white via-slate-100 to-slate-200/80 border border-white/80 shadow-[0_30px_70px_rgba(30,41,59,0.12)]">
            <PremiumVideoFrame
              source={FOUNDER_VIDEO_ID}
              type="youtube"
              title="Why we built BizMate"
              subtitle="The founder story behind building an AI team for everyday Indian business work."
              label="FOUNDER STORY"
              isActive={true}
            />
          </div>
        </div>

        {/* Four Points Strip */}
        <div className="mt-10 flex flex-wrap items-center justify-center gap-5 sm:gap-10 text-xs font-extrabold text-slate-700">
          {FOUNDER_POINTS.map((point) => {
            const Icon = point.icon;
            return (
              <span key={point.label} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200/60 shadow-2xs">
                <Icon className="h-4 w-4 text-indigo-600" />
                <span>{point.label}</span>
              </span>
            );
          })}
        </div>

      </div>
    </section>
  );
}
