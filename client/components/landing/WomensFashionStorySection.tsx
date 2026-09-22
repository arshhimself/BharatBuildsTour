'use client';

import React from 'react';
import { ArrowUpRight, CheckCircle2, ShieldCheck, Sparkles, MessageSquare, FileText, ArrowRight, ShoppingBag, MapPin } from 'lucide-react';

interface BusinessStory {
  id: string;
  name: string;
  category: string;
  website?: string;
  logo: string;
  tag: string;
  description: string;
  highlights: string[];
}

const REAL_BUSINESSES: BusinessStory[] = [
  {
    id: 'zeliora',
    name: 'Zeliora',
    category: 'Jewellery / D2C Retail',
    website: 'https://www.zeliora.in/',
    logo: '/businesses/zeliora-logo.jpg',
    tag: 'BUSINESS IN THE BIZMATE STORY',
    description:
      'Shaping real-time customer support, order management, and multi-channel inquiry workflows for D2C retail operations.',
    highlights: [
      'Order & Catalog Workflows',
      'High-Touch Customer Communication',
      'Real-Time Inquiry Management',
    ],
  },
  {
    id: 'crodlin-tech',
    name: 'Crodlin Tech',
    category: 'Software / Technology',
    website: 'https://www.crodlin.in/',
    logo: '/businesses/crodlin-logo.jpg',
    tag: 'BUSINESS IN THE BIZMATE STORY',
    description:
      'Streamlining client operations, service requests, and operational team coordination through conversational intelligence.',
    highlights: [
      'Client Operational Sync',
      'Automated Workflow Routing',
      'Multi-Agent Coordination',
    ],
  },
];

const SA_COLLECTION_STEPS = [
  { label: 'WhatsApp Inquiry' },
  { label: 'Sales Agent' },
  { label: 'Stock / Availability' },
  { label: 'Instant Quote' },
  { label: 'Payment Collected' },
];

const KRAFT_STEPS = [
  { label: 'IndiaMART Enquiry' },
  { label: 'WhatsApp Conversation' },
  { label: 'Sales Agent Requirement' },
  { label: 'Product Specs Check' },
  { label: 'Instant Quote' },
  { label: 'Follow-up' },
];

