'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sparkles,
  MessageSquare,
  PackageCheck,
  CreditCard,
  Bot,
  CheckCheck,
  ShieldCheck,
  FileText,
  ChevronLeft,
  Phone,
  Video,
  MoreVertical,
  Check
} from 'lucide-react';
import { Iphone3D } from './Iphone3D';

interface Moment {
  id: string;
  number: string;
  title: string;
  subtitle: string;
  badge: string;
  badgeColor: string;
  description: string;
  headerTitle: string;
  headerSub: string;
  headerIconColor: string;
}

const MOMENTS: Moment[] = [
  {
    id: 'moment-1',
    number: '01',
    title: 'Customer asks.',
    subtitle: 'INSTANT WHATSAPP RESPONSE',
    badge: 'WhatsApp Native',
    badgeColor: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    description: 'Sales Agent understands customer intent on WhatsApp and responds instantly with catalog availability.',
    headerTitle: 'BizMate Sales Agent',
    headerSub: 'online · WhatsApp Business',
    headerIconColor: 'bg-emerald-500',
  },
  {
    id: 'moment-2',
    number: '02',
    title: 'BizMate checks before you promise.',
    subtitle: 'STOCK & PRICING VERIFICATION',
    badge: 'Operation Agent',
    badgeColor: 'bg-blue-50 text-blue-700 border-blue-200',
    description: 'Stock, availability and pricing are checked autonomously before the customer gets a commitment.',
    headerTitle: 'BizMate Operation Agent',
    headerSub: 'stock verified · inventory sync',
    headerIconColor: 'bg-blue-500',
  },
  {
    id: 'moment-3',
    number: '03',
    title: 'Quote to payment.',
    subtitle: 'CHECKOUT & BILLING IN CHAT',
    badge: 'Finance Agent',
    badgeColor: 'bg-purple-50 text-purple-700 border-purple-200',
    description: 'Quote, UPI payment link and tax invoice move forward inside WhatsApp without repeating manual work.',
    headerTitle: 'BizMate Sales & Billing',
    headerSub: 'instant checkout · UPI ready',
    headerIconColor: 'bg-indigo-500',
  },
  {
    id: 'moment-4',
    number: '04',
    title: 'The rest keeps moving.',
    subtitle: 'COORDINATED BEHIND THE SCENES',
    badge: 'Manager Agent',
    badgeColor: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    description: 'Manager Agent coordinates while Finance, Social and Operation agents complete their work automatically.',
    headerTitle: 'BizMate Manager Agent',
    headerSub: 'owner briefing · 4 agents active',
    headerIconColor: 'bg-violet-600',
  },
];

