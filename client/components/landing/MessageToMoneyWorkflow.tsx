'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MessageSquare, 
  Sparkles, 
  Package, 
  FileText, 
  CreditCard, 
  CheckCircle2, 
  ShieldCheck, 
  Check,
  ArrowRight
} from 'lucide-react';
import { Iphone3D } from './Iphone3D';

const WORKFLOW_STEPS = [
  {
    id: '01',
    title: 'Customer message',
    subtitle: 'WhatsApp Customer Message',
    icon: MessageSquare,
    badge: 'WhatsApp Native',
    description: 'A customer asks for a product on WhatsApp: "10 black kurtis chahiye, size mix chalega?"',
    screenType: 'inquiry',
    chatData: {
      user: 'Customer',
      time: '09:24 AM',
      text: '10 black kurtis chahiye, size mix chalega?',
    }
  },
  {
    id: '02',
    title: 'Sales Agent understands',
    subtitle: 'Autonomous Catalog Match',
    icon: Sparkles,
    badge: 'AI Sales Agent',
    description: 'The request becomes a clear product and quantity. Sales Agent matches inventory instantly.',
    screenType: 'understanding',
    chatData: {
      agent: 'BizMate Sales Agent',
      time: '09:24 AM',
      text: 'Sure! I\'ll check the available stock and current pricing.',
    }
  },
  {
    id: '03',
    title: 'Check stock',
    subtitle: 'Inventory Allocation',
    icon: Package,
    badge: 'Operation Agent',
    description: 'Availability and pricing are confirmed: "We have 7 ready to ship right now."',
    screenType: 'inventory',
    stockInfo: {
      itemName: 'Black Kurti',
      oldStock: 12,
      newStock: 7,
      status: '7 Ready to Ship'
    }
  },
  {
    id: '04',
    title: 'Create quote',
    subtitle: 'Automated Tax Compliance',
    icon: FileText,
    badge: 'GST Ready',
    description: 'Quotation generated: 7 × Black Kurti total ₹3,850 (delivery included).',
    screenType: 'quote',
    invoiceData: {
      number: 'QUOTE PREPARED',
      item: '7 × Black Kurti',
      delivery: 'Included',
      total: '₹3,850'
    }
  },
  {
    id: '05',
    title: 'Manager approval',
    subtitle: 'Autonomous Policy Guard',
    icon: ShieldCheck,
    badge: 'Manager Agent',
    description: 'Manager Agent verifies policy, checks profit margin, and approves order for dispatch.',
    screenType: 'manager_approval',
    approvalStatus: 'APPROVED — Margin 38.4%'
  },
  {
    id: '06',
    title: 'Send payment link',
    subtitle: 'Instant Checkout URL',
    icon: CreditCard,
    badge: 'UPI / Razorpay',
    description: 'A secure payment link (₹3,850) is sent directly inside the WhatsApp chat.',
    screenType: 'payment_link',
    paymentLink: 'https://pay.bizmate.app/q/7-black-kurti'
  },
  {
    id: '07',
    title: 'Payment received',
    subtitle: 'Automated Bank Webhook',
    icon: CheckCircle2,
    badge: 'Auto Reconciled',
    description: 'Payment is confirmed automatically via UPI bank webhook. Account ledger updated.',
    screenType: 'payment_done',
    status: 'PAID — ₹3,850 via UPI'
  },
  {
    id: '08',
    title: 'Invoice shared',
    subtitle: 'PDF Delivered to Customer',
    icon: FileText,
    badge: 'WhatsApp Receipt',
    description: 'Official tax invoice PDF and delivery tracking link delivered directly to buyer on WhatsApp.',
    screenType: 'invoice_shared',
    invoiceNumber: 'INV-2026-0891.pdf'
  }
];

