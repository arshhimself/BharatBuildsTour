'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Pause, Sparkles, MessageCircle, Clock3, Wallet, X, Volume2, ShieldCheck } from 'lucide-react';

const FOUNDER_POINTS = [
  { label: 'Less chasing', icon: Sparkles },
  { label: 'More selling', icon: MessageCircle },
  { label: 'More time to grow', icon: Clock3 },
  { label: 'Clearer decisions', icon: Wallet },
];

export function FounderVideoSection() {
  const [isPlaying, setIsPlaying] = useState(false);

  return (
    <section id="product" className="relative py-24 bg-white border-t border-slate-100 overflow-hidden">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-600 block">
            WHY WE BUILT BIZMATE
          </span>

          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
            We built BizMate for the businesses<br className="hidden sm:inline" /> already doing everything manually.
          </h2>

          <p className="text-base sm:text-lg text-slate-600 leading-relaxed font-normal max-w-2xl mx-auto">
            WhatsApp messages. Stock checks. Customer follow-ups. Vendor updates. Payments. Content. Bills. Too many things to remember.
          </p>
        </div>

        {/* Video Card Container */}
        <div className="mt-12 max-w-4xl mx-auto">
          <div className="relative rounded-3xl overflow-hidden border border-slate-800 bg-slate-950 p-2 sm:p-4 shadow-2xl shadow-slate-900/10">
            
            <div className="relative aspect-video w-full rounded-2xl overflow-hidden bg-gradient-to-tr from-slate-950 via-slate-900 to-indigo-950 flex flex-col justify-between p-6 sm:p-10 group">
              
              {!isPlaying ? (
                <>
                  {/* Ambient Light Overlay */}
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl group-hover:bg-indigo-600/30 transition-all duration-300 pointer-events-none" />

                  {/* Top Bar */}
                  <div className="relative z-10 flex items-center justify-between">
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-slate-200 backdrop-blur-md border border-white/10">
                      <Volume2 className="h-3.5 w-3.5 text-indigo-400" />
                      <span>A calmer way to run your business</span>
                    </span>
                    <span className="rounded-md bg-indigo-600 px-2.5 py-1 text-xs font-bold text-white shadow-sm">
                      01:28
                    </span>
                  </div>

                  {/* Center Play Button & Title */}
                  <div className="relative z-10 my-auto text-center space-y-4">
                    <motion.button
                      whileHover={{ scale: 1.08 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setIsPlaying(true)}
                      className="mx-auto flex h-20 w-20 sm:h-24 sm:w-24 items-center justify-center rounded-full bg-white text-slate-950 shadow-2xl hover:bg-indigo-50 transition-all cursor-pointer"
                      aria-label="Play Founder Video"
                    >
                      <Play className="h-8 w-8 sm:h-10 sm:w-10 fill-current ml-1" />
                    </motion.button>
                    <div>
                      <h3 className="text-xl sm:text-3xl font-extrabold text-white tracking-tight">
                        The work behind the work should not be yours.
                      </h3>
                      <span className="text-xs text-slate-400 block mt-1 font-medium">
                        BizMate / founder story
                      </span>
                    </div>
                  </div>

                  {/* Bottom Bar */}
                  <div className="relative z-10 flex items-center justify-between border-t border-slate-800/80 pt-4 text-xs text-slate-400">
                    <span className="font-semibold text-slate-300">Watch founder story</span>
                    <div className="flex items-center gap-2 font-mono">
                      <div className="w-24 h-1 rounded-full bg-slate-800 overflow-hidden">
                        <div className="w-1/3 h-full bg-indigo-500" />
                      </div>
                      <span>01:28</span>
                    </div>
                  </div>
                </>
              ) : (
                <div className="relative h-full w-full bg-slate-950 flex flex-col items-center justify-center text-center p-6 space-y-4">
                  <button
                    onClick={() => setIsPlaying(false)}
                    className="absolute top-4 right-4 z-20 flex h-9 w-9 items-center justify-center rounded-full bg-slate-900 text-white hover:bg-slate-800 transition-colors"
                  >
                    <X className="h-5 w-5" />
                  </button>

                  <div className="h-14 w-14 rounded-2xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center border border-indigo-500/30">
                    <Sparkles className="h-7 w-7 animate-spin" style={{ animationDuration: '8s' }} />
                  </div>

                  <h3 className="text-lg font-bold text-white">BizMate Founder Walkthrough</h3>
                  <p className="text-xs sm:text-sm text-slate-300 max-w-lg leading-relaxed font-normal">
                    "We built BizMate so small business owners never have to spend hours checking stock, typing WhatsApp replies, calculating GST, and following up on unpaid bills manually. Your AI team handles the routine, giving you back control."
                  </p>

                  <button
                    onClick={() => setIsPlaying(false)}
                    className="rounded-full bg-indigo-600 px-5 py-2 text-xs font-bold text-white hover:bg-indigo-500 transition-colors"
                  >
                    Close Video
                  </button>
                </div>
              )}

            </div>

          </div>
        </div>

        {/* Four Points Strip */}
        <div className="mt-10 flex flex-wrap items-center justify-center gap-6 sm:gap-10 text-xs font-extrabold text-slate-700">
          {FOUNDER_POINTS.map((point) => {
            const Icon = point.icon;
            return (
              <span key={point.label} className="inline-flex items-center gap-2">
                <Icon className="h-4 w-4 text-indigo-600" />
                <span>{point.label}</span>
              </span>
            );
          })}
        </div>

      </div>
    </section>
  );
}
