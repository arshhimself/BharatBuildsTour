'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  Sparkles,
  MessageCircle,
  Wallet,
  Share2,
  Package,
  CheckCheck,
  ShieldCheck,
  User,
  ArrowRight,
} from 'lucide-react';

const SPECIALISTS = [
  {
    id: 'finance',
    name: 'Finance Agent',
    role: 'Bills & balances',
    icon: Wallet,
    color: 'bg-purple-50 text-purple-700 border-purple-200/80',
    iconBg: 'bg-purple-600 text-white',
  },
  {
    id: 'social',
    name: 'Social Agent',
    role: 'Content & campaigns',
    icon: Share2,
    color: 'bg-pink-50 text-pink-700 border-pink-200/80',
    iconBg: 'bg-pink-600 text-white',
  },
  {
    id: 'operation',
    name: 'Operation Agent',
    role: 'Stock & vendors',
    icon: Package,
    color: 'bg-amber-50 text-amber-700 border-amber-200/80',
    iconBg: 'bg-amber-600 text-white',
  },
];

export function MultiAgentSection() {
  return (
    <section id="ai-team" className="relative py-24 bg-[#F8FAFF] border-t border-slate-200/60 overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[600px] bg-indigo-50/40 rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">

        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-700 text-[11px] font-extrabold uppercase tracking-wider">
            <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
            <span>THE AI TEAM</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900 leading-tight">
            You talk to one.<br />
            <span className="text-indigo-600">Your AI team handles the rest.</span>
          </h2>

          <p className="text-base sm:text-lg text-slate-600 font-normal max-w-2xl mx-auto leading-relaxed">
            You talk to Manager Agent. Your customers talk to Sales Agent. Finance, Social and Operation agents work quietly behind the scenes.
          </p>
        </div>

        {/* Specialist Agent System Bar (Background / Top Layer) */}
        <div className="mt-12 max-w-4xl mx-auto">
          <div className="text-center mb-3">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Specialist Agents Working Quietly Behind the Scenes
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {SPECIALISTS.map((agent) => (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4 }}
                className={`rounded-2xl border p-3 flex items-center gap-3 bg-white/80 backdrop-blur-xs shadow-2xs ${agent.color}`}
              >
                <div className={`flex h-8 w-8 items-center justify-center rounded-xl font-bold text-xs shrink-0 ${agent.iconBg}`}>
                  <agent.icon className="h-4 w-4" />
                </div>
                <div className="min-w-0">
                  <h4 className="text-xs font-bold text-slate-900 truncate">{agent.name}</h4>
                  <p className="text-[10px] text-slate-500 font-medium truncate">{agent.role}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Primary Dual Conversation Canvas (Hero Visualization) */}
        <div className="mt-10 grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl mx-auto">

          {/* LEFT: OWNER → MANAGER AGENT CONVERSATION HERO */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="rounded-3xl border border-slate-200/90 bg-white p-5 sm:p-6 shadow-xl flex flex-col justify-between overflow-hidden relative"
          >
            {/* Header Badge */}
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-600 text-white">
                  <User className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-xs font-extrabold text-slate-900 leading-tight">OWNER &rarr; MANAGER AGENT</h3>
                  <span className="text-[10px] text-indigo-600 font-semibold block">WhatsApp Conversation</span>
                </div>
              </div>
              <span className="bg-indigo-50 text-indigo-700 text-[9px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full border border-indigo-100">
                You Talk To One
              </span>
            </div>

            {/* Conversation UI */}
            <div className="space-y-3 text-[11px] bg-[#efeae2] p-3.5 rounded-2xl border border-slate-200/60 relative overflow-hidden"
              style={{
                backgroundImage: `url('/whatsappChatWallPaper.jpg')`,
                backgroundSize: '280px auto',
                backgroundRepeat: 'repeat',
              }}
            >
              <div className="absolute inset-0 bg-white/40 pointer-events-none" />

              {/* Owner Message */}
              <div className="relative flex justify-end">
                <div className="max-w-[85%] rounded-2xl rounded-tr-xs bg-[#d9fdd3] p-2.5 text-slate-800 shadow-xs">
                  <p className="leading-snug font-medium">Kal ka business kaisa tha?</p>
                  <div className="mt-0.5 flex justify-end gap-1 text-[8px] text-slate-500">
                    <span>09:14 AM</span>
                    <CheckCheck className="h-3 w-3 text-[#53bdeb]" />
                  </div>
                </div>
              </div>

              {/* Manager Response */}
              <div className="relative flex justify-start">
                <div className="max-w-[88%] rounded-2xl rounded-tl-xs bg-white p-3 text-slate-800 shadow-xs space-y-1.5">
                  <p className="leading-snug font-semibold text-slate-900">
                    Sales were <strong className="text-slate-900">₹1.84L</strong>. 3 payments are pending. 2 customers need follow-up.
                  </p>

                  {/* Specialist Agents Background Updates */}
                  <div className="text-[10px] space-y-1 pt-1 border-t border-slate-100 font-normal">
                    <div className="flex items-center gap-1.5 text-purple-700 bg-purple-50 p-1.5 rounded-lg border border-purple-100">
                      <Wallet className="h-3 w-3 shrink-0" />
                      <span>Finance Agent has reconciled today&apos;s billing.</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-amber-700 bg-amber-50 p-1.5 rounded-lg border border-amber-100">
                      <Package className="h-3 w-3 shrink-0" />
                      <span>Operation Agent flagged a stock issue.</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-pink-700 bg-pink-50 p-1.5 rounded-lg border border-pink-100">
                      <Share2 className="h-3 w-3 shrink-0" />
                      <span>Social Agent prepared a new-arrivals post.</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-4 text-center">
              <span className="text-[10.5px] text-slate-500 font-medium">
                The Manager Agent synthesizes your whole business into simple WhatsApp answers.
              </span>
            </div>
          </motion.div>

          {/* RIGHT: CUSTOMER → SALES AGENT CONVERSATION HERO */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="rounded-3xl border border-slate-200/90 bg-white p-5 sm:p-6 shadow-xl flex flex-col justify-between overflow-hidden relative"
          >
            {/* Header Badge */}
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-600 text-white">
                  <MessageCircle className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-xs font-extrabold text-slate-900 leading-tight">CUSTOMER &rarr; SALES AGENT</h3>
                  <span className="text-[10px] text-emerald-600 font-semibold block">WhatsApp Conversation</span>
                </div>
              </div>
              <span className="bg-emerald-50 text-emerald-700 text-[9px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full border border-emerald-100">
                24/7 Buyer Support
              </span>
            </div>

            {/* Conversation UI */}
            <div className="space-y-3 text-[11px] bg-[#efeae2] p-3.5 rounded-2xl border border-slate-200/60 relative overflow-hidden"
              style={{
                backgroundImage: `url('/whatsappChatWallPaper.jpg')`,
                backgroundSize: '280px auto',
                backgroundRepeat: 'repeat',
              }}
            >
              <div className="absolute inset-0 bg-white/40 pointer-events-none" />

              {/* Customer Message */}
              <div className="relative flex justify-end">
                <div className="max-w-[85%] rounded-2xl rounded-tr-xs bg-[#d9fdd3] p-2.5 text-slate-800 shadow-xs">
                  <p className="leading-snug font-medium">10 black kurtis chahiye. Size mix chalega?</p>
                  <div className="mt-0.5 flex justify-end gap-1 text-[8px] text-slate-500">
                    <span>10:24 AM</span>
                    <CheckCheck className="h-3 w-3 text-[#53bdeb]" />
                  </div>
                </div>
              </div>

              {/* Sales Agent Response */}
              <div className="relative flex justify-start">
                <div className="max-w-[88%] rounded-2xl rounded-tl-xs bg-white p-2.5 text-slate-800 shadow-xs">
                  <p className="leading-snug font-medium text-slate-900">
                    Yes. We have 7 ready to ship. I can prepare a quote for 7.
                  </p>
                  <div className="mt-0.5 text-[8px] text-slate-400">10:24 AM</div>
                </div>
              </div>

              {/* Quotation & Payment Snippet */}
              <div className="relative bg-white rounded-xl p-2.5 shadow-sm border border-slate-200/80 text-[10.5px]">
                <div className="flex justify-between font-bold text-slate-900 border-b border-slate-100 pb-1 mb-1">
                  <span>Quote #Q7842 (7 Black Kurtis)</span>
                  <span className="text-emerald-600">₹3,850</span>
                </div>
                <button className="w-full mt-1.5 rounded-lg bg-[#25d366] py-1 text-center font-bold text-white text-[10px] shadow-xs">
                  Pay Securely — ₹3,850
                </button>
              </div>
            </div>

            <div className="mt-4 text-center">
              <span className="text-[10.5px] text-slate-500 font-medium">
                Sales Agent responds instantly to buyer queries and delivers ready-to-pay invoices.
              </span>
            </div>
          </motion.div>

        </div>

      </div>
    </section>
  );
}
