'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowRight, Play } from 'lucide-react';

export function FinalCTASection() {
  return (
    <section className="relative py-24 bg-[#F8FAFF] border-t border-slate-100 overflow-hidden">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        <div className="text-center max-w-3xl mx-auto space-y-6">
          <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-600 block">
            THE NEXT VERSION OF YOUR BUSINESS
          </span>

          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
            Your customers already talk to your business.<br />
            <span className="text-indigo-600">Now let your business talk back.</span>
          </h2>

          <p className="text-base sm:text-lg text-slate-600 leading-relaxed font-normal max-w-2xl mx-auto">
            Give customers a Sales Agent. Give yourself a Manager Agent. Let the specialists handle the rest.
          </p>

          <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              href="/early-access"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-full bg-[#25D366] px-7 py-3.5 text-sm font-bold text-white shadow-md shadow-emerald-500/20 hover:bg-[#128C7E] transition-all transform hover:scale-[1.02]"
            >
              <span>Reserve early access</span>
              <ArrowRight className="h-4 w-4" />
            </Link>

            <a
              href="/#product"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-full bg-white border border-slate-300 px-6 py-3.5 text-sm font-bold text-slate-800 shadow-xs hover:bg-slate-50 transition-colors"
            >
              <Play className="h-4 w-4 fill-current ml-0.5 text-slate-900" />
              <span>Watch founder story</span>
            </a>
          </div>
        </div>

      </div>
    </section>
  );
}