export function MessageToMoneyWorkflow() {
  const [activeStep, setActiveStep] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-progress active step on scroll when container is in view
  useEffect(() => {
    function handleScroll() {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const windowHeight = window.innerHeight;

      if (rect.top < windowHeight * 0.8 && rect.bottom > windowHeight * 0.2) {
        const totalHeight = rect.height - windowHeight * 0.5;
        const scrolled = Math.max(0, windowHeight * 0.5 - rect.top);
        const progress = Math.min(1, scrolled / totalHeight);
        const stepIndex = Math.min(
          WORKFLOW_STEPS.length - 1,
          Math.floor(progress * WORKFLOW_STEPS.length)
        );
        setActiveStep(stepIndex);
      }
    }

    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const currentStep = WORKFLOW_STEPS[activeStep];

  return (
    <section id="how-it-works" ref={containerRef} className="relative py-24 bg-[#F8FAFF] border-t border-slate-100 overflow-hidden">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3">
          <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-600 block">
            WATCH BIZMATE THINK
          </span>

          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
            From one customer message<br /> to a completed order.
          </h2>

          <p className="text-base sm:text-lg text-slate-600 font-normal">
            One conversation. Every step coordinated behind the scenes.
          </p>
        </div>

        {/* Story Layout: Left Stepper + Right Sticky Phone */}
        <div className="mt-16 grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
          
          {/* Left Side: Editorial Steps List */}
          <div className="lg:col-span-6 space-y-3">
            {WORKFLOW_STEPS.map((step, index) => {
              const Icon = step.icon;
              const isActive = activeStep === index;

              return (
                <div
                  key={step.id}
                  onClick={() => setActiveStep(index)}
                  className={`cursor-pointer rounded-2xl border p-5 transition-all duration-300 ${
                    isActive
                      ? 'border-indigo-600 bg-white shadow-xl shadow-indigo-900/5 ring-1 ring-indigo-600/20'
                      : 'border-slate-200/80 bg-white/70 hover:bg-white hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-4">
                      <span className={`font-mono text-sm font-bold ${isActive ? 'text-indigo-600' : 'text-slate-400'}`}>
                        {step.id}
                      </span>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="text-base font-bold text-slate-900">{step.title}</h3>
                          {isActive && (
                            <span className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-[10px] font-extrabold text-indigo-600">
                              {step.badge}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-slate-500 font-medium mt-0.5">{step.description}</p>
                      </div>
                    </div>

                    <div className="shrink-0 pt-0.5">
                      {isActive ? (
                        <div className="h-2.5 w-2.5 rounded-full bg-indigo-600 animate-pulse" />
                      ) : (
                        <span className="text-[11px] text-slate-400 font-semibold">{step.id}/08</span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right Side: Sticky 3D Phone Screen showing real-time step transformation */}
          <div className="lg:col-span-6 sticky top-28 flex justify-center">
            <div className="w-full max-w-sm">
              <Iphone3D glowColor="rgba(99, 102, 241, 0.15)">
                <div className="h-full bg-slate-950 text-white flex flex-col justify-between p-4 overflow-hidden relative">
                  
                  {/* Phone Header Bar */}
                  <div className="flex items-center justify-between pb-3 border-b border-slate-800 text-xs text-slate-400 font-semibold">
                    <div className="flex items-center gap-2">
                      <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                      <span>BizMate Sales OS</span>
                    </div>
                    <span className="text-indigo-400 font-bold font-mono">Step {currentStep.id} of 08</span>
                  </div>

                  {/* Phone Body Visual */}
                  <div className="my-auto py-4">
                    <AnimatePresence mode="wait">
                      <motion.div
                        key={currentStep.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.3 }}
                        className="space-y-4"
                      >
                        {/* Step Icon Badge */}
                        <div className="flex justify-center">
                          <div className="h-12 w-12 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shadow-inner">
                            {React.createElement(currentStep.icon, { className: 'h-6 w-6' })}
                          </div>
                        </div>

                        {/* Visual Card per Step */}
                        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4 shadow-lg">
                          <div className="text-center mb-3">
                            <span className="text-[10px] uppercase tracking-wider font-extrabold text-indigo-400">
                              {currentStep.subtitle}
                            </span>
                            <h4 className="text-base font-bold text-white mt-0.5">{currentStep.title}</h4>
                          </div>

                          {/* Specific mockup contents */}
                          {currentStep.screenType === 'inquiry' && (
                            <div className="rounded-xl bg-slate-950 p-3 text-xs space-y-2 border border-slate-800">
                              <div className="flex items-center justify-between text-[10px] text-slate-400">
                                <span>{currentStep.chatData?.user}</span>
                                <span>{currentStep.chatData?.time}</span>
                              </div>
                              <p className="text-slate-200 bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                                "{currentStep.chatData?.text}"
                              </p>
                              <div className="flex justify-end">
                                <span className="inline-flex items-center gap-1 rounded bg-amber-500/10 px-2 py-0.5 text-[10px] font-semibold text-amber-400">
                                  Pending Response
                                </span>
                              </div>
                            </div>
                          )}

                          {currentStep.screenType === 'understanding' && (
                            <div className="rounded-xl bg-emerald-950/40 p-3 text-xs space-y-2 border border-emerald-500/30">
                              <div className="flex items-center justify-between text-[10px] text-emerald-400 font-bold">
                                <span>{currentStep.chatData?.agent}</span>
                                <span>⚡ 0.8s</span>
                              </div>
                              <p className="text-emerald-100 bg-emerald-900/30 p-2.5 rounded-lg border border-emerald-800/50">
                                "{currentStep.chatData?.text}"
                              </p>
                              <div className="flex justify-between items-center text-[10px] text-emerald-400 font-semibold">
                                <span>Match Confidence: 99.4%</span>
                                <span className="text-emerald-300">Ready to Reserve</span>
                              </div>
                            </div>
                          )}

                          {currentStep.screenType === 'inventory' && (
                            <div className="rounded-xl bg-slate-950 p-3 text-xs space-y-3 border border-slate-800">
                              <div className="flex justify-between items-center">
                                <span className="font-bold text-white">{currentStep.stockInfo?.itemName}</span>
                                <span className="text-[10px] font-mono text-indigo-400">7 Ready to Ship</span>
                              </div>
                              <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800">
                                <div className="bg-emerald-500 h-full w-[70%]" />
                              </div>
                              <div className="text-[10px] text-center text-emerald-400 font-semibold">
                                ✓ Availability and pricing confirmed
                              </div>
                            </div>
                          )}

                          {currentStep.screenType === 'quote' && (
                            <div className="rounded-xl bg-slate-950 p-3 text-xs space-y-2 border border-slate-800">
                              <div className="flex justify-between text-[10px] text-slate-400 pb-1 border-b border-slate-800">
                                <span>{currentStep.invoiceData?.number}</span>
                                <span className="text-emerald-400 font-bold">GST INCLUDED</span>
                              </div>
                              <div className="space-y-1 text-slate-300">
                                <div className="flex justify-between">
                                  <span>Item:</span>
                                  <span>{currentStep.invoiceData?.item}</span>
                                </div>
                                <div className="flex justify-between text-slate-400">
                                  <span>Delivery:</span>
                                  <span>{currentStep.invoiceData?.delivery}</span>
                                </div>
                                <div className="flex justify-between font-bold text-white text-sm pt-2 border-t border-slate-800">
                                  <span>Total:</span>
                                  <span className="text-indigo-400">{currentStep.invoiceData?.total}</span>
                                </div>
                              </div>
                            </div>
                          )}

                          {currentStep.screenType === 'manager_approval' && (
                            <div className="rounded-xl bg-slate-950 p-3 text-xs space-y-3 border border-slate-800">
                              <div className="flex justify-between items-center text-slate-400 text-[10px]">
                                <span>Policy Verification</span>
                                <span className="text-emerald-400 font-bold">Passed</span>
                              </div>
                              <div className="bg-indigo-950/60 p-3 rounded-lg border border-indigo-800/40 text-center">
                                <span className="text-[10px] text-indigo-300 block">Manager Agent Status</span>
                                <span className="text-sm font-extrabold text-white">{currentStep.approvalStatus}</span>
                              </div>
                            </div>
                          )}

                          {currentStep.screenType === 'payment_link' && (
                            <div className="rounded-xl bg-indigo-950/50 p-3 text-xs space-y-3 border border-indigo-500/30 text-center">
                              <div className="inline-flex items-center gap-1 text-[10px] font-bold text-indigo-300 uppercase tracking-wider">
                                <CreditCard className="h-3 w-3" />
                                UPI / Razorpay Smart Link
                              </div>
                              <div className="bg-slate-950 p-2.5 rounded-lg font-mono text-[11px] text-indigo-300 truncate border border-indigo-900/60">
                                {currentStep.paymentLink}
                              </div>
                              <div className="rounded-lg bg-emerald-600 text-white font-bold py-2 text-xs shadow-md">
                                Pay ₹3,850 via GPay / PhonePe / Paytm
                              </div>
                            </div>
                          )}

                          {currentStep.screenType === 'payment_done' && (
                            <div className="rounded-xl bg-emerald-950/60 p-4 text-xs space-y-3 border border-emerald-500/40 text-center">
                              <div className="flex justify-center">
                                <div className="h-10 w-10 rounded-full bg-emerald-500 text-slate-950 flex items-center justify-center font-bold">
                                  <Check className="h-6 w-6 stroke-[3]" />
                                </div>
                              </div>
                              <h5 className="font-extrabold text-emerald-300 text-sm">{currentStep.status}</h5>
                              <p className="text-[10px] text-emerald-400">
                                Tax Invoice #INV-2026-0891 delivered to customer on WhatsApp.
                              </p>
                            </div>
                          )}

                          {currentStep.screenType === 'invoice_shared' && (
                            <div className="rounded-xl bg-slate-950 p-3 text-xs space-y-3 border border-slate-800">
                              <div className="flex justify-between items-center text-slate-400 text-[10px]">
                                <span>WhatsApp Delivery</span>
                                <span className="text-emerald-400 font-bold font-mono">DELIVERED</span>
                              </div>
                              <div className="bg-slate-900 p-3 rounded-lg border border-slate-800 text-center font-mono text-indigo-300 text-xs">
                                📄 {currentStep.invoiceNumber}
                              </div>
                              <div className="text-[10px] text-slate-400 text-center">
                                Tax receipt & tracking details sent to buyer.
                              </div>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    </AnimatePresence>
                  </div>

                  {/* Bottom Nav Stepper Dots */}
                  <div className="flex items-center justify-between pt-3 border-t border-slate-800">
                    <button
                      disabled={activeStep === 0}
                      onClick={() => setActiveStep((prev) => Math.max(0, prev - 1))}
                      className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-[11px] font-bold text-slate-300 hover:bg-slate-800 disabled:opacity-30 disabled:pointer-events-none"
                    >
                      Prev
                    </button>
                    <div className="flex gap-1">
                      {WORKFLOW_STEPS.map((_, i) => (
                        <div
                          key={i}
                          className={`h-1.5 rounded-full transition-all ${
                            i === activeStep ? 'w-4 bg-indigo-500' : 'w-1.5 bg-slate-800'
                          }`}
                        />
                      ))}
                    </div>
                    <button
                      disabled={activeStep === WORKFLOW_STEPS.length - 1}
                      onClick={() => setActiveStep((prev) => Math.min(WORKFLOW_STEPS.length - 1, prev + 1))}
                      className="px-3 py-1.5 rounded-lg bg-indigo-600 text-[11px] font-bold text-white hover:bg-indigo-500 disabled:opacity-30 disabled:pointer-events-none"
                    >
                      Next
                    </button>
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
