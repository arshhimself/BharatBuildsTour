'use client';

import React, { useState } from 'react';
import { Sparkles, CheckCircle2, ArrowRight, Loader2, AlertCircle, MessageSquare } from 'lucide-react';
import { apiPost, ApiError } from '@/lib/api/client';

const BUSINESS_TYPES = [
  'Retail store',
  'Wholesaler',
  'Distributor',
  'Manufacturer',
  'Direct-to-Consumer (D2C)',
  'Other SME',
];

interface EarlyAccessFormProps {
  compact?: boolean;
}

export function EarlyAccessForm({ compact = false }: EarlyAccessFormProps) {
  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [leadMessage, setLeadMessage] = useState<string>('');

  const [formData, setFormData] = useState({
    full_name: '',
    business_name: '',
    phone: '',
    email: '',
    business_type: '',
    city: '',
    about_business: '',
    daily_whatsapp_orders: '',
  });

  const whatsappContactUrl = process.env.NEXT_PUBLIC_WHATSAPP_CONTACT_URL?.trim() || '';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (status === 'submitting') return;

    setStatus('submitting');
    setErrorMessage('');
    setLeadMessage('');

    try {
      const payload = {
        full_name: formData.full_name.trim(),
        business_name: formData.business_name.trim(),
        phone: formData.phone.trim(),
        email: formData.email.trim(),
        business_type: formData.business_type.trim(),
        city: formData.city.trim(),
        about_business: formData.about_business.trim(),
        daily_whatsapp_orders: formData.daily_whatsapp_orders.trim() || undefined,
      };

      const res = await apiPost<{ success: boolean; lead_id: string; status: string; message?: string }>(
        '/early-access/leads',
        payload
      );

      if (res.success) {
        setStatus('success');
        if (res.message) {
          setLeadMessage(res.message);
        }
      } else {
        setStatus('error');
        setErrorMessage('Something went wrong while saving your request. Please try again.');
      }
    } catch (err) {
      setStatus('error');
      if (err instanceof ApiError) {
        if (err.status === 422) {
          setErrorMessage('Please check all required fields and enter a valid email and phone number.');
        } else {
          setErrorMessage(err.message || 'Something went wrong while saving your request. Please try again.');
        }
      } else {
        setErrorMessage('Something went wrong while saving your request. Please try again.');
      }
    }
  };

  if (status === 'success') {
    return (
      <div className="bg-white rounded-3xl border border-emerald-200/80 p-6 sm:p-10 shadow-xl space-y-6">
        <div className="flex items-center gap-3">
          <div className="h-12 w-12 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 shrink-0">
            <CheckCircle2 className="h-7 w-7" />
          </div>
          <div>
            <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 border border-emerald-200 px-3 py-0.5 text-[11px] font-bold text-emerald-700">
              EARLY ACCESS REQUEST RECEIVED
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight mt-1">
              You're on the list.
            </h2>
          </div>
        </div>

        <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
          {leadMessage || (
            <>
              Thanks — your early-access request has been received. Our team will contact you on WhatsApp or email to understand your business, confirm onboarding, and share your secure ₹2,000 payment link.
            </>
          )}
        </p>

        {/* Next Steps Box */}
        <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-4">
          <span className="text-[11px] font-extrabold uppercase tracking-wider text-slate-500 block">
            NEXT STEPS
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="bg-white p-3.5 rounded-xl border border-slate-200/70 shadow-sm space-y-1">
              <span className="text-xs font-mono font-extrabold text-indigo-600">01</span>
              <h4 className="text-xs font-bold text-slate-900">Quick conversation</h4>
              <p className="text-[11px] text-slate-500">Understanding your store & workflow</p>
            </div>
            <div className="bg-white p-3.5 rounded-xl border border-slate-200/70 shadow-sm space-y-1">
              <span className="text-xs font-mono font-extrabold text-indigo-600">02</span>
              <h4 className="text-xs font-bold text-slate-900">Onboarding</h4>
              <p className="text-[11px] text-slate-500">Catalog & agent configuration</p>
            </div>
            <div className="bg-white p-3.5 rounded-xl border border-slate-200/70 shadow-sm space-y-1">
              <span className="text-xs font-mono font-extrabold text-indigo-600">03</span>
              <h4 className="text-xs font-bold text-slate-900">Secure ₹2,000 reservation</h4>
              <p className="text-[11px] text-slate-500">Pass confirmed after onboarding</p>
            </div>
          </div>
        </div>

        {/* Professional Payment Copy */}
        <div className="p-4 rounded-xl bg-indigo-50/60 border border-indigo-100 text-xs text-slate-600 leading-relaxed">
          Once we review your business details, our team will contact you for a quick onboarding conversation and share a secure payment link to confirm your early-access reservation.
        </div>

        {/* Optional WhatsApp Conversion Action */}
        {whatsappContactUrl && (
          <div className="pt-2">
            <a
              href={whatsappContactUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#25D366] hover:bg-[#128C7E] px-5 py-3 text-xs font-bold text-white shadow-md shadow-emerald-500/20 transition-all"
            >
              <MessageSquare className="h-4 w-4" />
              <span>Contact us on WhatsApp</span>
            </a>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-xl space-y-6">
      
      {/* Header & Pricing Display */}
      <div className="space-y-3 pb-4 border-b border-slate-100">
        <div className="flex items-center justify-between">
          <div className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 px-3.5 py-1 text-xs font-semibold text-indigo-700">
            <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
            <span>FOUNDER COHORT EARLY ACCESS</span>
          </div>
        </div>

        <div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Reserve Your BizMate Early Access
          </h2>
          <p className="mt-1.5 text-xs sm:text-sm text-slate-600 font-normal leading-relaxed">
            Tell us a little about your business. Our team will review your details, reach out for a quick onboarding conversation, and help you get started with BizMate.
          </p>
        </div>

        {/* Price Card */}
        <div className="mt-3 p-4 rounded-2xl bg-indigo-50/70 border border-indigo-100 flex items-center justify-between">
          <div>
            <span className="text-2xl font-extrabold text-slate-900">₹2,000</span>
            <span className="text-xs text-slate-600 font-medium block">2 months of early access</span>
          </div>
          <span className="rounded-full bg-emerald-100 border border-emerald-200 px-3 py-1 text-[11px] font-bold text-emerald-800">
            LIMITED SEATS
          </span>
        </div>
      </div>

      {/* Error Banner */}
      {status === 'error' && errorMessage && (
        <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 flex items-start gap-2.5 text-xs text-rose-700 font-medium">
          <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-rose-600" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Lead Capture Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        
        {/* Full Name & Store Name */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="full_name" className="block text-xs font-bold text-slate-700 mb-1">
              Full name <span className="text-indigo-600">*</span>
            </label>
            <input
              id="full_name"
              required
              type="text"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              placeholder="e.g. Rajesh Kumar"
              className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-xs text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all"
            />
          </div>

          <div>
            <label htmlFor="business_name" className="block text-xs font-bold text-slate-700 mb-1">
              Business / Store name <span className="text-indigo-600">*</span>
            </label>
            <input
              id="business_name"
              required
              type="text"
              value={formData.business_name}
              onChange={(e) => setFormData({ ...formData, business_name: e.target.value })}
              placeholder="e.g. Kumar Traders"
              className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-xs text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all"
            />
          </div>
        </div>

        {/* WhatsApp & Email */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="phone" className="block text-xs font-bold text-slate-700 mb-1">
              WhatsApp number <span className="text-indigo-600">*</span>
            </label>
            <input
              id="phone"
              required
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              placeholder="e.g. +91 98765 43210"
              className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-xs text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all"
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-xs font-bold text-slate-700 mb-1">
              Email address <span className="text-indigo-600">*</span>
            </label>
            <input
              id="email"
              required
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="e.g. rajesh@kumartraders.com"
              className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-xs text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all"
            />
          </div>
        </div>

        {/* Business Type & City */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="business_type" className="block text-xs font-bold text-slate-700 mb-1">
              Business type <span className="text-indigo-600">*</span>
            </label>
            <select
              id="business_type"
              required
              value={formData.business_type}
              onChange={(e) => setFormData({ ...formData, business_type: e.target.value })}
              className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-xs text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all bg-white"
            >
              <option value="" disabled>Select business type</option>
              {BUSINESS_TYPES.map((bt) => (
                <option key={bt} value={bt}>{bt}</option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="city" className="block text-xs font-bold text-slate-700 mb-1">
              City <span className="text-indigo-600">*</span>
            </label>
            <input
              id="city"
              required
              type="text"
              value={formData.city}
              onChange={(e) => setFormData({ ...formData, city: e.target.value })}
              placeholder="e.g. Mumbai"
              className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-xs text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all"
            />
          </div>
        </div>

        {/* Tell us about your business */}
        <div>
          <label htmlFor="about_business" className="block text-xs font-bold text-slate-700 mb-1">
            Tell us about your business <span className="text-indigo-600">*</span>
          </label>
          <textarea
            id="about_business"
            required
            rows={3}
            value={formData.about_business}
            onChange={(e) => setFormData({ ...formData, about_business: e.target.value })}
            placeholder="Describe what products you sell, your current customer flow, and how your team operates..."
            className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-xs text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all resize-none"
          />
        </div>

        {/* Optional Daily WhatsApp Orders */}
        <div>
          <label htmlFor="daily_whatsapp_orders" className="block text-xs font-bold text-slate-700 mb-1">
            Approx. WhatsApp orders / enquiries per day <span className="text-slate-400 font-normal">(Optional)</span>
          </label>
          <input
            id="daily_whatsapp_orders"
            type="text"
            value={formData.daily_whatsapp_orders}
            onChange={(e) => setFormData({ ...formData, daily_whatsapp_orders: e.target.value })}
            placeholder="e.g. 20–30 customer enquiries/orders"
            className="w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-xs text-slate-900 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-600/20 outline-none transition-all"
          />
        </div>

        {/* Submit CTA Button */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={status === 'submitting'}
            className="w-full flex items-center justify-center gap-2 rounded-xl bg-[#25D366] hover:bg-[#128C7E] py-3.5 text-sm font-bold text-white shadow-md shadow-emerald-500/20 transition-all transform active:scale-[0.99] disabled:opacity-75 disabled:cursor-not-allowed cursor-pointer"
          >
            {status === 'submitting' ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Submitting request...</span>
              </>
            ) : (
              <>
                <span>Reserve My Early Access</span>
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        </div>

        <p className="text-[11px] text-center text-slate-500 pt-1 font-medium">
          Our team will contact you for a quick business-fit conversation before sharing your payment link.
        </p>
      </form>
    </div>
  );
}
