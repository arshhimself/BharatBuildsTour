'use client';

import React from 'react';
import { Sparkles, ExternalLink } from 'lucide-react';
import { PremiumVideoFrame } from '@/components/landing/PremiumVideoFrame';

export function ProductMotionSection() {
  return (
    <section id="product-overview" className="scroll-mt-24 relative py-16 sm:py-24 bg-gradient-to-b from-white via-[#F8FAFF] to-white border-t border-slate-200/60 overflow-hidden">
      {/* Background Soft Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[450px] bg-gradient-to-r from-indigo-100/30 via-purple-100/30 to-blue-100/30 rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">

        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-10 sm:mb-14">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-50 border border-indigo-200/80 text-indigo-700 text-[11px] font-extrabold uppercase tracking-wider shadow-xs">
            <Sparkles className="h-3.5 w-3.5 text-indigo-600 animate-pulse" />
            <span>PRODUCT OVERVIEW</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900 leading-[1.15]">
            One conversation.<br />
            <span className="text-indigo-600">A whole business moving behind it.</span>
          </h2>

          <p className="text-base sm:text-lg text-slate-600 font-medium max-w-2xl mx-auto leading-relaxed">
            See how BizMate turns everyday customer conversations into sales, operations and follow-through.
          </p>
        </div>

        {/* 16:9 Product Theater Video Stage */}
        <div className="max-w-5xl mx-auto">
          <div className="relative p-1.5 sm:p-2.5 rounded-[32px] bg-gradient-to-b from-white via-slate-100 to-slate-200/80 border border-white/80 shadow-[0_30px_70px_rgba(30,41,59,0.12)]">
            <PremiumVideoFrame
              source="/media/BizMateLaunchVideo.mp4"
              type="mp4"
              title="One conversation. A whole business moving behind it."
              subtitle="See how BizMate turns everyday customer conversations into sales, operations and follow-through."
              label="PRODUCT OVERVIEW"
              isActive={true}
            />
          </div>

          {/* Secondary YouTube Action Link */}
          <div className="mt-5 text-center">
            <a
              href="https://youtu.be/MiKX5bY41Fo?si=TCziFyrW5hzIKnHi"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-indigo-600 transition-colors"
            >
              <span>Watch on YouTube</span>
              <ExternalLink className="h-3.5 w-3.5" />
            </a>
          </div>
        </div>

      </div>
    </section>
  );
}
