'use client';

import React from 'react';
import Link from 'next/link';
import { Sparkles, ArrowRight, Bot, ShieldCheck, Zap } from 'lucide-react';
import { PremiumYouTubePlayer } from '@/components/landing/PremiumYouTubePlayer';

const AGENT_CHIPS = [
  { name: 'Manager Agent', role: 'Orchestrator', color: 'bg-indigo-50 text-indigo-700 border-indigo-200' },
  { name: 'Finance Agent', role: 'Payments & Invoices', color: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  { name: 'Social Agent', role: 'Posts & Creatives', color: 'bg-purple-50 text-purple-700 border-purple-200' },
  { name: 'Operations Agent', role: 'Inventory & Stock', color: 'bg-blue-50 text-blue-700 border-blue-200' },
  { name: 'Sales Agent', role: 'Catalog & Orders', color: 'bg-amber-50 text-amber-700 border-amber-200' },
];

export function AgentOfficePreviewSection() {
  return (
    <section id="agent-office-preview" className="scroll-mt-24 relative py-16 sm:py-24 bg-gradient-to-b from-white via-slate-50/50 to-white border-t border-slate-200/60 overflow-hidden">
      {/* Soft Background Decor */}
      <div className="absolute top-0 inset-x-0 h-32 bg-gradient-to-b from-indigo-50/30 to-transparent pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[500px] bg-gradient-to-r from-indigo-100/30 via-purple-100/30 to-blue-100/30 rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">

        {/* Section Header (Above Video) */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-10 sm:mb-14">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-50 border border-indigo-200/80 text-indigo-700 text-[11px] font-extrabold uppercase tracking-wider shadow-xs">
            <Sparkles className="h-3.5 w-3.5 text-indigo-600 animate-pulse" />
            <span>BEHIND THE CONVERSATION</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900 leading-[1.15]">
            See the AI team at work.
          </h2>

          <p className="text-base sm:text-lg text-slate-600 font-medium max-w-2xl mx-auto leading-relaxed">
            Simple conversations on the surface. Multiple agents coordinating underneath.
          </p>
        </div>

        {/* Cinematic Product Theater Stage (16:9 Video Dominating Width) */}
        <div className="max-w-5xl mx-auto">
          <div className="relative p-1.5 sm:p-2.5 rounded-[32px] bg-gradient-to-b from-white via-slate-100 to-slate-200/80 border border-white/80 shadow-[0_30px_70px_rgba(30,41,59,0.12)]">
            <PremiumYouTubePlayer
              videoId="ZsH8Fy58Sj0"
              title="Manager + specialist agents at work"
              subtitle="Watch Manager & Specialist Agents coordinate live behind the scenes."
              label="AGENT OFFICE"
              isActive={true}
            />
          </div>

          {/* Specialist Agent Metadata Chips Under Video */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-2 sm:gap-3">
            {AGENT_CHIPS.map((chip) => (
              <span
                key={chip.name}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-bold transition-all shadow-2xs hover:scale-105 ${chip.color}`}
              >
                <Bot className="h-3.5 w-3.5 opacity-80" />
                <span>{chip.name}</span>
                <span className="text-[10px] font-medium opacity-60">({chip.role})</span>
              </span>
            ))}
          </div>

          {/* CTA Button Below Video */}
          <div className="mt-8 text-center">
            <Link
              href="/agent-office"
              className="group inline-flex items-center gap-2.5 px-7 py-3.5 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white font-extrabold text-sm shadow-xl shadow-indigo-600/20 hover:shadow-indigo-600/30 transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0 cursor-pointer"
            >
              <span>Explore the full Agent Office</span>
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </div>

        </div>

      </div>
    </section>
  );
}
