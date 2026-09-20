'use client';

import React from 'react';
import { Check, MessageCircle } from 'lucide-react';

const STORY_POINTS = [
  'Customer orders',
  'Stock & size variants',
  'Social content',
  'Payment follow-ups',
];

export function WomensFashionStorySection() {
  return (
    <section id="stories" className="relative py-24 bg-white border-t border-slate-100 overflow-hidden">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3">
          <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-600 block">
            BUILT AROUND REAL WORK
          </span>

          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
            Built around the way<br /> real businesses actually work.
          </h2>

          <p className="text-base sm:text-lg text-slate-600 font-normal max-w-2xl mx-auto">
            BizMate is being shaped with owners who sell, follow up, source and grow through everyday conversations.
          </p>
        </div>

        {/* Story Feature Layout */}
        <div className="mt-16 grid grid-cols-1 lg:grid-cols-12 gap-10 items-center max-w-5xl mx-auto">
          
          {/* Left Store Graphic Visual */}
          <div className="lg:col-span-6">
            <div className="relative rounded-3xl border border-amber-200/80 bg-gradient-to-tr from-amber-100/60 via-amber-50 to-orange-100/50 p-8 sm:p-12 shadow-sm overflow-hidden flex flex-col justify-between min-h-[320px]">
              
              {/* Sun Light Effect */}
              <div className="absolute top-4 right-4 w-28 h-28 bg-amber-300/40 rounded-full blur-2xl pointer-events-none" />

              {/* Racks & Store Graphics Mockup */}
              <div className="space-y-4 my-auto">
                <div className="flex gap-3 justify-center">
                  <div className="w-16 h-24 rounded-2xl bg-amber-200/70 border border-amber-300" />
                  <div className="w-20 h-28 rounded-2xl bg-orange-200/70 border border-orange-300" />
                  <div className="w-16 h-24 rounded-2xl bg-amber-200/70 border border-amber-300" />
                </div>
              </div>

              {/* Floating Order Notification Card */}
              <div className="relative z-10 self-end rounded-2xl border border-slate-200 bg-white p-3.5 shadow-lg flex items-center gap-3 text-xs max-w-xs">
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-emerald-500 text-white shrink-0">
                  <MessageCircle className="h-4 w-4" />
                </div>
                <div>
                  <strong className="text-slate-900 block font-bold text-xs">New order received</strong>
                  <span className="text-slate-500 text-[11px] font-medium">10 black kurtis · ₹3,850</span>
                </div>
              </div>

            </div>
          </div>

          {/* Right Copy Content */}
          <div className="lg:col-span-6 space-y-6">
            <span className="text-[11px] font-extrabold uppercase tracking-wider text-indigo-600 block">
              LOCAL WOMEN'S CLOTHING STORE
            </span>

            <h3 className="text-2xl sm:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">
              More time with customers.<br />
              <span className="text-indigo-600">Less time hunting for answers.</span>
            </h3>

            <p className="text-sm sm:text-base text-slate-600 leading-relaxed font-normal">
              A WhatsApp-heavy business with new arrivals, size variants, vendor updates, payments and follow-ups — all moving at once.
            </p>

            {/* Checklist Grid */}
            <div className="grid grid-cols-2 gap-3 pt-2">
              {STORY_POINTS.map((point) => (
                <div key={point} className="flex items-center gap-2 text-xs font-bold text-slate-800">
                  <div className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-100 text-emerald-600 shrink-0">
                    <Check className="h-3 w-3 stroke-[3]" />
                  </div>
                  <span>{point}</span>
                </div>
              ))}
            </div>

            <div className="pt-2">
              <span className="text-[11px] text-slate-400 font-mono italic block">
                Example story · Owner identity anonymized
              </span>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
