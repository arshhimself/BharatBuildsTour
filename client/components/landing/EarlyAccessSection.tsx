'use client';

import React from 'react';
import { Check } from 'lucide-react';
import { EarlyAccessForm } from './EarlyAccessForm';

const EARLY_INCLUDES = [
  '2 months early access',
  'Personalised onboarding',
  'Built around your workflow',
  'Priority catalog & inventory setup',
];

export function EarlyAccessSection() {
  return (
    <section id="early-access" className="relative py-24 bg-white border-t border-slate-100 overflow-hidden">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Early Access Main Card */}
        <div className="rounded-3xl border border-indigo-100 bg-gradient-to-tr from-indigo-50/70 via-blue-50/40 to-slate-50 p-8 sm:p-12 shadow-md relative overflow-hidden max-w-6xl mx-auto">
          
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
            
            {/* Left Column Copy */}
            <div className="lg:col-span-5 space-y-6">
              <span className="text-[11px] font-extrabold uppercase tracking-wider text-indigo-600 block">
                EARLY ACCESS
              </span>

              <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
                Be one of the first businesses to run with BizMate.
              </h2>

              <p className="text-base sm:text-lg text-slate-600 leading-relaxed font-normal">
                Reserve two months of early access for ₹2,000 and help shape the AI team your business actually needs.
              </p>

              {/* Includes List */}
              <div className="space-y-3 pt-2">
                {EARLY_INCLUDES.map((item) => (
                  <div key={item} className="flex items-center gap-2.5 text-xs font-bold text-slate-800">
                    <div className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-100 text-emerald-600 shrink-0">
                      <Check className="h-3 w-3 stroke-[3]" />
                    </div>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Right Column Form */}
            <div className="lg:col-span-7">
              <EarlyAccessForm />
            </div>

          </div>

        </div>

      </div>
    </section>
  );
}
