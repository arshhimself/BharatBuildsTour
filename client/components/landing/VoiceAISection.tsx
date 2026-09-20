'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Pause, Mic, Volume2 } from 'lucide-react';

export function VoiceAISection() {
  const [customerPlaying, setCustomerPlaying] = useState(false);
  const [ownerPlaying, setOwnerPlaying] = useState(false);

  return (
    <section id="voice" className="relative py-24 bg-white border-t border-slate-100 overflow-hidden">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3">
          <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-600 block">
            VOICE AI
          </span>

          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
            You don't have to type.<br />
            <span className="text-indigo-600">Just talk.</span>
          </h2>

          <p className="text-base sm:text-lg text-slate-600 font-normal max-w-2xl mx-auto">
            BizMate works with the way business owners and customers actually communicate — quick voice notes, mixed languages and everyday conversation.
          </p>
        </div>

        {/* Dual Voice Cards Grid */}
        <div className="mt-14 grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          
          {/* Card 1: Customer -> Sales Agent */}
          <div className="rounded-3xl border border-slate-200 bg-emerald-50/40 p-6 sm:p-8 space-y-6 shadow-sm hover:shadow-md transition-shadow">
            
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500 text-white font-extrabold text-sm shadow-xs">
                C
              </div>
              <div>
                <span className="text-[10px] font-extrabold uppercase tracking-wider text-emerald-700 block">
                  CUSTOMER → SALES AGENT
                </span>
                <h3 className="text-base sm:text-lg font-bold text-slate-900">
                  “Bhai, 10 black kurti chahiye…”
                </h3>
              </div>
            </div>

            {/* Voice Message Waveform Player */}
            <div className="rounded-2xl border border-emerald-200 bg-white p-5 space-y-4 shadow-xs">
              <div className="flex items-center justify-between text-xs text-slate-500">
                <span className="font-bold text-slate-800">Customer voice note</span>
                <span className="font-mono text-emerald-700 font-bold">Hinglish · 0:12</span>
              </div>

              <div className="flex items-center gap-4">
                <button
                  onClick={() => setCustomerPlaying(!customerPlaying)}
                  className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-emerald-500 text-white font-bold shadow-md hover:bg-emerald-600 transition-all cursor-pointer"
                  aria-label={customerPlaying ? 'Pause Customer Voice Note' : 'Play Customer Voice Note'}
                >
                  {customerPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5 fill-current ml-0.5" />}
                </button>

                {/* Animated Waveform */}
                <div className="flex-1 flex items-center gap-1 h-10 px-3 bg-slate-50 rounded-xl border border-slate-200/80">
                  {Array.from({ length: 26 }).map((_, idx) => {
                    const height = 12 + ((idx * 17) % 22);
                    return (
                      <motion.div
                        key={idx}
                        animate={
                          customerPlaying
                            ? { height: [`${height * 0.4}px`, `${height}px`, `${height * 0.4}px`] }
                            : { height: `${height * 0.5}px` }
                        }
                        transition={{
                          repeat: customerPlaying ? Infinity : 0,
                          duration: 0.8,
                          delay: idx * 0.04
                        }}
                        className={`flex-1 rounded-full ${
                          customerPlaying ? 'bg-emerald-500' : 'bg-slate-300'
                        }`}
                      />
                    );
                  })}
                </div>
              </div>

              <div className="flex justify-between text-[11px] font-mono text-slate-400 border-t border-slate-100 pt-2">
                <span>00:00</span>
                <span>00:12</span>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 text-xs">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-0.5">
                  Transcript
                </span>
                <p className="font-medium text-slate-800">
                  "Bhai 10 black kurti chahiye… size mix chalega?"
                </p>
              </div>
            </div>

            {/* Sales Agent Reply */}
            <div className="pt-2">
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                Sales Agent reply
              </span>
              <p className="text-sm font-semibold text-slate-800 bg-white p-4 rounded-2xl border border-slate-200/80">
                "We have seven ready to ship. I can prepare the quote for the available stock."
              </p>
            </div>

          </div>

          {/* Card 2: Owner -> Manager Agent */}
          <div className="rounded-3xl border border-slate-200 bg-indigo-50/40 p-6 sm:p-8 space-y-6 shadow-sm hover:shadow-md transition-shadow">
            
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-indigo-600 text-white font-extrabold text-sm shadow-xs">
                M
              </div>
              <div>
                <span className="text-[10px] font-extrabold uppercase tracking-wider text-indigo-700 block">
                  OWNER → MANAGER AGENT
                </span>
                <h3 className="text-base sm:text-lg font-bold text-slate-900">
                  “Kal ka business kaisa tha?”
                </h3>
              </div>
            </div>

            {/* Voice Message Waveform Player */}
            <div className="rounded-2xl border border-indigo-200 bg-white p-5 space-y-4 shadow-xs">
              <div className="flex items-center justify-between text-xs text-slate-500">
                <span className="font-bold text-slate-800">Owner voice note</span>
                <span className="font-mono text-indigo-700 font-bold">Hinglish · 0:09</span>
              </div>

              <div className="flex items-center gap-4">
                <button
                  onClick={() => setOwnerPlaying(!ownerPlaying)}
                  className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-indigo-600 text-white font-bold shadow-md hover:bg-indigo-700 transition-all cursor-pointer"
                  aria-label={ownerPlaying ? 'Pause Owner Voice Note' : 'Play Owner Voice Note'}
                >
                  {ownerPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5 fill-current ml-0.5" />}
                </button>

                {/* Animated Waveform */}
                <div className="flex-1 flex items-center gap-1 h-10 px-3 bg-slate-50 rounded-xl border border-slate-200/80">
                  {Array.from({ length: 26 }).map((_, idx) => {
                    const height = 12 + ((idx * 19) % 22);
                    return (
                      <motion.div
                        key={idx}
                        animate={
                          ownerPlaying
                            ? { height: [`${height * 0.4}px`, `${height}px`, `${height * 0.4}px`] }
                            : { height: `${height * 0.5}px` }
                        }
                        transition={{
                          repeat: ownerPlaying ? Infinity : 0,
                          duration: 0.8,
                          delay: idx * 0.04
                        }}
                        className={`flex-1 rounded-full ${
                          ownerPlaying ? 'bg-indigo-600' : 'bg-slate-300'
                        }`}
                      />
                    );
                  })}
                </div>
              </div>

              <div className="flex justify-between text-[11px] font-mono text-slate-400 border-t border-slate-100 pt-2">
                <span>00:00</span>
                <span>00:09</span>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 text-xs">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-0.5">
                  Transcript
                </span>
                <p className="font-medium text-slate-800">
                  "Good morning. Yesterday’s sales were ₹1.84 lakh. You have three pending payments, two follow-ups and a vendor price update."
                </p>
              </div>
            </div>

            {/* Manager Agent Reply */}
            <div className="pt-2">
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                Manager Agent reply
              </span>
              <p className="text-sm font-semibold text-slate-800 bg-white p-4 rounded-2xl border border-slate-200/80">
                "Good morning. Here's what needs your attention today."
              </p>
            </div>

          </div>

        </div>

        {/* Demo Preview State Footer */}
        <div className="mt-8 text-center text-xs text-slate-400 font-semibold">
          <span>Interactive Audio Simulation · Multi-Lingual Hinglish Voice Recognition</span>
        </div>

      </div>
    </section>
  );
}