export function WomensFashionStorySection() {
  return (
    <section id="stories" className="relative py-24 bg-[#F8FAFF] border-t border-slate-200/60 overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-0 inset-x-0 h-40 bg-gradient-to-b from-white to-transparent pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] bg-indigo-50/50 rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">

        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-700 text-[11px] font-extrabold uppercase tracking-wider">
            <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
            <span>BUILT WITH REAL BUSINESSES</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900 leading-tight">
            Real businesses.<br />
            <span className="text-indigo-600">Real workflows.</span> Real conversations.
          </h2>

          <p className="text-base sm:text-lg text-slate-600 font-normal max-w-2xl mx-auto leading-relaxed">
            BizMate is being shaped alongside businesses that sell, serve customers
            and run their operations every day.
          </p>
        </div>

        {/* Business Grid 1: Zeliora & Crodlin Tech */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {REAL_BUSINESSES.map((business) => (
            <div
              key={business.id}
              className="group relative bg-white rounded-3xl border border-slate-200/80 p-6 sm:p-8 shadow-sm hover:shadow-xl hover:shadow-indigo-500/5 transition-all duration-300 hover:-translate-y-1 flex flex-col justify-between"
            >
              <div className="space-y-6">
                {/* Header Row: Logo & Status Tag */}
                <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-100">
                  <div className="relative h-14 w-40 rounded-xl overflow-hidden bg-slate-950 p-2.5 flex items-center justify-center border border-slate-800 shadow-inner">
                    <img
                      src={business.logo}
                      alt={`${business.name} logo`}
                      className="max-h-full max-w-full object-contain transition-transform duration-300 group-hover:scale-105"
                    />
                  </div>
                  <span className="inline-block bg-slate-100 text-slate-700 text-[10px] font-bold tracking-wider uppercase px-3 py-1.5 rounded-full border border-slate-200/80">
                    {business.tag}
                  </span>
                </div>

                {/* Business Info */}
                <div>
                  <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                    {business.name}
                  </h3>
                  <span className="text-xs font-semibold text-indigo-600 block mt-0.5">
                    {business.category}
                  </span>
                  <p className="mt-3 text-sm text-slate-600 leading-relaxed font-normal">
                    {business.description}
                  </p>
                </div>

                {/* Key Workflows / Highlights */}
                <div className="space-y-2.5 pt-2">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                    Core Operational Focus
                  </span>
                  <div className="space-y-2">
                    {business.highlights.map((highlight) => (
                      <div key={highlight} className="flex items-center gap-2 text-xs font-bold text-slate-800">
                        <div className="flex h-4 w-4 items-center justify-center rounded-full bg-emerald-100 text-emerald-600 shrink-0">
                          <CheckCircle2 className="h-3 w-3 stroke-[3]" />
                        </div>
                        <span>{highlight}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Card Footer CTA */}
              <div className="pt-8 mt-6 border-t border-slate-100 flex items-center justify-between">
                <span className="text-xs text-slate-400 font-medium flex items-center gap-1.5">
                  <ShieldCheck className="h-3.5 w-3.5 text-indigo-500" />
                  Verified Business
                </span>

                {business.website && (
                  <a
                    href={business.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold text-xs transition-colors duration-200"
                  >
                    <span>Visit website ↗</span>
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Business Card 3: SA Collection (Featured Retail Workflow Story) */}
        <div className="mt-8 max-w-5xl mx-auto">
          <div className="group relative bg-white rounded-3xl border border-slate-200/80 p-6 sm:p-8 shadow-sm hover:shadow-xl hover:shadow-indigo-500/5 transition-all duration-300">

            {/* Header: Logo, Name, Location & Tag */}
            <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-slate-100">
              <div className="flex items-center gap-4">
                <div className="relative h-14 w-28 rounded-xl overflow-hidden bg-slate-950 p-2 flex items-center justify-center border border-slate-800 shadow-inner">
                  <img
                    src="/businesses/sa-collection-logo.jpg"
                    alt="SA Collection logo"
                    className="max-h-full max-w-full object-contain"
                  />
                </div>
                <div>
                  <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                    SA Collection
                  </h3>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-xs font-semibold text-indigo-600">
                      Women&apos;s Fashion Retail
                    </span>
                    <span className="text-slate-300">&middot;</span>
                    <span className="text-xs font-medium text-slate-500 flex items-center gap-1">
                      <MapPin className="h-3 w-3 text-rose-500" />
                      Mumbai Market
                    </span>
                  </div>
                </div>
              </div>

              <span className="inline-block bg-emerald-50 text-emerald-700 text-[10px] font-bold tracking-wider uppercase px-3 py-1.5 rounded-full border border-emerald-200/80">
                Current Workflow &rarr; Automation Opportunity
              </span>
            </div>

            {/* Business Context & Metrics */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
              <div className="md:col-span-7 space-y-3">
                <p className="text-sm sm:text-base text-slate-700 font-normal leading-relaxed">
                  A busy ladies&apos; clothing shop in the Mumbai retail hub handling daily customer enquiries on WhatsApp. BizMate streamlines their high-frequency order lifecycle.
                </p>
                <div className="flex flex-wrap items-center gap-4 pt-1">
                  <div className="bg-slate-50 border border-slate-200/80 rounded-xl px-3.5 py-2">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Daily Orders</span>
                    <span className="text-sm font-black text-slate-900">20–30 orders / day</span>
                  </div>
                  <div className="bg-slate-50 border border-slate-200/80 rounded-xl px-3.5 py-2">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Avg Order Value</span>
                    <span className="text-sm font-black text-slate-900">₹800 – ₹1,500</span>
                  </div>
                </div>
              </div>

              {/* Sample WhatsApp Sales Automation Visual */}
              <div className="md:col-span-5 bg-[#efeae2] p-3.5 rounded-2xl border border-slate-200/80 space-y-2 text-[11px] relative overflow-hidden"
                style={{
                  backgroundImage: `url('/whatsappChatWallPaper.jpg')`,
                  backgroundSize: '280px auto',
                  backgroundRepeat: 'repeat',
                }}
              >
                <div className="absolute inset-0 bg-white/40 pointer-events-none" />

                {/* Customer inquiry */}
                <div className="relative flex justify-end">
                  <div className="max-w-[85%] rounded-xl bg-[#d9fdd3] p-2 text-slate-800 shadow-xs">
                    <p className="leading-snug">Black kurti chahiye, mix size available hai?</p>
                  </div>
                </div>

                {/* Sales Agent response */}
                <div className="relative flex justify-start">
                  <div className="max-w-[88%] rounded-xl bg-white p-2 text-slate-800 shadow-xs">
                    <p className="leading-snug font-medium text-slate-900">Yes, 7 pieces ready to ship! Quote ₹1,299.</p>
                  </div>
                </div>

                {/* Payment button */}
                <div className="relative bg-white rounded-lg p-2 border border-slate-200 shadow-2xs">
                  <button className="w-full rounded-md bg-[#25d366] py-1 text-center font-bold text-white text-[10px]">
                    Pay Securely — ₹1,299
                  </button>
                </div>
              </div>
            </div>

            {/* Illustrative Process Flow Steps */}
            <div className="mt-6 pt-6 border-t border-slate-100">
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10.5px] font-bold uppercase tracking-wider text-slate-400">
                  Target Automation Flow
                </span>
                <span className="text-[10px] text-slate-400 font-mono">
                  Illustrative BizMate workflow
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5">
                {SA_COLLECTION_STEPS.map((step, idx) => (
                  <div key={step.label} className="bg-slate-50 rounded-xl border border-slate-200/70 p-2.5 text-center">
                    <span className="text-[9px] font-bold text-indigo-600 block">0{idx + 1}</span>
                    <span className="text-xs font-bold text-slate-800">{step.label}</span>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>

        {/* Business Card 4: Kraft Industrial Rubber Product Workflow Story Card */}
        <div className="mt-8 max-w-5xl mx-auto">
          <div className="group relative bg-white rounded-3xl border border-slate-200/80 p-6 sm:p-8 shadow-sm hover:shadow-xl hover:shadow-indigo-500/5 transition-all duration-300">

            {/* Header: Logo, Name, Category & Tag */}
            <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-slate-100">
              <div className="flex items-center gap-4">
                <div className="relative h-14 w-28 rounded-xl overflow-hidden bg-white p-2 flex items-center justify-center border border-slate-200 shadow-xs">
                  <img
                    src="/businesses/proof-01.jpg"
                    alt="Kraft logo"
                    className="max-h-full max-w-full object-contain"
                  />
                </div>
                <div>
                  <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                    Kraft
                  </h3>
                  <span className="text-xs font-semibold text-indigo-600 block">
                    Industrial Rubber Products
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="inline-block bg-amber-50 text-amber-700 text-[10px] font-bold tracking-wider uppercase px-3 py-1.5 rounded-full border border-amber-200/80">
                  Illustrative BizMate workflow
                </span>
              </div>
            </div>

            {/* Context & Quote */}
            <div className="mt-6 space-y-3">
              <p className="text-base sm:text-lg font-medium text-slate-800 leading-relaxed italic border-l-4 border-indigo-500 pl-4 py-1">
                &ldquo;IndiaMART enquiries become WhatsApp conversations — where BizMate can help move product questions, specifications, quotes and follow-ups forward.&rdquo;
              </p>
              <p className="text-xs text-slate-500 leading-relaxed">
                Kraft manufactures industrial rubber shapes and components for Indian B2B businesses and MSMEs. BizMate maps into their high-volume lead handling lifecycle.
              </p>
            </div>

            {/* Illustrative Workflow Visual Diagram */}
            <div className="mt-8 pt-6 border-t border-slate-100">
              <div className="flex items-center justify-between mb-4">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
                  Product Sales Workflow Map
                </span>
                <span className="text-[10px] text-slate-400 font-mono">
                  Illustrative BizMate workflow
                </span>
              </div>

              {/* Step Process Flow Badges */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                {KRAFT_STEPS.map((step, idx) => (
                  <div
                    key={step.label}
                    className="relative bg-slate-50 rounded-2xl border border-slate-200/70 p-3 flex flex-col justify-between text-center min-h-[85px]"
                  >
                    <span className="text-[10px] font-black text-indigo-600 font-mono block mb-1">
                      0{idx + 1}
                    </span>
                    <span className="text-xs font-bold text-slate-800 leading-snug">
                      {step.label}
                    </span>
                    {idx < KRAFT_STEPS.length - 1 && (
                      <ArrowRight className="hidden lg:block absolute -right-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-300 z-10" />
                    )}
                  </div>
                ))}
              </div>

              {/* Visual Component Cards (IndiaMART Badge, WhatsApp Chat Bubble, Spec & Quote Preview) */}
              <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">

                {/* 1. IndiaMART Source Badge & Lead Card */}
                <div className="rounded-2xl border border-teal-200/80 bg-teal-50/40 p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-extrabold uppercase tracking-wide bg-teal-600 text-white px-2 py-0.5 rounded-md">
                      IndiaMART Lead
                    </span>
                    <span className="text-[10px] font-medium text-teal-700">MSME Buyer</span>
                  </div>
                  <h4 className="text-xs font-bold text-slate-900">Rubber Grommets &amp; Bushings Enquiry</h4>
                  <p className="text-[11px] text-slate-600">Requirement: 5,000 units oil-resistant EPDM rubber shapes.</p>
                </div>

                {/* 2. WhatsApp Sales Agent Conversation */}
                <div className="rounded-2xl border border-emerald-200/80 bg-emerald-50/40 p-4 space-y-2">
                  <div className="flex items-center gap-1.5 text-emerald-700 font-bold text-[11px]">
                    <MessageSquare className="h-3.5 w-3.5 text-emerald-600" />
                    <span>WhatsApp Sales Agent</span>
                  </div>
                  <div className="bg-white rounded-xl p-2.5 border border-emerald-100 shadow-2xs text-[11px] text-slate-700 space-y-1">
                    <p className="font-semibold text-slate-900">Agent Response:</p>
                    <p>&ldquo;Checking EPDM shore hardness &amp; CAD specs for your application...&rdquo;</p>
                  </div>
                </div>

                {/* 3. Instant Quote & Spec Summary */}
                <div className="rounded-2xl border border-indigo-200/80 bg-indigo-50/40 p-4 space-y-2">
                  <div className="flex items-center gap-1.5 text-indigo-700 font-bold text-[11px]">
                    <FileText className="h-3.5 w-3.5 text-indigo-600" />
                    <span>Quote &amp; Spec Sheet</span>
                  </div>
                  <div className="bg-white rounded-xl p-2.5 border border-indigo-100 shadow-2xs text-[11px] text-slate-700 flex items-center justify-between">
                    <div>
                      <span className="font-bold text-slate-900 block">Draft Quote #KR-842</span>
                      <span className="text-[10px] text-slate-500">5,000 Custom Molded Seals</span>
                    </div>
                    <span className="font-bold text-indigo-600 text-xs">Ready</span>
                  </div>
                </div>

              </div>

            </div>

          </div>
        </div>

      </div>
    </section>
  );
}
