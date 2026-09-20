'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Check, Sparkles, MessageCircle, TrendingUp } from 'lucide-react';
import { Iphone3D } from './Iphone3D';
import { WhatsAppScreen } from './WhatsAppScreen';
import { ManagerAgentScreen } from './ManagerAgentScreen';

const AGENT_STRIP = [
  { name: 'Sales Agent', desc: 'customer conversations' },
  { name: 'Manager Agent', desc: 'owner briefings' },
  { name: 'Finance Agent', desc: 'bills & balances' },
  { name: 'Operation Agent', desc: 'stock & vendors' },
  { name: 'Social Agent', desc: 'content & growth' },
];

export function Hero() {
  return (
    <section id="top" className="relative min-h-screen pt-28 pb-12 overflow-hidden bg-[#F8FAFF]">
      {/* Subtle Background Light Glows */}
      <div className="pointer-events-none absolute top-0 left-1/2 -translate-x-1/2 h-[500px] w-full max-w-5xl -z-10 opacity-50">
        <div className="absolute top-12 left-1/4 h-72 w-72 rounded-full bg-indigo-200/40 blur-[100px]" />
        <div className="absolute top-24 right-1/4 h-72 w-72 rounded-full bg-blue-200/40 blur-[100px]" />
      </div>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Eyebrow Label */}
        <div className="flex justify-center">
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 rounded-full border border-indigo-200/80 bg-white/90 px-4 py-1.5 text-[11px] font-bold tracking-wider text-indigo-700 shadow-xs backdrop-blur-sm uppercase"
          >
            <span className="h-2 w-2 rounded-full bg-indigo-600 animate-pulse" />
            <span>AI Team For Your Business</span>
          </motion.div>
        </div>

        {/* 3-Column Desktop Grid */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          
          {/* Left: Manager iPhone */}
          <div className="hidden lg:flex lg:col-span-3 justify-center relative">
            <div className="w-full max-w-[280px]">
              <Iphone3D glowColor="rgba(99, 102, 241, 0.12)">
                <ManagerAgentScreen />
              </Iphone3D>
            </div>

            {/* Left Floating Badge */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6, duration: 0.5 }}
              className="absolute -bottom-4 -right-4 z-20 hidden xl:flex items-center gap-2.5 rounded-2xl border border-slate-200 bg-white p-3 shadow-lg text-xs"
            >
              <div className="flex h-7 w-7 items-center justify-center rounded-xl bg-emerald-100 text-emerald-600">
                <MessageCircle className="h-4 w-4" />
              </div>
              <div>
                <strong className="text-slate-900 block font-bold text-[11px]">Customer replied</strong>
                <span className="text-slate-500 text-[10px]">Quote for 7</span>
              </div>
              <span className="text-emerald-500 font-bold ml-1">✓</span>
            </motion.div>
          </div>

          {/* Center: Hero Copy & Actions */}
          <div className="lg:col-span-6 text-center space-y-6">
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-xs sm:text-sm font-semibold text-indigo-600 uppercase tracking-wider"
            >
              More selling. Less remembering.
            </motion.p>

            <motion.h1
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-slate-900 leading-[1.05]"
            >
              Run your business.<br />
              <span className="text-indigo-600">Not the busywork.</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-base sm:text-lg text-slate-600 leading-relaxed max-w-xl mx-auto font-normal"
            >
              Your AI team for sales, operations, finance and growth — working quietly behind the conversations you already have.
            </motion.p>

            {/* Hero Action Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3"
            >
              <a
                href="/#product"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-full bg-indigo-600 px-7 py-3.5 text-sm font-bold text-white shadow-lg shadow-indigo-600/25 hover:bg-indigo-700 transition-all transform hover:scale-[1.02]"
              >
                <span>Watch BizMate work</span>
                <ArrowRight className="h-4 w-4" />
              </a>

              <Link
                href="/early-access"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-full bg-white border border-slate-300 px-6 py-3.5 text-sm font-bold text-slate-800 shadow-xs hover:bg-slate-50 transition-colors"
              >
                <span>Reserve early access</span>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-extrabold text-indigo-600">
                  ₹2,000
                </span>
              </Link>
            </motion.div>

            {/* Hero Micro Notes */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="pt-2 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs font-semibold text-slate-500"
            >
              <span className="inline-flex items-center gap-1.5">
                <Check className="h-4 w-4 text-emerald-500 stroke-[3]" />
                Built for real businesses
              </span>
              <span className="inline-flex items-center gap-1.5">
                <Check className="h-4 w-4 text-emerald-500 stroke-[3]" />
                One simple interface
              </span>
            </motion.div>
          </div>

          {/* Right: Sales iPhone */}
          <div className="hidden lg:flex lg:col-span-3 justify-center relative">
            <div className="w-full max-w-[280px]">
              <Iphone3D glowColor="rgba(37, 211, 102, 0.12)">
                <WhatsAppScreen />
              </Iphone3D>
            </div>

            {/* Right Floating Badge */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6, duration: 0.5 }}
              className="absolute -bottom-4 -left-4 z-20 hidden xl:flex items-center gap-2.5 rounded-2xl border border-slate-200 bg-white p-3 shadow-lg text-xs"
            >
              <div className="flex h-7 w-7 items-center justify-center rounded-xl bg-blue-100 text-blue-600">
                <TrendingUp className="h-4 w-4" />
              </div>
              <div>
                <strong className="text-slate-900 block font-bold text-[11px]">Sales yesterday</strong>
                <span className="text-slate-500 text-[10px]">₹1.84L <em className="text-emerald-600 not-italic font-bold">+12.4%</em></span>
              </div>
            </motion.div>
          </div>

        </div>

        {/* Mobile View Phones (Single Centered iPhone Preview) */}
        <div className="mt-10 lg:hidden flex justify-center">
          <div className="w-full max-w-[300px]">
            <Iphone3D glowColor="rgba(99, 102, 241, 0.12)">
              <WhatsAppScreen />
            </Iphone3D>
          </div>
        </div>

        {/* Bottom Proof Strip / Agent Role Bar */}
        <div className="mt-16 border-t border-slate-200/80 pt-8 pb-4 grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
          {AGENT_STRIP.map((agent) => (
            <div key={agent.name} className="space-y-0.5">
              <strong className="text-xs font-extrabold text-slate-900 block">{agent.name}</strong>
              <span className="text-[11px] text-slate-500 font-medium block">{agent.desc}</span>
            </div>
          ))}
        </div>

      </div>
    </section>
  );
}
