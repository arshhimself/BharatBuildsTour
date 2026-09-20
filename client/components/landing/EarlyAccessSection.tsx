'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Check, ArrowRight, Sparkles } from 'lucide-react';

const EARLY_INCLUDES = [
  '2 months early access',
  'Personalised onboarding',
  'Built around your workflow',
];

export function EarlyAccessSection() {
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    businessName: '',
    email: '',
    phone: '',
    city: '',
    businessType: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.name && formData.businessName && formData.phone) {
      setSubmitted(true);
    }
  };

  return (
    <section id="early-access" className="relative py-24 bg-white border-t border-slate-100 overflow-hidden">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Early Access Main Card */}
        <div className="rounded-3xl border border-indigo-100 bg-gradient-to-tr from-indigo-50/70 via-blue-50/40 to-slate-50 p-8 sm:p-12 shadow-md relative overflow-hidden max-w-5xl mx-auto">
          
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
            
            {/* Left Column Copy */}
            <div className="lg:col-span-6 space-y-6">
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

            {/* Right Column Prebook Form Card */}
            <div className="lg:col-span-6">
              <div className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xl">
                {!submitted ? (
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="flex items-baseline justify-between pb-2 border-b border-slate-100">
                      <div>
                        <strong className="text-3xl font-extrabold text-slate-900">₹2,000</strong>
                        <span className="text-xs text-slate-500 font-medium block">2 months of early access</span>
                      </div>
                      <span className="rounded-full bg-indigo-50 px-3 py-1 text-[10px] font-extrabold text-indigo-600">
                        LIMITED SEATS
                      </span>
                    </div>

                    <div>
                      <input
                        required
                        type="text"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        placeholder="Full name"
                        className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-xs text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all"
                      />
                    </div>

                    <div>
                      <input
                        required
                        type="text"
                        value={formData.businessName}
                        onChange={(e) => setFormData({ ...formData, businessName: e.target.value })}
                        placeholder="Business name"
                        className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-xs text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all"
                      />
                    </div>

                    <div>
                      <input
                        required
                        type="email"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        placeholder="Work email"
                        className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-xs text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <input
                        required
                        type="tel"
                        value={formData.phone}
                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                        placeholder="Phone / WhatsApp"
                        className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-xs text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all"
                      />
                      <input
                        required
                        type="text"
                        value={formData.city}
                        onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                        placeholder="City"
                        className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-xs text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all"
                      />
                    </div>

                    <div>
                      <select
                        required
                        value={formData.businessType}
                        onChange={(e) => setFormData({ ...formData, businessType: e.target.value })}
                        className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-xs text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all bg-white"
                      >
                        <option value="" disabled>Business type</option>
                        <option value="Retail store">Retail store</option>
                        <option value="Wholesaler">Wholesaler</option>
                        <option value="Distributor">Distributor</option>
                        <option value="Other SME">Other SME</option>
                      </select>
                    </div>

                    <button
                      type="submit"
                      className="w-full flex items-center justify-center gap-2 rounded-xl bg-indigo-600 py-3 text-xs font-bold text-white shadow-md hover:bg-indigo-700 transition-all transform hover:scale-[1.01] cursor-pointer"
                    >
                      <span>Reserve my early-access slot</span>
                      <ArrowRight className="h-4 w-4" />
                    </button>

                    <small className="text-[10px] text-slate-400 text-center block font-medium">
                      We'll capture your details before the payment step.
                    </small>
                  </form>
                ) : (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="text-center py-6 space-y-4"
                  >
                    <div className="mx-auto h-12 w-12 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center">
                      <Check className="h-7 w-7 stroke-[3]" />
                    </div>
                    <h3 className="text-xl font-extrabold text-slate-900">
                      You're on the list.
                    </h3>
                    <p className="text-xs text-slate-600 max-w-xs mx-auto">
                      Thank you, <strong>{formData.name}</strong>. We'll be in touch with the next step for your early-access reservation for <strong>{formData.businessName}</strong>.
                    </p>

                    <Link
                      href="/early-access"
                      className="inline-flex items-center gap-1.5 text-xs font-bold text-indigo-600 hover:text-indigo-700"
                    >
                      <span>Proceed to Full Reservation Portal</span>
                      <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                  </motion.div>
                )}
              </div>
            </div>

          </div>

        </div>

      </div>
    </section>
  );
}
