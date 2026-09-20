'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, CheckCircle2, Building2, Store, PackageCheck, TrendingUp } from 'lucide-react';

const CATEGORIES = [
  { name: 'SMEs', icon: Building2 },
  { name: 'Retailers', icon: Store },
  { name: 'Wholesalers', icon: PackageCheck },
  { name: 'Distributors', icon: TrendingUp },
  { name: 'Store Owners', icon: ShieldCheck }
];

export function PilotStoriesSection() {
  return (
    <section className="relative py-24 bg-[#F8FAFF] overflow-hidden">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Category Trust Bar */}
        <div className="text-center max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 px-4 py-1.5 text-xs font-semibold text-indigo-700">
            <ShieldCheck className="h-3.5 w-3.5 text-indigo-600" />
            <span>BUILT FOR AMBITIOUS BUSINESSES</span>
          </div>

          <h2 className="mt-6 text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900">
            Designed for Real Indian Retailers & Store Owners
          </h2>

          <p className="mt-4 text-base sm:text-lg text-slate-600 font-medium">
            Early pilot observations across apparel stores, electronics distributors, and wholesale merchants.
          </p>

          {/* Category Pills Bar */}
          <div className="mt-8 flex flex-wrap justify-center items-center gap-3">
            {CATEGORIES.map((cat, idx) => {
              const Icon = cat.icon;
              return (
                <div
                  key={idx}
                  className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-5 py-2.5 text-xs font-bold text-slate-800 shadow-sm"
                >
                  <Icon className="h-4 w-4 text-indigo-600" />
                  <span>{cat.name}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Observation Cards: Before vs After BizMate */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          
          {/* Observation 1: Sales Response Time */}
          <motion.div
            whileHover={{ y: -4 }}
            className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xl space-y-4"
          >
            <span className="text-[10px] font-extrabold uppercase tracking-wider text-indigo-600">
              Early Pilot Observation 01 — Customer Response
            </span>
            <h3 className="text-xl font-bold text-slate-900">
              Elimination of Unanswered WhatsApp Messages
            </h3>
            
            <div className="space-y-3 pt-2 text-xs">
              <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-900">
                <span className="font-bold text-rose-700 block mb-1">WITHOUT BIZMATE:</span>
                "During peak store hours, customer WhatsApp messages stay unread for 2 to 4 hours. Buyers leave for competitors."
              </div>

              <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900">
                <span className="font-bold text-emerald-700 block mb-1">WITH BIZMATE SALES AGENT:</span>
                "Every customer inquiry is answered instantly with live stock availability, price quote, and UPI payment link."
              </div>
            </div>
          </motion.div>

          {/* Observation 2: Daily Accounting & Stock Control */}
          <motion.div
            whileHover={{ y: -4 }}
            className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xl space-y-4"
          >
            <span className="text-[10px] font-extrabold uppercase tracking-wider text-indigo-600">
              Early Pilot Observation 02 — Owner Clarity
            </span>
            <h3 className="text-xl font-bold text-slate-900">
              Daily Executive Control Without Manual Bookkeeping
            </h3>
            
            <div className="space-y-3 pt-2 text-xs">
              <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-900">
                <span className="font-bold text-rose-700 block mb-1">WITHOUT BIZMATE:</span>
                "Store owner spends late evenings tallying paper slips, checking bank screenshots, and guessing remaining stock."
              </div>

              <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900">
                <span className="font-bold text-emerald-700 block mb-1">WITH BIZMATE MANAGER AGENT:</span>
                "Manager Agent sends a 30-second WhatsApp voice briefing detailing exact daily sales revenue and net margin."
              </div>
            </div>
          </motion.div>

        </div>

      </div>
    </section>
  );
}
