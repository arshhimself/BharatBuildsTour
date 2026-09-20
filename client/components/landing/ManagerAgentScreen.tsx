'use client';

import React from 'react';
import {
  TrendingUp,
  PackageX,
  CreditCard,
  FileClock,
  Truck,
  Users,
  Sparkles,
  ChevronRight,
  BellRing,
} from 'lucide-react';

export function ManagerAgentScreen() {
  return (
    <div className="flex h-full w-full flex-col bg-[#f8faff] font-sans text-slate-900 select-none">
      {/* Top Status Bar Placeholder */}
      <div className="flex items-center justify-between bg-white px-5 pt-3 pb-1 text-[11px] font-semibold text-slate-900 border-b border-slate-100">
        <span>9:41</span>
        <div className="flex items-center gap-1.5">
          <span className="text-[10px]">5G</span>
          <div className="h-2.5 w-4 rounded-sm border border-slate-800 p-0.5">
            <div className="h-full w-full bg-slate-900 rounded-xs" />
          </div>
        </div>
      </div>

      {/* Header */}
      <header className="flex items-center justify-between bg-white px-4 py-2.5 border-b border-slate-100 shadow-xs">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-indigo-600 text-white font-bold text-xs shadow-xs">
            ⚡
          </div>
          <div>
            <h2 className="text-xs font-bold leading-tight text-slate-900">BizMate</h2>
            <p className="text-[9px] font-medium text-indigo-600">Manager Agent</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative">
            <BellRing className="h-4 w-4 text-slate-600" />
            <span className="absolute -top-0.5 -right-0.5 h-1.5 w-1.5 rounded-full bg-rose-500" />
          </div>
        </div>
      </header>

      {/* Content Area */}
      <main className="flex-1 overflow-y-auto p-3 space-y-2.5 scrollbar-hide text-[11px]">
        {/* Morning Briefing Banner */}
        <div className="rounded-2xl bg-gradient-to-r from-indigo-600 via-indigo-700 to-indigo-800 p-3 text-white shadow-md">
          <div className="flex items-center justify-between">
            <span className="inline-flex items-center gap-1 rounded-full bg-white/20 px-2 py-0.5 text-[9px] font-medium text-white">
              <Sparkles className="h-2.5 w-2.5 text-amber-300" />
              Morning Briefing
            </span>
            <span className="text-[9px] text-white/70">Today</span>
          </div>

          <h3 className="mt-2 text-sm font-bold leading-snug">Good morning 👋</h3>
          <p className="text-[10px] text-indigo-100 mt-0.5 leading-relaxed">
            Here is what needs your attention today across your store operations.
          </p>
        </div>

        {/* Quick Summary Grid */}
        <div className="grid grid-cols-2 gap-2">
          {/* Sales Card */}
          <div className="rounded-xl bg-white p-2.5 border border-slate-100 shadow-xs">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[9.5px] font-medium">Sales Yesterday</span>
              <TrendingUp className="h-3.5 w-3.5 text-emerald-500" />
            </div>
            <p className="mt-1 text-sm font-extrabold text-slate-900">₹1.84L</p>
            <span className="text-[8.5px] font-semibold text-emerald-600">↑ 12% vs prev day</span>
          </div>

          {/* Low Stock Card */}
          <div className="rounded-xl bg-amber-50/70 p-2.5 border border-amber-200/60 shadow-xs">
            <div className="flex items-center justify-between text-amber-800">
              <span className="text-[9.5px] font-medium">Low Stock</span>
              <PackageX className="h-3.5 w-3.5 text-amber-600" />
            </div>
            <p className="mt-1 text-sm font-extrabold text-amber-900">7 items</p>
            <span className="text-[8.5px] font-semibold text-amber-700">Action required</span>
          </div>
        </div>

        {/* Action Items List */}
        <div className="space-y-1.5">
          <p className="text-[9.5px] font-bold tracking-wider uppercase text-slate-400 px-1">
            Important Updates
          </p>

          {/* Item 1: Pending Payments */}
          <div className="flex items-center justify-between rounded-xl bg-white p-2.5 border border-slate-100 shadow-xs hover:border-slate-200 transition-colors">
            <div className="flex items-center gap-2.5">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
                <CreditCard className="h-3.5 w-3.5" />
              </div>
              <div>
                <p className="text-[10.5px] font-semibold text-slate-900 leading-tight">Pending Payments</p>
                <p className="text-[9px] text-slate-500">3 payments · ₹42,500 total</p>
              </div>
            </div>
            <ChevronRight className="h-3.5 w-3.5 text-slate-400" />
          </div>

          {/* Item 2: Expiring Quotes */}
          <div className="flex items-center justify-between rounded-xl bg-white p-2.5 border border-slate-100 shadow-xs">
            <div className="flex items-center gap-2.5">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                <FileClock className="h-3.5 w-3.5" />
              </div>
              <div>
                <p className="text-[10.5px] font-semibold text-slate-900 leading-tight">Quotes Expiring</p>
                <p className="text-[9px] text-slate-500">2 quotes expiring in next 24h</p>
              </div>
            </div>
            <ChevronRight className="h-3.5 w-3.5 text-slate-400" />
          </div>

          {/* Item 3: Vendor Update */}
          <div className="flex items-center justify-between rounded-xl bg-white p-2.5 border border-slate-100 shadow-xs">
            <div className="flex items-center gap-2.5">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-sky-50 text-sky-600">
                <Truck className="h-3.5 w-3.5" />
              </div>
              <div>
                <p className="text-[10.5px] font-semibold text-slate-900 leading-tight">Vendor Price Update</p>
                <p className="text-[9px] text-slate-500">Price updated from 2 vendors</p>
              </div>
            </div>
            <ChevronRight className="h-3.5 w-3.5 text-slate-400" />
          </div>

          {/* Item 4: Customer Follow-ups */}
          <div className="flex items-center justify-between rounded-xl bg-white p-2.5 border border-slate-100 shadow-xs">
            <div className="flex items-center gap-2.5">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-purple-50 text-purple-600">
                <Users className="h-3.5 w-3.5" />
              </div>
              <div>
                <p className="text-[10.5px] font-semibold text-slate-900 leading-tight">Customer Follow-ups</p>
                <p className="text-[9px] text-slate-500">5 customers pending reply</p>
              </div>
            </div>
            <ChevronRight className="h-3.5 w-3.5 text-slate-400" />
          </div>
        </div>
      </main>
    </div>
  );
}
