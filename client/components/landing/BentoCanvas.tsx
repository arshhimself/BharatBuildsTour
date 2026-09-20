'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { 
  MessageCircle, 
  Package, 
  Wallet, 
  Share2, 
  Check, 
  ArrowRight,
  TrendingUp,
  Sparkles
} from 'lucide-react';

export function BentoCanvas() {
  return (
    <section id="product" className="relative py-24 bg-white border-t border-slate-100 overflow-hidden">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3">
          <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-600 block">
            ONE SIMPLE INTERFACE
          </span>

          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
            Everything your business<br /> needs to keep moving.
          </h2>

          <p className="text-base sm:text-lg text-slate-600 font-normal">
            Real workflows, not a dashboard full of noise.
          </p>
        </div>

        {/* Asymmetric Editorial Bento Grid */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Bento Item 1: WhatsApp -> Sales */}
          <div className="md:col-span-2 rounded-3xl border border-slate-200 bg-emerald-50/30 p-6 sm:p-8 space-y-6 flex flex-col justify-between shadow-xs hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-extrabold uppercase tracking-wider text-emerald-700">
                WHATSAPP → SALES
              </span>
              <MessageCircle className="h-5 w-5 text-emerald-600" />
            </div>

            <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">
              Make every message count.
            </h3>

            <div className="rounded-2xl border border-emerald-200/80 bg-white p-4 space-y-3 text-xs shadow-xs">
              <div className="bg-emerald-100/70 text-emerald-950 p-2.5 rounded-xl ml-auto max-w-xs text-right font-medium">
                Do you have the black kurti in M?
              </div>
              <div className="bg-slate-100 text-slate-800 p-2.5 rounded-xl mr-auto max-w-xs font-medium">
                Let me check the available stock.
              </div>
              <div className="bg-emerald-50 border border-emerald-200 text-emerald-900 p-3 rounded-xl flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Package className="h-4 w-4 text-emerald-600" />
                  <div>
                    <strong className="block text-xs font-bold">12 available</strong>
                    <span className="text-[10px] text-emerald-700">Black Kurti · all sizes</span>
                  </div>
                </div>
                <Check className="h-4 w-4 text-emerald-600 stroke-[3]" />
              </div>
            </div>
          </div>

          {/* Bento Item 2: Operation Agent Stock */}
          <div className="md:col-span-1 rounded-3xl border border-slate-200 bg-slate-50/60 p-6 sm:p-8 space-y-6 flex flex-col justify-between shadow-xs hover:shadow-md transition-shadow">
            <span className="text-[11px] font-extrabold uppercase tracking-wider text-slate-500 block">
              OPERATION AGENT
            </span>

            <div>
              <h3 className="text-xl font-extrabold text-slate-900 tracking-tight">
                Know your stock<br /> before you promise.
              </h3>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-4 space-y-3 text-xs">
              <div className="flex justify-between font-bold text-slate-900">
                <span>Black Kurti</span>
                <span className="text-emerald-600">12 available</span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full w-[80%]" />
              </div>
              <span className="text-[10px] text-slate-400 block font-mono">
                Ready to ship · Updated just now
              </span>
            </div>
          </div>

          {/* Bento Item 3: Finance Agent */}
          <div className="md:col-span-1 rounded-3xl border border-slate-200 bg-amber-50/40 p-6 sm:p-8 space-y-6 flex flex-col justify-between shadow-xs hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-extrabold uppercase tracking-wider text-amber-700">
                FINANCE AGENT
              </span>
              <Wallet className="h-6 w-6 text-amber-600" />
            </div>

            <h3 className="text-xl font-extrabold text-slate-900 tracking-tight">
              Clear numbers.<br /> Quicker decisions.
            </h3>

            <div className="rounded-2xl border border-amber-200/80 bg-white p-4 space-y-1">
              <span className="text-[10px] text-slate-500 font-medium block">
                Outstanding this week
              </span>
              <strong className="text-2xl font-extrabold text-slate-900 block">
                ₹42,500
              </strong>
              <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-600">
                <TrendingUp className="h-3 w-3" /> 8% lower than last week
              </span>
            </div>
          </div>

          {/* Bento Item 4: Social Agent */}
          <div className="md:col-span-1 rounded-3xl border border-slate-200 bg-pink-50/40 p-6 sm:p-8 space-y-6 flex flex-col justify-between shadow-xs hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-extrabold uppercase tracking-wider text-pink-700">
                SOCIAL AGENT
              </span>
              <Share2 className="h-5 w-5 text-pink-600" />
            </div>

            <h3 className="text-xl font-extrabold text-slate-900 tracking-tight">
              Turn new arrivals<br /> into attention.
            </h3>

            <div className="rounded-2xl border border-pink-200/80 bg-white p-4 space-y-2 text-xs">
              <div className="rounded-xl bg-gradient-to-tr from-pink-500 to-rose-400 p-4 text-white text-center font-extrabold text-sm tracking-wider">
                NEW ARRIVALS
              </div>
              <p className="text-[11px] font-semibold text-slate-800">
                Fresh pieces, just in. Find your new favourite this week.
              </p>
              <div className="flex gap-2 text-[10px] font-mono text-pink-600 font-bold">
                <span>#newarrivals</span>
                <span>#style</span>
              </div>
            </div>
          </div>

          {/* Bento Item 5: Sales Workflow Stepper */}
          <div className="md:col-span-1 rounded-3xl border border-slate-200 bg-indigo-50/40 p-6 sm:p-8 space-y-6 flex flex-col justify-between shadow-xs hover:shadow-md transition-shadow">
            <span className="text-[11px] font-extrabold uppercase tracking-wider text-indigo-700 block">
              SALES WORKFLOW
            </span>

            <h3 className="text-xl font-extrabold text-slate-900 tracking-tight">
              Quote → Payment → Invoice
            </h3>

            <div className="rounded-2xl border border-indigo-200/80 bg-white p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500 text-white text-xs">
                  <Check className="h-3.5 w-3.5 stroke-[3]" />
                </div>
                <div className="h-0.5 flex-1 bg-emerald-500 mx-1" />
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500 text-white text-xs">
                  <Check className="h-3.5 w-3.5 stroke-[3]" />
                </div>
                <div className="h-0.5 flex-1 bg-emerald-500 mx-1" />
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500 text-white text-xs">
                  <Check className="h-3.5 w-3.5 stroke-[3]" />
                </div>
              </div>
              <div className="flex justify-between text-[10px] text-slate-500 font-bold">
                <span>Quote sent</span>
                <span>Payment received</span>
                <span>Invoice shared</span>
              </div>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
