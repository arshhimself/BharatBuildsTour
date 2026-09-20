'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Users, 
  Sparkles, 
  Wallet, 
  Share2, 
  Package, 
  MessageCircle, 
  ArrowRight, 
  CheckCircle2,
  ChevronDown
} from 'lucide-react';

const AGENTS = [
  {
    id: 'manager',
    name: 'Manager Agent',
    role: 'briefings & decisions',
    icon: Sparkles,
    color: 'bg-indigo-600 text-white border-indigo-600',
    description: 'Summarizes yesterday’s performance, tracks low stock alerts, surface pending payments, and coordinates sub-agents.',
  },
  {
    id: 'finance',
    name: 'Finance Agent',
    role: 'bills & balances',
    icon: Wallet,
    color: 'bg-purple-600 text-white border-purple-600',
    description: 'Auto-reconciles bank webhooks, tracks outstanding receivables, and updates tax invoice ledgers.',
  },
  {
    id: 'social',
    name: 'Social Agent',
    role: 'content & campaigns',
    icon: Share2,
    color: 'bg-pink-600 text-white border-pink-600',
    description: 'Turns new inventory arrivals into Instagram stories, posts, and WhatsApp promotional broadcasts.',
  },
  {
    id: 'operation',
    name: 'Operation Agent',
    role: 'stock & vendors',
    icon: Package,
    color: 'bg-amber-600 text-white border-amber-600',
    description: 'Monitors real-time stock levels, generates courier shipping labels, and drafts vendor re-orders.',
  },
  {
    id: 'sales',
    name: 'Sales Agent',
    role: 'customer conversations',
    icon: MessageCircle,
    color: 'bg-emerald-600 text-white border-emerald-600',
    description: 'Handles 24/7 buyer chats on WhatsApp, answers stock availability queries, and delivers payment links.',
  }
];

