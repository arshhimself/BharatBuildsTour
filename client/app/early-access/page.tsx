'use client';

import React from 'react';
import Link from 'next/link';
import { 
  Sparkles, 
  ArrowLeft
} from 'lucide-react';
import { Navbar } from '@/components/landing/navbar';
import { Footer } from '@/components/landing/Footer';
import { EarlyAccessForm } from '@/components/landing/EarlyAccessForm';

export default function EarlyAccessPage() {
  return (
    <div className="min-h-screen bg-[#F8FAFF] text-slate-900 font-sans flex flex-col justify-between">
      <Navbar />

      <main className="pt-28 pb-20 px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto w-full flex-1">
        
        {/* Back Link */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 hover:text-indigo-600 transition-colors mb-6"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to BizMate Home</span>
        </Link>

        {/* Main Content Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Left Column: Early Access Form */}
          <div className="lg:col-span-7">
            <EarlyAccessForm />
          </div>

          {/* Right Column: Benefits Panel */}
          <div className="lg:col-span-5 bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-xl flex flex-col justify-between">
            <div className="space-y-5">
              {/* Header */}
              <div>
                <div className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 px-3.5 py-1 text-xs font-semibold text-indigo-700 mb-3">
                  <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
                  <span>EARLY ACCESS INCLUDES</span>
                </div>
                <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                  More Than Early Access
                </h2>
                <p className="text-xs sm:text-sm text-slate-600 font-normal mt-1.5 leading-relaxed">
                  Get hands-on onboarding and help setting up BizMate around the way your business actually works.
                </p>
              </div>

              {/* 4 Benefit Rows */}
              <div className="space-y-3 pt-1">
                {/* Row 01 */}
                <div className="group flex items-start gap-3.5 p-2.5 rounded-2xl transition-all duration-200 hover:bg-slate-50 border border-slate-100/80">
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-indigo-600 font-mono text-xs font-extrabold border border-indigo-100 transition-colors group-hover:bg-[#25D366]/15 group-hover:text-[#128C7E] group-hover:border-[#25D366]/30">
                    01
                  </div>
                  <div>
                    <h3 className="text-xs sm:text-sm font-bold text-slate-900">
                      1-on-1 onboarding conversation
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5 leading-relaxed font-normal">
                      Direct WhatsApp setup session with the BizMate engineering team.
                    </p>
                  </div>
                </div>

                {/* Row 02 */}
                <div className="group flex items-start gap-3.5 p-2.5 rounded-2xl transition-all duration-200 hover:bg-slate-50 border border-slate-100/80">
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-indigo-600 font-mono text-xs font-extrabold border border-indigo-100 transition-colors group-hover:bg-[#25D366]/15 group-hover:text-[#128C7E] group-hover:border-[#25D366]/30">
                    02
                  </div>
                  <div>
                    <h3 className="text-xs sm:text-sm font-bold text-slate-900">
                      Catalog & inventory setup
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5 leading-relaxed font-normal">
                      We'll help organize your products, stock and pricing data.
                    </p>
                  </div>
                </div>

                {/* Row 03 */}
                <div className="group flex items-start gap-3.5 p-2.5 rounded-2xl transition-all duration-200 hover:bg-slate-50 border border-slate-100/80">
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-indigo-600 font-mono text-xs font-bold border border-indigo-100 transition-colors group-hover:bg-[#25D366]/15 group-hover:text-[#128C7E] group-hover:border-[#25D366]/30">
                    03
                  </div>
                  <div>
                    <h3 className="text-xs sm:text-sm font-bold text-slate-900">
                      Founder pricing reservation
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5 leading-relaxed font-normal">
                      Your ₹2,000 reservation secures 2 months of early access.
                    </p>
                  </div>
                </div>

                {/* Row 04 */}
                <div className="group flex items-start gap-3.5 p-2.5 rounded-2xl transition-all duration-200 hover:bg-slate-50 border border-slate-100/80">
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-indigo-600 font-mono text-xs font-bold border border-indigo-100 transition-colors group-hover:bg-[#25D366]/15 group-hover:text-[#128C7E] group-hover:border-[#25D366]/30">
                    04
                  </div>
                  <div>
                    <h3 className="text-xs sm:text-sm font-bold text-slate-900">
                      Full AI team access
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5 leading-relaxed font-normal">
                      Manager, Sales, Finance, Social and Operation Agents included.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Bottom Subtle Visual — BizMate AI Team Mini Bar */}
            <div className="pt-4 border-t border-slate-100 mt-6 space-y-2">
              <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400 block">
                INCLUDED AI AGENTS
              </span>
              <div className="flex flex-wrap gap-1.5">
                {['Manager', 'Sales', 'Finance', 'Social', 'Operation'].map((agent) => (
                  <span
                    key={agent}
                    className="inline-flex items-center gap-1.5 rounded-full bg-slate-50 border border-slate-200/80 px-2.5 py-1 text-[11px] font-semibold text-slate-700"
                  >
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                    <span>{agent}</span>
                  </span>
                ))}
              </div>
            </div>
          </div>

        </div>

      </main>

      <Footer />
    </div>
  );
}