export function MessageToMoneyWorkflow() {
  const [activeMoment, setActiveMoment] = useState(0);
  const momentRefs = useRef<(HTMLDivElement | null)[]>([]);

  // Natural scroll tracking with IntersectionObserver (No page locking)
  useEffect(() => {
    const observers: IntersectionObserver[] = [];

    momentRefs.current.forEach((el, index) => {
      if (!el) return;

      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting && entry.intersectionRatio >= 0.45) {
              setActiveMoment(index);
            }
          });
        },
        { threshold: [0.45, 0.75] }
      );

      observer.observe(el);
      observers.push(observer);
    });

    return () => {
      observers.forEach((obs) => obs.disconnect());
    };
  }, []);

  const currentMoment = MOMENTS[activeMoment];

  return (
    <section id="how-it-works" className="relative py-20 sm:py-28 bg-gradient-to-b from-[#F8FAFF] via-white to-[#F8FAFF] border-t border-slate-200/60 overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-1/3 left-0 w-96 h-96 bg-indigo-100/40 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute bottom-10 right-0 w-96 h-96 bg-emerald-100/30 rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-50 border border-indigo-200/80 text-indigo-700 text-[11px] font-extrabold uppercase tracking-wider shadow-xs">
            <Sparkles className="h-3.5 w-3.5 text-indigo-600 animate-pulse" />
            <span>THE WORK BIZMATE TAKES OFF YOUR PLATE</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900 leading-[1.15]">
            From the first WhatsApp message<br className="hidden sm:inline" /> to the final follow-up.
          </h2>

          <p className="text-base sm:text-lg text-slate-600 font-medium max-w-2xl mx-auto leading-relaxed">
            BizMate keeps sales, stock, payments and everyday business work moving while you stay focused on running the business.
          </p>
        </div>

        {/* Editorial Asymmetric Layout */}
        <div className="mt-14 grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
          
          {/* LEFT SIDE: 4 Business Moments Stepper List */}
          <div className="lg:col-span-6 space-y-4">
            {MOMENTS.map((moment, index) => {
              const isActive = activeMoment === index;

              return (
                <div
                  key={moment.id}
                  ref={(el) => { momentRefs.current[index] = el; }}
                  onClick={() => setActiveMoment(index)}
                  className={`cursor-pointer rounded-2xl border p-5 sm:p-6 transition-all duration-300 relative overflow-hidden ${
                    isActive
                      ? 'bg-white border-indigo-600/80 shadow-xl shadow-indigo-950/5 ring-2 ring-indigo-600/20 translate-x-1'
                      : 'bg-white/80 border-slate-200/90 hover:bg-white hover:border-slate-300 shadow-xs'
                  }`}
                >
                  {/* Left Active Accent Bar */}
                  {isActive && (
                    <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-gradient-to-b from-indigo-500 to-purple-600 rounded-l-2xl" />
                  )}

                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3.5">
                      <span className={`font-mono text-xs font-black px-2.5 py-1 rounded-lg shrink-0 ${
                        isActive ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-500'
                      }`}>
                        {moment.number}
                      </span>

                      <div className="space-y-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="text-base sm:text-lg font-extrabold text-slate-900 leading-snug">
                            {moment.title}
                          </h3>
                          <span className={`px-2 py-0.5 rounded-full border text-[10px] font-black uppercase tracking-wider ${moment.badgeColor}`}>
                            {moment.badge}
                          </span>
                        </div>

                        <p className="text-xs sm:text-sm text-slate-600 font-medium leading-relaxed">
                          {moment.description}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* RIGHT SIDE: 3D iPhone Product Theater */}
          <div className="lg:col-span-6 sticky top-24 flex justify-center w-full">
            <div className="w-full max-w-sm">
              <Iphone3D glowColor="rgba(99, 102, 241, 0.18)">
                <div className="h-full w-full bg-[#efeae2] font-sans text-slate-900 flex flex-col justify-between overflow-hidden select-none">
                  
                  {/* iPhone Top Status Bar */}
                  <div className="flex items-center justify-between bg-[#075e54] px-5 pt-3 pb-1 text-[11px] font-semibold text-white">
                    <span>9:41</span>
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px]">5G</span>
                      <div className="h-2.5 w-4 rounded-xs border border-white p-0.5">
                        <div className="h-full w-full bg-white rounded-2xs" />
                      </div>
                    </div>
                  </div>

                  {/* WhatsApp Dynamic Header */}
                  <header className="relative z-10 flex items-center gap-2.5 bg-[#075e54] px-3.5 py-2.5 text-white shadow-md">
                    <ChevronLeft className="h-4 w-4 opacity-90" />

                    <div className={`flex h-8 w-8 items-center justify-center rounded-full font-bold text-xs text-white shadow-inner ${currentMoment.headerIconColor}`}>
                      <Sparkles className="h-4 w-4 text-white" />
                    </div>

                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-1">
                        <p className="truncate text-xs font-bold leading-tight">{currentMoment.headerTitle}</p>
                        <ShieldCheck className="h-3.5 w-3.5 text-emerald-300 fill-emerald-400/20 shrink-0" />
                      </div>
                      <p className="text-[9.5px] text-white/80">{currentMoment.headerSub}</p>
                    </div>

                    <div className="flex items-center gap-2.5 text-white/90">
                      <Video className="h-4 w-4" />
                      <Phone className="h-4 w-4" />
                      <MoreVertical className="h-4 w-4" />
                    </div>
                  </header>

                  {/* WhatsApp Chat Wall & Active Screen Content */}
                  <main
                    className="relative flex-1 p-3.5 overflow-y-auto space-y-3 scrollbar-hide text-xs"
                    style={{
                      backgroundImage: `url('/whatsappChatWallPaper.jpg')`,
                      backgroundSize: '320px auto',
                      backgroundRepeat: 'repeat',
                    }}
                  >
                    {/* Date Divider */}
                    <div className="flex justify-center my-1">
                      <span className="rounded-md bg-white/80 backdrop-blur-xs px-2.5 py-1 text-[10px] font-bold text-slate-600 shadow-2xs">
                        Today · BizMate Automation
                      </span>
                    </div>

                    <AnimatePresence mode="wait">
                      <motion.div
                        key={currentMoment.id}
                        initial={{ opacity: 0, y: 8, scale: 0.98 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -8, scale: 0.98 }}
                        transition={{ duration: 0.25, ease: 'easeOut' }}
                        className="space-y-3"
                      >
                        {/* MOMENT 01: Customer Asks */}
                        {activeMoment === 0 && (
                          <>
                            {/* Customer Message */}
                            <div className="flex justify-start">
                              <div className="max-w-[85%] rounded-2xl rounded-tl-xs bg-white p-3 text-slate-900 shadow-xs border border-slate-200/60 space-y-1">
                                <p className="text-xs font-medium leading-relaxed">
                                  "10 black kurtis chahiye, size mix chalega?"
                                </p>
                                <span className="block text-[9px] text-slate-400 text-right">09:24 AM</span>
                              </div>
                            </div>

                            {/* Sales Agent Reply */}
                            <div className="flex justify-end">
                              <div className="max-w-[88%] rounded-2xl rounded-tr-xs bg-[#dcf8c6] p-3 text-slate-900 shadow-xs border border-emerald-200/60 space-y-1">
                                <div className="flex items-center gap-1 text-[10px] font-bold text-emerald-800 mb-1">
                                  <Sparkles className="h-3 w-3 text-emerald-600" />
                                  <span>BizMate Sales Agent</span>
                                </div>
                                <p className="text-xs font-medium leading-relaxed">
                                  Haan bilkul! Main instant stock check karke pricing aur billing summary aapko share karti hoon.
                                </p>
                                <div className="flex items-center justify-end gap-1 text-[9px] text-emerald-700">
                                  <span>09:24 AM</span>
                                  <CheckCheck className="h-3.5 w-3.5 text-blue-500" />
                                </div>
                              </div>
                            </div>

                            {/* Autonomous Intent Badge */}
                            <div className="flex justify-center pt-2">
                              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-600 text-white text-[10px] font-extrabold shadow-sm">
                                <Check className="h-3 w-3 stroke-[3]" />
                                Autonomous Catalog Match
                              </span>
                            </div>
                          </>
                        )}

                        {/* MOMENT 02: BizMate checks before you promise */}
                        {activeMoment === 1 && (
                          <>
                            {/* Customer Inquiry Context */}
                            <div className="flex justify-start">
                              <div className="max-w-[80%] rounded-2xl rounded-tl-xs bg-white p-2.5 text-slate-800 shadow-xs border border-slate-200/60 text-[11px]">
                                <span className="text-[9px] text-slate-400 font-bold block">BUYER INQUIRY</span>
                                "10 black kurtis, mixed sizes"
                              </div>
                            </div>

                            {/* Stock Check Verification Card */}
                            <div className="flex justify-end">
                              <div className="max-w-[92%] rounded-2xl rounded-tr-xs bg-[#dcf8c6] p-3 text-slate-900 shadow-xs border border-emerald-200/60 space-y-2">
                                <div className="flex items-center justify-between text-[10px] font-bold text-emerald-900 border-b border-emerald-300/60 pb-1">
                                  <span>STOCK &amp; PRICING CHECK</span>
                                  <span className="text-emerald-700 font-mono">09:25 AM</span>
                                </div>

                                <div className="bg-white/90 rounded-xl p-2.5 space-y-1.5 text-xs border border-emerald-200/80">
                                  <div className="flex justify-between items-center font-bold text-slate-900">
                                    <span>Black Kurti (Cotton)</span>
                                    <span className="text-emerald-600 text-[11px]">7 In Stock</span>
                                  </div>
                                  <div className="text-[10px] text-slate-500 flex justify-between">
                                    <span>Rate: ₹550 / piece</span>
                                    <span>Subtotal: ₹3,850</span>
                                  </div>
                                  <div className="pt-1 flex items-center gap-1 text-[10px] font-bold text-emerald-700">
                                    <Check className="h-3 w-3 text-emerald-600 stroke-[3]" />
                                    <span>Availability &amp; Price Verified</span>
                                  </div>
                                </div>

                                <div className="flex items-center justify-end gap-1 text-[9px] text-emerald-700">
                                  <span>09:25 AM</span>
                                  <CheckCheck className="h-3.5 w-3.5 text-blue-500" />
                                </div>
                              </div>
                            </div>
                          </>
                        )}

                        {/* MOMENT 03: Quote to payment */}
                        {activeMoment === 2 && (
                          <>
                            {/* WhatsApp Quote Card */}
                            <div className="flex justify-end">
                              <div className="max-w-[92%] rounded-2xl rounded-tr-xs bg-[#dcf8c6] p-3 text-slate-900 shadow-xs border border-emerald-200/60 space-y-2">
                                <div className="flex items-center justify-between text-[10px] font-bold text-emerald-900 border-b border-emerald-300/60 pb-1">
                                  <span>QUOTATION #Q-8910</span>
                                  <span className="text-emerald-700 font-mono">09:26 AM</span>
                                </div>

                                <div className="bg-white/90 rounded-xl p-2.5 space-y-1.5 text-xs border border-emerald-200/80">
                                  <div className="flex justify-between font-bold text-slate-900">
                                    <span>7 × Black Kurti</span>
                                    <span>₹3,850</span>
                                  </div>
                                  <div className="text-[10px] text-slate-500 flex justify-between">
                                    <span>GST &amp; Express Shipping</span>
                                    <span className="text-emerald-600 font-bold">Included</span>
                                  </div>
                                </div>

                                {/* Instant UPI Payment Button */}
                                <div className="pt-0.5">
                                  <div className="w-full py-2 px-3 rounded-xl bg-indigo-600 text-white font-extrabold text-xs text-center shadow-md flex items-center justify-center gap-1.5">
                                    <CreditCard className="h-3.5 w-3.5" />
                                    <span>Pay ₹3,850 via GPay / UPI</span>
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* Payment Confirmation & Tax Invoice Receipt */}
                            <div className="flex justify-end">
                              <div className="max-w-[92%] rounded-2xl bg-[#dcf8c6] p-3 text-slate-900 shadow-xs border border-emerald-200/60 space-y-2">
                                <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-900">
                                  <div className="h-4 w-4 rounded-full bg-emerald-600 text-white flex items-center justify-center text-[10px]">
                                    <Check className="h-3 w-3 stroke-[3]" />
                                  </div>
                                  <span>Payment Received — ₹3,850</span>
                                </div>

                                <div className="bg-white/90 rounded-xl p-2 flex items-center justify-between text-xs border border-emerald-200/80">
                                  <div className="flex items-center gap-2">
                                    <FileText className="h-4 w-4 text-indigo-600" />
                                    <div>
                                      <span className="font-bold text-slate-900 block text-[11px]">Tax_Invoice_INV-0891.pdf</span>
                                      <span className="text-[9px] text-slate-400">124 KB · Delivered</span>
                                    </div>
                                  </div>
                                </div>

                                <div className="flex items-center justify-end gap-1 text-[9px] text-emerald-700">
                                  <span>09:27 AM</span>
                                  <CheckCheck className="h-3.5 w-3.5 text-blue-500" />
                                </div>
                              </div>
                            </div>
                          </>
                        )}

                        {/* MOMENT 04: The rest keeps moving */}
                        {activeMoment === 3 && (
                          <>
                            {/* Manager Agent Briefing Bubble */}
                            <div className="flex justify-end">
                              <div className="max-w-[95%] rounded-2xl rounded-tr-xs bg-[#dcf8c6] p-3 text-slate-900 shadow-xs border border-emerald-200/60 space-y-2">
                                <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-950 border-b border-emerald-300/60 pb-1">
                                  <Bot className="h-4 w-4 text-indigo-600" />
                                  <span>BizMate Manager Briefing</span>
                                </div>

                                <p className="text-xs font-medium leading-relaxed text-slate-800">
                                  Order #0891 (₹3,850) completed! Here is what was handled automatically:
                                </p>

                                <div className="space-y-1.5 text-[11px] font-medium text-slate-700">
                                  <div className="flex items-start gap-1.5 bg-white/80 p-1.5 rounded-lg border border-emerald-200/60">
                                    <span className="font-bold text-indigo-600 shrink-0">📦 Stock:</span>
                                    <span>Black Kurti inventory updated (-7).</span>
                                  </div>
                                  <div className="flex items-start gap-1.5 bg-white/80 p-1.5 rounded-lg border border-emerald-200/60">
                                    <span className="font-bold text-emerald-600 shrink-0">🧾 Ledger:</span>
                                    <span>Payment reconciled &amp; GST entry added.</span>
                                  </div>
                                  <div className="flex items-start gap-1.5 bg-white/80 p-1.5 rounded-lg border border-emerald-200/60">
                                    <span className="font-bold text-purple-600 shrink-0">📱 Social:</span>
                                    <span>Post scheduled on Instagram for 6 PM.</span>
                                  </div>
                                </div>

                                <div className="flex items-center justify-end gap-1 text-[9px] text-emerald-700">
                                  <span>09:28 AM</span>
                                  <CheckCheck className="h-3.5 w-3.5 text-blue-500" />
                                </div>
                              </div>
                            </div>
                          </>
                        )}
                      </motion.div>
                    </AnimatePresence>
                  </main>

                  {/* Bottom Footer Bar */}
                  <div className="bg-white px-3 py-2 border-t border-slate-200 flex items-center justify-between text-[10px] text-slate-500 font-bold">
                    <span>BizMate OS Active</span>
                    <span className="text-emerald-600 font-mono">● 4 Agents Connected</span>
                  </div>

                </div>
              </Iphone3D>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