export function MultiAgentSection() {
  const [activeAgentId, setActiveAgentId] = useState<string | null>('manager');

  const activeAgent = AGENTS.find((a) => a.id === activeAgentId);

  return (
    <section id="ai-team" className="relative py-24 bg-[#F8FAFF] border-t border-slate-100 overflow-hidden">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3">
          <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-600 block">
            THE AI TEAM
          </span>

          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
            You talk to one.<br />
            <span className="text-indigo-600">Your AI team handles the rest.</span>
          </h2>

          <p className="text-base sm:text-lg text-slate-600 font-normal max-w-2xl mx-auto">
            You do not need to talk to five systems. You talk to Manager Agent. Your customers talk to Sales Agent. The specialists work behind the scenes.
          </p>
        </div>

        {/* Clean Node Hierarchy Canvas */}
        <div className="mt-16 max-w-4xl mx-auto rounded-3xl border border-slate-200 bg-white p-8 sm:p-12 shadow-xl relative overflow-hidden">
          
          {/* Node Diagram Grid */}
          <div className="relative space-y-10 z-10">
            
            {/* Top Level: Owner */}
            <div className="flex justify-center">
              <div className="flex items-center gap-3 rounded-2xl border border-slate-900 bg-slate-900 px-6 py-3 text-white shadow-md">
                <Users className="h-5 w-5 text-indigo-400" />
                <div>
                  <h4 className="text-xs font-extrabold text-white">You</h4>
                  <p className="text-[10px] text-slate-400 font-medium">the owner</p>
                </div>
              </div>
            </div>

            {/* Connecting Vertical Line */}
            <div className="flex justify-center -my-6">
              <div className="w-0.5 h-10 bg-indigo-300 animate-pulse" />
            </div>

            {/* Manager Agent Hub Node */}
            <div className="flex justify-center">
              <button
                onClick={() => setActiveAgentId(activeAgentId === 'manager' ? null : 'manager')}
                className={`flex items-center gap-3 rounded-2xl border-2 px-6 py-3.5 transition-all shadow-md cursor-pointer ${
                  activeAgentId === 'manager'
                    ? 'border-indigo-600 bg-indigo-50 text-slate-900 ring-2 ring-indigo-600/20'
                    : 'border-indigo-200 bg-white hover:border-indigo-400'
                }`}
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white">
                  <Sparkles className="h-5 w-5" />
                </div>
                <div className="text-left">
                  <h4 className="text-sm font-extrabold text-slate-900">Manager Agent</h4>
                  <p className="text-[11px] text-slate-500 font-medium">briefings & decisions</p>
                </div>
              </button>
            </div>

            {/* Connecting Horizontal Line to 3 Sub-Agents */}
            <div className="flex justify-around items-center max-w-2xl mx-auto -my-6">
              <div className="w-1/3 h-0.5 bg-indigo-200" />
              <div className="w-1/3 h-0.5 bg-indigo-200" />
            </div>

            {/* 3 Specialist Sub-Agent Nodes */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-3xl mx-auto">
              
              {/* Finance Agent */}
              <button
                onClick={() => setActiveAgentId(activeAgentId === 'finance' ? null : 'finance')}
                className={`p-4 rounded-2xl border text-center transition-all cursor-pointer ${
                  activeAgentId === 'finance'
                    ? 'border-purple-600 bg-purple-50 ring-2 ring-purple-600/20 shadow-md'
                    : 'border-slate-200 bg-white hover:border-purple-300'
                }`}
              >
                <div className="mx-auto flex h-9 w-9 items-center justify-center rounded-xl bg-purple-600 text-white mb-2">
                  <Wallet className="h-4 w-4" />
                </div>
                <h4 className="text-xs font-bold text-slate-900">Finance Agent</h4>
                <p className="text-[10px] text-slate-500 mt-0.5 font-medium">bills & balances</p>
              </button>

              {/* Social Agent */}
              <button
                onClick={() => setActiveAgentId(activeAgentId === 'social' ? null : 'social')}
                className={`p-4 rounded-2xl border text-center transition-all cursor-pointer ${
                  activeAgentId === 'social'
                    ? 'border-pink-600 bg-pink-50 ring-2 ring-pink-600/20 shadow-md'
                    : 'border-slate-200 bg-white hover:border-pink-300'
                }`}
              >
                <div className="mx-auto flex h-9 w-9 items-center justify-center rounded-xl bg-pink-600 text-white mb-2">
                  <Share2 className="h-4 w-4" />
                </div>
                <h4 className="text-xs font-bold text-slate-900">Social Agent</h4>
                <p className="text-[10px] text-slate-500 mt-0.5 font-medium">content & campaigns</p>
              </button>

              {/* Operation Agent */}
              <button
                onClick={() => setActiveAgentId(activeAgentId === 'operation' ? null : 'operation')}
                className={`p-4 rounded-2xl border text-center transition-all cursor-pointer ${
                  activeAgentId === 'operation'
                    ? 'border-amber-600 bg-amber-50 ring-2 ring-amber-600/20 shadow-md'
                    : 'border-slate-200 bg-white hover:border-amber-300'
                }`}
              >
                <div className="mx-auto flex h-9 w-9 items-center justify-center rounded-xl bg-amber-600 text-white mb-2">
                  <Package className="h-4 w-4" />
                </div>
                <h4 className="text-xs font-bold text-slate-900">Operation Agent</h4>
                <p className="text-[10px] text-slate-500 mt-0.5 font-medium">stock & vendors</p>
              </button>

            </div>

            {/* External Customer Path Row */}
            <div className="pt-6 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-center gap-4">
              <div className="flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-4 py-2 text-xs font-bold text-emerald-800">
                <MessageCircle className="h-4 w-4 text-emerald-600" />
                <span>Customers</span>
                <span className="text-[10px] font-normal text-emerald-600">talk to Sales Agent</span>
              </div>

              <ArrowRight className="h-4 w-4 text-slate-400 hidden sm:block" />

              <button
                onClick={() => setActiveAgentId(activeAgentId === 'sales' ? null : 'sales')}
                className={`flex items-center gap-2.5 rounded-full border px-4 py-2 transition-all cursor-pointer ${
                  activeAgentId === 'sales'
                    ? 'border-emerald-600 bg-emerald-100 text-emerald-950 ring-2 ring-emerald-600/20'
                    : 'border-emerald-200 bg-white hover:border-emerald-400 text-slate-900'
                }`}
              >
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-600 text-white">
                  <MessageCircle className="h-3.5 w-3.5" />
                </div>
                <span className="text-xs font-bold">Sales Agent</span>
              </button>
            </div>

          </div>

          {/* Active Agent Detail Panel Expansion */}
          <AnimatePresence>
            {activeAgent && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
                className="mt-8 pt-6 border-t border-slate-100 text-center"
              >
                <div className="inline-flex items-center gap-2 rounded-full bg-slate-900 px-3 py-1 text-[10px] font-bold text-white mb-2">
                  <activeAgent.icon className="h-3 w-3 text-indigo-400" />
                  <span>{activeAgent.name} Role Details</span>
                </div>
                <p className="text-xs sm:text-sm text-slate-600 max-w-xl mx-auto font-normal leading-relaxed">
                  {activeAgent.description}
                </p>

                <div className="mt-4">
                  <Link
                    href="/agent-office"
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-indigo-600 hover:text-indigo-700 transition-colors"
                  >
                    <span>Explore AI Team</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

        </div>

      </div>
    </section>
  );
}
