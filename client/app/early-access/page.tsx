'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  ArrowRight, 
  CheckCircle2, 
  ShieldCheck, 
  ArrowLeft,
  Building2,
  Phone,
  User,
  MapPin,
  Store,
  CreditCard,
  Check
} from 'lucide-react';
import { Navbar } from '@/components/landing/navbar';
import { Footer } from '@/components/landing/Footer';

export default function EarlyAccessPage() {
  const [formData, setFormData] = useState({
    name: '',
    storeName: '',
    phone: '',
    category: 'Women Apparel & Fashion',
    city: ''
  });

  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.name && formData.storeName && formData.phone) {
      setSubmitted(true);
    }
  };

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
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
          
          {/* Left Column: Form / Confirmation */}
          <div className="lg:col-span-7 bg-white rounded-3xl border border-slate-200 p-6 sm:p-10 shadow-xl">
            {!submitted ? (
              <div>
                <div className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 px-3.5 py-1 text-xs font-semibold text-indigo-700 mb-4">
                  <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
                  <span>EARLY ACCESS RESERVATION</span>
                </div>

                <h1 className="text-2xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
                  Reserve Your Founder Pass — ₹2,000
                </h1>

                <p className="mt-2 text-xs sm:text-sm text-slate-600">
                  Fill in your store details below to lock your priority onboarding slot.
                </p>

                <form onSubmit={handleSubmit} className="mt-8 space-y-4">
                  {/* Full Name */}
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Your Full Name
                    </label>
                    <div className="relative">
                      <User className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                      <input
                        type="text"
                        required
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        placeholder="e.g. Ramesh Kumar"
                        className="w-full rounded-xl border border-slate-300 pl-10 pr-4 py-2.5 text-sm text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all"
                      />
                    </div>
                  </div>

                  {/* Business / Store Name */}
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Store / Business Name
                    </label>
                    <div className="relative">
                      <Store className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                      <input
                        type="text"
                        required
                        value={formData.storeName}
                        onChange={(e) => setFormData({ ...formData, storeName: e.target.value })}
                        placeholder="e.g. Unique Fashion Store"
                        className="w-full rounded-xl border border-slate-300 pl-10 pr-4 py-2.5 text-sm text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all"
                      />
                    </div>
                  </div>

                  {/* WhatsApp Phone Number */}
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      WhatsApp Phone Number
                    </label>
                    <div className="relative">
                      <Phone className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                      <input
                        type="tel"
                        required
                        value={formData.phone}
                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                        placeholder="e.g. +91 98765 43210"
                        className="w-full rounded-xl border border-slate-300 pl-10 pr-4 py-2.5 text-sm text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all"
                      />
                    </div>
                  </div>

                  {/* Business Category */}
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Primary Business Category
                    </label>
                    <select
                      value={formData.category}
                      onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                      className="w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all bg-white"
                    >
                      <option>Women Apparel & Fashion</option>
                      <option>Men Retail & Clothing</option>
                      <option>Electronics & Hardware</option>
                      <option>Grocery & FMCG Wholesale</option>
                      <option>General Retail Store</option>
                    </select>
                  </div>

                  {/* City */}
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      City
                    </label>
                    <div className="relative">
                      <MapPin className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                      <input
                        type="text"
                        required
                        value={formData.city}
                        onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                        placeholder="e.g. New Delhi / Jaipur / Mumbai"
                        className="w-full rounded-xl border border-slate-300 pl-10 pr-4 py-2.5 text-sm text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all"
                      />
                    </div>
                  </div>

                  {/* Submit Button */}
                  <div className="pt-4">
                    <button
                      type="submit"
                      className="w-full flex items-center justify-center gap-2 rounded-xl bg-indigo-600 py-3.5 text-sm font-bold text-white shadow-lg shadow-indigo-600/30 hover:bg-indigo-700 transition-all transform hover:scale-[1.01]"
                    >
                      <CreditCard className="h-4 w-4" />
                      <span>Proceed to Reserve — ₹2,000</span>
                    </button>
                  </div>
                </form>
              </div>
            ) : (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center py-8 space-y-5"
              >
                <div className="mx-auto h-16 w-16 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center">
                  <Check className="h-10 w-10 stroke-[3]" />
                </div>
                <h2 className="text-2xl font-extrabold text-slate-900">
                  Reservation Details Recorded
                </h2>
                <p className="text-sm text-slate-600 max-w-md mx-auto">
                  Thank you, <strong className="text-slate-900">{formData.name}</strong>. We have registered <strong className="text-slate-900">{formData.storeName}</strong> ({formData.city}) for Priority Batch 1 Onboarding.
                </p>

                <div className="p-4 rounded-2xl bg-indigo-50 border border-indigo-200 text-left text-xs space-y-2 text-slate-700">
                  <div className="flex justify-between font-bold">
                    <span>Reservation ID:</span>
                    <span className="text-indigo-600">BM-EARLY-9042</span>
                  </div>
                  <div className="flex justify-between">
                    <span>WhatsApp Contact:</span>
                    <span>{formData.phone}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Deposit Status:</span>
                    <span className="text-amber-600 font-bold">Payment Authorization Pending</span>
                  </div>
                </div>

                <div className="pt-2">
                  <a
                    href={process.env.NEXT_PUBLIC_EARLY_ACCESS_PAYMENT_URL || "#"}
                    target={process.env.NEXT_PUBLIC_EARLY_ACCESS_PAYMENT_URL ? "_blank" : "_self"}
                    rel="noreferrer"
                    className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-6 py-3 text-xs font-bold text-white shadow-md hover:bg-emerald-500 transition-colors"
                  >
                    <CreditCard className="h-4 w-4" />
                    <span>Complete ₹2,000 Payment Authorization</span>
                  </a>
                </div>

                <p className="text-xs text-slate-500">
                  Our engineering team will contact you on WhatsApp ({formData.phone}) to verify payment authorization and initiate catalog setup.
                </p>

                <div>
                  <Link
                    href="/"
                    className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 hover:text-indigo-600 transition-colors"
                  >
                    Return to Homepage
                  </Link>
                </div>
              </motion.div>
            )}
          </div>

          {/* Right Column: Benefits Checklist */}
          <div className="lg:col-span-5 space-y-6">
            <div className="rounded-3xl border border-slate-900 bg-slate-950 p-6 sm:p-8 text-white space-y-6">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-amber-400" />
                <span>Founder Cohort Privileges</span>
              </h3>

              <ul className="space-y-4 text-xs text-slate-300">
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span><strong>1-on-1 Onboarding:</strong> Direct WhatsApp setup session with BizMate engineers.</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span><strong>Catalog & Inventory Sync:</strong> We help import your stock lists and price sheets.</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span><strong>Locked Founder Pricing:</strong> Lock in ₹2,000 deposit towards your first year subscription.</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span><strong>All 5 Agents Included:</strong> Manager, Sales, Finance, Social, and Operation Agents.</span>
                </li>
              </ul>

              <div className="pt-4 border-t border-slate-800 text-[11px] text-slate-400 flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-emerald-400 shrink-0" />
                <span>100% money-back guarantee if not fully satisfied during onboarding.</span>
              </div>
            </div>
          </div>

        </div>

      </main>

      <Footer />
    </div>
  );
}
