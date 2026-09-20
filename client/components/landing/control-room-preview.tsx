'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowRight, TrendingUp } from 'lucide-react';

const WEEKLY_BARS = [42, 58, 46, 74, 62, 87, 69];
const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

export function ControlRoomPreview() {
  return (
    <section className="relative py-24 bg-[#F8FAFF] border-t border-slate-100 overflow-hidden">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Copy Column */}
          <div className="lg:col-span-5 space-y-6">
            <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-600 block">
              ONE CONVERSATION AWAY
            </span>

            <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
              Your whole business.<br />
              <span className="text-indigo-600">One conversation away.</span>
            </h2>

            <p className="text-base sm:text-lg text-slate-600 leading-relaxed font-normal">
              Ask what happened yesterday. Ask what needs attention. Ask what to do next. Manager Agent brings the right answer together.
            </p>

            <div>
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 text-sm font-bold text-indigo-600 hover:text-indigo-700 transition-colors"
              >
                <span>Explore Dashboard</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>

          {/* Right Dashboard Window Mockup Column */}
          <div className="lg:col-span-7">
            <div className="rounded-3xl border border-slate-200 bg-white shadow-2xl overflow-hidden">
              {/* Window Bar */}
              <div className="flex items-center gap-2 bg-slate-100/90 px-4 py-3 border-b border-slate-200 text-xs font-semibold text-slate-500">
                <div className="flex gap-1.5">
                  <span className="h-3 w-3 rounded-full bg-rose-400" />
                  <span className="h-3 w-3 rounded-full bg-amber-400" />
                  <span className="h-3 w-3 rounded-full bg-emerald-400" />
                </div>
                <span className="mx-auto font-mono text-[11px] text-slate-500">bizmate / manager briefing</span>
              </div>

              {/* Window Inner Layout */}
              <div className="grid grid-cols-1 sm:grid-cols-12 bg-white">
                {/* Sidebar */}
                <aside className="sm:col-span-3 bg-slate-50/80 p-4 border-r border-slate-200/80 space-y-4 text-xs font-semibold">
                  <strong className="text-slate-900 font-extrabold text-sm block mb-3">BizMate</strong>
                  <div className="space-y-1">
                    <span className="block px-3 py-1.5 rounded-lg bg-indigo-600 text-white font-bold">Overview</span>
                    <span className="block px-3 py-1.5 text-slate-600 hover:text-slate-900">Sales</span>
                    <span className="block px-3 py-1.5 text-slate-600 hover:text-slate-900">Stock</span>
                    <span className="block px-3 py-1.5 text-slate-600 hover:text-slate-900">Finance</span>
                    <span className="block px-3 py-1.5 text-slate-600 hover:text-slate-900">Social</span>
                  </div>
                </aside>

                {/* Dashboard Main Content */}
                <div className="sm:col-span-9 p-6 space-y-6">
                  <div>
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block font-mono">
                      TUESDAY, 20 SEPTEMBER
                    </span>
                    <h3 className="text-xl font-extrabold text-slate-900 mt-0.5">Good morning, Aamir</h3>
                    <p className="text-xs text-slate-500 font-medium">Here's what needs your attention.</p>
                  </div>

                  {/* Metrics Cards */}
                  <div className="grid grid-cols-3 gap-3">
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
                      <span className="text-[10px] text-slate-500 font-medium block">Sales yesterday</span>
                      <b className="text-base font-extrabold text-slate-900 block">₹1.84L</b>
                      <em className="text-[10px] text-emerald-600 font-bold not-italic">+12.4%</em>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
                      <span className="text-[10px] text-slate-500 font-medium block">Orders</span>
                      <b className="text-base font-extrabold text-slate-900 block">24</b>
                      <em className="text-[10px] text-emerald-600 font-bold not-italic">+8.2%</em>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
                      <span className="text-[10px] text-slate-500 font-medium block">To follow up</span>
                      <b className="text-base font-extrabold text-slate-900 block">5</b>
                      <em className="text-[10px] text-indigo-600 font-bold not-italic">Today</em>
                    </div>
                  </div>

                  {/* Weekly Chart */}
                  <div className="p-4 rounded-xl border border-slate-200/80 bg-slate-50/40 space-y-4">
                    <div className="flex justify-between items-center text-xs">
                      <b className="font-bold text-slate-900">Sales overview</b>
                      <span className="text-[11px] text-slate-500 font-semibold">This week ⌄</span>
                    </div>

                    <div className="flex items-end justify-between h-28 pt-4 px-2">
                      {WEEKLY_BARS.map((height, idx) => (
                        <div key={idx} className="flex-1 flex justify-center h-full items-end mx-1">
                          <div
                            className="w-full max-w-[20px] rounded-t-sm bg-gradient-to-t from-indigo-600 to-indigo-400"
                            style={{ height: `${height}%` }}
                          />
                        </div>
                      ))}
                    </div>

                    <div className="flex justify-between text-[10px] font-semibold text-slate-400 px-1 border-t border-slate-200/80 pt-2">
                      {DAYS.map((d) => (
                        <span key={d}>{d}</span>
                      ))}
                    </div>
                  </div>
                </div>

              </div>

            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
