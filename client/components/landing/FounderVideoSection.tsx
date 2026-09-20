'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Sparkles, MessageCircle, Clock3, Wallet, Volume2, X } from 'lucide-react';

const FOUNDER_VIDEO_ID = "QTemHF4NwCs";

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
            
            <div className="relative aspect-video w-full rounded-2xl overflow-hidden bg-slate-950 flex flex-col justify-between group">
              
              {!isPlaying ? (
                <div
                  onClick={() => setIsPlaying(true)}
                  className="relative w-full h-full flex flex-col justify-between p-6 sm:p-10 cursor-pointer"
                >
                  {/* Integrated Preview YouTube Video (Muted Autoplay Loop) */}
                  <div className="absolute inset-0 w-full h-full overflow-hidden pointer-events-none">
                    <iframe
                      src={`https://www.youtube.com/embed/${FOUNDER_VIDEO_ID}?autoplay=1&mute=1&playsinline=1&controls=0&enablejsapi=1&rel=0&loop=1&playlist=${FOUNDER_VIDEO_ID}`}
                      title="BizMate Founder Video Preview"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      tabIndex={-1}
                      className="absolute inset-0 w-[150%] h-[150%] top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 object-cover opacity-40 blur-[1px] pointer-events-none scale-105"
                    />
                  </div>

                  {/* Dark Gradient Overlay for contrast */}
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/60 to-slate-950/40 pointer-events-none" />

                  {/* Ambient Light Overlay */}
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl group-hover:bg-indigo-600/35 transition-all duration-300 pointer-events-none" />

                  {/* Top Bar */}
                  <div className="relative z-10 flex items-center justify-between">
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-900/80 px-3 py-1 text-xs font-semibold text-slate-200 backdrop-blur-md border border-white/10 shadow-sm">
                      <Volume2 className="h-3.5 w-3.5 text-indigo-400" />
                      <span>A calmer way to run your business</span>
                    </span>
                    <span className="rounded-md bg-indigo-600 px-2.5 py-1 text-xs font-bold text-white shadow-sm">
                      Watch Founder Story
                    </span>
                  </div>

                  {/* Center Play Button & Title */}
                  <div className="relative z-10 my-auto text-center space-y-4">
                    <motion.button
                      whileHover={{ scale: 1.08 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={(e) => {
                        e.stopPropagation();
                        setIsPlaying(true);
                      }}
                      className="mx-auto flex h-20 w-20 sm:h-24 sm:w-24 items-center justify-center rounded-full bg-white text-slate-950 shadow-2xl hover:bg-indigo-50 transition-all cursor-pointer group-hover:shadow-indigo-500/20 group-hover:shadow-2xl"
                      aria-label="Play Founder Video"
                    >
                      <Play className="h-8 w-8 sm:h-10 sm:w-10 fill-current ml-1 text-slate-900" />
                    </motion.button>
                    <div>
                      <h3 className="text-xl sm:text-3xl font-extrabold text-white tracking-tight drop-shadow-md">
                        The work behind the work should not be yours.
                      </h3>
                      <span className="text-xs text-slate-300 block mt-1 font-medium tracking-wide">
                        BizMate founder story — Watch video
                      </span>
                    </div>
                  </div>

                  {/* Bottom Bar */}
                  <div className="relative z-10 flex items-center justify-between border-t border-white/10 pt-4 text-xs text-slate-300">
                    <span className="font-semibold text-white">Watch founder story</span>
                    <div className="flex items-center gap-2 font-mono">
                      <span className="inline-flex items-center gap-1 text-indigo-400 font-sans font-bold">
                        <Play className="h-3 w-3 fill-current" /> Play Video
                      </span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="relative w-full h-full bg-slate-950">
                  <button
                    onClick={() => setIsPlaying(false)}
                    aria-label="Close video"
                    className="absolute top-3 right-3 z-30 flex h-9 w-9 items-center justify-center rounded-full bg-slate-900/90 text-white hover:bg-slate-800 transition-colors border border-white/10 shadow-lg cursor-pointer"
                  >
                    <X className="h-5 w-5" />
                  </button>

                  <iframe
                    src={`https://www.youtube.com/embed/${FOUNDER_VIDEO_ID}?autoplay=1&mute=0&playsinline=1&controls=1&enablejsapi=1&rel=0`}
                    title="BizMate Founder Video"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share; fullscreen"
                    allowFullScreen
                    className="w-full h-full border-0 relative z-10 rounded-2xl"
                  />
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
