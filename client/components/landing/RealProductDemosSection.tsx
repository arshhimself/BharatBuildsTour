'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, MessageSquare, Mic, Share2, ArrowRight } from 'lucide-react';
import { PremiumYouTubePlayer } from '@/components/landing/PremiumYouTubePlayer';

interface DemoSelectorItem {
  id: string;
  youtubeId: string;
  category: string;
  title: string;
  subtitle: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  iconBg: string;
  color: string;
}

const DEMOS: DemoSelectorItem[] = [
  {
    id: 'sales-agent',
    youtubeId: 'fZdbSssVUp4',
    category: 'SALES AGENT',
    title: 'From message to payment.',
    subtitle: 'Sales Agent handles the conversation, payment and invoice on WhatsApp.',
    description: 'From message → payment → invoice',
    icon: MessageSquare,
    iconBg: 'bg-emerald-600 text-white',
    color: 'border-emerald-500/60 bg-emerald-50/50 text-emerald-950',
  },
  {
    id: 'voice-ai',
    youtubeId: 'pt4SLCnRePg',
    category: 'VOICE AI',
    title: 'Speak the way you already speak.',
    subtitle: 'Marathi voice in. Marathi voice out. No typing required.',
    description: 'Marathi voice → Marathi reply',
    icon: Mic,
    iconBg: 'bg-indigo-600 text-white',
    color: 'border-indigo-500/60 bg-indigo-50/50 text-indigo-950',
  },
  {
    id: 'social-agent',
    youtubeId: 'ET-A1wb6fS4',
    category: 'SOCIAL AGENT',
    title: 'From one WhatsApp request to a live social post.',
    subtitle: 'Ask your Manager Agent. Let Social Agent create the content. Review it. Publish.',
    description: 'WhatsApp → creative → Instagram',
    icon: Share2,
    iconBg: 'bg-pink-600 text-white',
    color: 'border-pink-500/60 bg-pink-50/50 text-pink-950',
  },
];

export function RealProductDemosSection() {
  const [selectedDemoId, setSelectedDemoId] = useState<string>('sales-agent');

  const activeDemo = DEMOS.find((d) => d.id === selectedDemoId) || DEMOS[0];

  return (
    <section id="real-demos" className="relative py-24 bg-[#F8FAFF] border-t border-slate-200/60 overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-0 inset-x-0 h-40 bg-gradient-to-b from-white to-transparent pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[500px] bg-indigo-50/50 rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-700 text-[11px] font-extrabold uppercase tracking-wider">
            <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
            <span>REAL PRODUCT DEMOS</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900 leading-tight">
            See BizMate working in real conversations.
          </h2>

          <p className="text-base sm:text-lg text-slate-600 font-normal max-w-xl mx-auto leading-relaxed">
            Real workflows. Real conversations. Real product behavior.
          </p>
        </div>

        {/* CINEMATIC PRODUCT-VIDEO THEATER */}
        <div className="mt-14 max-w-5xl mx-auto space-y-8">
          
          {/* Main Hero Video Stage */}
          <div className="relative">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeDemo.id}
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                transition={{ duration: 0.3 }}
              >
                <PremiumYouTubePlayer
                  videoId={activeDemo.youtubeId}
                  title={activeDemo.title}
                  subtitle={activeDemo.subtitle}
                  label={`LIVE PRODUCT DEMO · ${activeDemo.category}`}
                  isActive={true}
                />
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Premium Video Selectors Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {DEMOS.map((demo) => {
              const isSelected = demo.id === selectedDemoId;
              const IconComp = demo.icon;

              return (
                <button
                  key={demo.id}
                  onClick={() => setSelectedDemoId(demo.id)}
                  className={`group relative rounded-2xl border p-4 text-left transition-all duration-300 cursor-pointer overflow-hidden ${
                    isSelected
                      ? 'bg-white border-indigo-600/80 shadow-xl ring-2 ring-indigo-600/20 translate-y-[-2px]'
                      : 'bg-white/80 border-slate-200/90 hover:border-slate-300 hover:bg-white shadow-xs'
                  }`}
                >
                  {/* Top Active Progress Bar Line */}
                  {isSelected && (
                    <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-600 animate-pulse" />
                  )}

                  <div className="flex items-center gap-3 mb-2">
                    <div className={`flex h-8 w-8 items-center justify-center rounded-xl font-bold text-xs shrink-0 ${demo.iconBg}`}>
                      <IconComp className="h-4 w-4" />
                    </div>
                    <div>
                      <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400 block">
                        {demo.category}
                      </span>
                      <h4 className="text-xs font-bold text-slate-900 leading-tight">
                        {demo.id === 'sales-agent' ? 'Sales Agent' : demo.id === 'voice-ai' ? 'Voice AI' : 'Social Agent'}
                      </h4>
                    </div>
                  </div>

                  <p className="text-xs text-slate-600 font-medium leading-snug">
                    {demo.description}
                  </p>

                  <div className={`mt-3 flex items-center gap-1 text-[10.5px] font-bold transition-colors ${
                    isSelected ? 'text-indigo-600' : 'text-slate-400 group-hover:text-slate-600'
                  }`}>
                    <span>{isSelected ? 'Active Demo' : 'Select Demo'}</span>
                    <ArrowRight className={`h-3 w-3 transition-transform ${isSelected ? 'translate-x-1' : 'group-hover:translate-x-0.5'}`} />
                  </div>
                </button>
              );
            })}
          </div>

        </div>

      </div>
    </section>
  );
}
