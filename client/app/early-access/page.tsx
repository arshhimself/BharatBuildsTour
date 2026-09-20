'use client';

import React from 'react';
import Link from 'next/link';
import { 
  Sparkles, 
  ArrowLeft,
  CreditCard,
  CheckCircle2,
  Clock,
  ShieldCheck
} from 'lucide-react';
import { Navbar } from '@/components/landing/navbar';
import { Footer } from '@/components/landing/Footer';

export default function EarlyAccessPage() {
  const paymentUrl = process.env.NEXT_PUBLIC_EARLY_ACCESS_PAYMENT_URL?.trim() || '';

  return (
    <div className="min-h-screen bg-[#F8FAFF] text-slate-900 font-sans flex flex-col justify-between">
      <Navbar />

      <main className="pt-28 pb-20 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto w-full flex-1">
        
        {/* Back Link */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 hover:text-indigo-600 transition-colors mb-6"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to BizMate Home</span>
        </Link>

        {/* Main Content Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
          
          {/* Left Column: Early Access Pass Reservation */}
          <div className="lg:col-span-7 bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-xl flex flex-col justify-between">
            <div className="space-y-6">
              <div>
                <div className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 px-3.5 py-1 text-xs font-semibold text-indigo-700 mb-3">
                  <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
                  <span>FOUNDER COHORT BATCH 1</span>
                </div>

                <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                  Reserve Your Founder Pass — ₹2,000
                </h1>

                <p className="mt-2 text-xs sm:text-sm text-slate-600 font-normal leading-relaxed">
                  Join the exclusive founder cohort to receive 2 months of full early access, priority catalog setup, and 1-on-1 onboarding with the BizMate engineering team.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-indigo-50/70 border border-indigo-100 space-y-3">
                <div className="flex items-center justify-between text-xs font-bold text-slate-900">
                  <span>Founder Pass Deposit:</span>
                  <span className="text-indigo-600 text-sm font-extrabold">₹2,000</span>
                </div>
                <div className="flex items-center justify-between text-xs text-slate-600">
                  <span>Early Access Period:</span>
                  <span className="font-semibold text-slate-900">2 Months Full Access</span>
                </div>
                <div className="flex items-center justify-between text-xs text-slate-600">
                  <span>Priority Onboarding:</span>
                  <span className="font-semibold text-emerald-600 flex items-center gap-1">
                    <CheckCircle2 className="h-3.5 w-3.5" /> Guaranteed Batch 1
                  </span>
                </div>
              </div>

              <div className="space-y-3 text-xs text-slate-600">
                <div className="flex items-start gap-2.5">
                  <ShieldCheck className="h-4 w-4 text-indigo-600 shrink-0 mt-0.5" />
                  <span>Deposit applied directly toward your initial subscription upon launch.</span>
                </div>
                <div className="flex items-start gap-2.5">
                  <Clock className="h-4 w-4 text-indigo-600 shrink-0 mt-0.5" />
                  <span>Early access onboarding slots are limited to ensure 1-on-1 setup quality.</span>
                </div>
              </div>

              <div className="pt-2">
                {paymentUrl ? (
                  <a
                    href={paymentUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="w-full flex items-center justify-center gap-2 rounded-xl bg-[#25D366] py-3.5 text-sm font-bold text-white shadow-md shadow-emerald-500/20 hover:bg-[#128C7E] transition-all transform hover:scale-[1.01] cursor-pointer"
                  >
                    <CreditCard className="h-4 w-4" />
                    <span>Reserve Early Access — ₹2,000</span>
                  </a>
                ) : (
                  <button
                    type="button"
                    disabled
                    className="w-full flex items-center justify-center gap-2 rounded-xl bg-[#25D366] py-3.5 text-sm font-bold text-white shadow-md shadow-emerald-500/20 opacity-95 cursor-default"
                  >
                    <CreditCard className="h-4 w-4" />
                    <span>Reserve Early Access — ₹2,000</span>
                  </button>
                )}
                <p className="text-[11px] text-center text-slate-500 mt-2.5 font-medium">
                  Early access is opening soon. Priority slots reserved in order of entry.
                </p>
              </div>
            </div>

            <div className="pt-6 border-t border-slate-100 mt-6 text-center">
              <Link
                href="/"
                className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-600 hover:text-indigo-600 transition-colors"
              >
                Return to Homepage
              </Link>
            </div>
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
                      1-on-1 onboarding
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5 leading-relaxed font-normal">
                      Direct WhatsApp setup session with the BizMate team.
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
                      Founder pricing
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5 leading-relaxed font-normal">
                      Your ₹2,000 reservation is applied according to the offer terms.
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
                      AI team access
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5 leading-relaxed font-normal">
                      Manager, Sales, Finance, Social and Operation Agents included.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Bottom Subtle Visual — BizMate AI Team Mini Bar */}
            <div className="pt-4 border-t border-slate-100 mt-4 space-y-2">
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
