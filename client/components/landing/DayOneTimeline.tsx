'use client';

import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

const TIMELINE_EVENTS = [
  {
    time: '08:42 AM',
    title: 'Customer message arrives.',
    description: 'A new order lands on WhatsApp.',
    color: 'bg-emerald-500',
    tagColor: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  },
  {
    time: '08:44 AM',
    title: 'Sales Agent responds.',
    description: 'The customer gets a quick, clear answer.',
    color: 'bg-blue-500',
    tagColor: 'bg-blue-50 text-blue-700 border-blue-200',
  },
  {
    time: '09:05 AM',
    title: 'Manager Agent briefs the owner.',
    description: 'Sales, payments and priorities in one view.',
    color: 'bg-indigo-500',
    tagColor: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  },
  {
    time: '10:20 AM',
    title: 'Operation Agent surfaces a stock issue.',
    description: 'A vendor update is ready before the next quote.',
    color: 'bg-amber-500',
    tagColor: 'bg-amber-50 text-amber-700 border-amber-200',
  },
  {
    time: '02:40 PM',
    title: 'A follow-up is surfaced.',
    description: 'No promising customer slips through the cracks.',
    color: 'bg-emerald-500',
    tagColor: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  },
  {
    time: '06:30 PM',
    title: 'End-of-day summary.',
    description: 'The day closes with clarity, not a mental checklist.',
    color: 'bg-blue-500',
    tagColor: 'bg-blue-50 text-blue-700 border-blue-200',
  }
];

export function DayOneTimeline() {
  return (
    <section className="relative py-24 bg-[#F8FAFF] border-t border-slate-100 overflow-hidden">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3">
          <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-600 block">
            A DAY WITH BIZMATE
          </span>

          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
            What changes when the busywork<br /> stops living in your head?
          </h2>
        </div>

        {/* Vertical Timeline Layout */}
        <div className="mt-16 max-w-4xl mx-auto relative">
          
          {/* Vertical Progress Line */}
          <div className="absolute top-4 bottom-4 left-1/2 -ml-0.5 w-0.5 bg-slate-200 rounded-full" />

          <div className="space-y-12">
            {TIMELINE_EVENTS.map((event, idx) => {
              const isEven = idx % 2 === 0;

              return (
                <motion.div
                  key={event.time}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: idx * 0.08 }}
                  className={`relative flex items-center justify-between ${
                    isEven ? 'flex-row-reverse' : ''
                  }`}
                >
                  
                  {/* Timeline Center Dot Node */}
                  <div className={`absolute left-1/2 -translate-x-1/2 flex h-5 w-5 items-center justify-center rounded-full bg-white border-2 border-slate-300 z-10`}>
                    <div className={`h-2.5 w-2.5 rounded-full ${event.color}`} />
                  </div>

                  {/* Timeline Card */}
                  <div className={`w-full sm:w-[45%] ${isEven ? 'text-right' : 'text-left'}`}>
                    <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs space-y-2 hover:shadow-md transition-shadow">
                      <div className={`flex items-center gap-2 text-xs font-bold ${isEven ? 'justify-end' : 'justify-start'}`}>
                        <time className="font-mono text-indigo-600">{event.time}</time>
                        <span className={`px-2 py-0.5 rounded-full border text-[9px] font-extrabold uppercase ${event.tagColor}`}>
                          PREVIEW
                        </span>
                      </div>

                      <h3 className="text-base font-bold text-slate-900">{event.title}</h3>
                      <p className="text-xs text-slate-500 font-medium leading-relaxed">{event.description}</p>
                    </div>
                  </div>

                  {/* Empty Spacer */}
                  <div className="hidden sm:block w-[45%]" />

                </motion.div>
              );
            })}
          </div>

        </div>

      </div>
    </section>
  );
}
