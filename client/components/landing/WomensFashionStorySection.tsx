'use client';

import React from 'react';
import { ArrowUpRight, CheckCircle2, ShieldCheck, Sparkles } from 'lucide-react';

interface BusinessStory {
  id: string;
  name: string;
  category: string;
  website: string;
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

        {/* Business Cards Composition (2-Column Desktop, 1-Column Mobile) */}
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
                  <div className="flex items-center gap-2">
                    <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                      {business.name}
                    </h3>
                  </div>
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

                <a
                  href={business.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold text-xs transition-colors duration-200"
                >
                  <span>Visit website ↗</span>
                </a>
              </div>
            </div>
          ))}
        </div>

        {/* Supporting Secondary Proof Element */}
        <div className="mt-12 max-w-2xl mx-auto text-center">
          <div className="inline-flex items-center gap-3 px-4 py-2.5 rounded-2xl bg-white border border-slate-200/80 shadow-xs">
            <div className="h-7 w-7 rounded-lg overflow-hidden bg-slate-900 p-1 flex items-center justify-center border border-slate-700 shrink-0">
              <img
                src="/businesses/proof-01.jpg"
                alt="Partner Proof Asset"
                className="max-h-full max-w-full object-contain"
              />
            </div>
            <p className="text-xs text-slate-600 font-medium">
              Co-designing automated operations with forward-thinking teams.
            </p>
          </div>
        </div>

      </div>
    </section>
  );
}
