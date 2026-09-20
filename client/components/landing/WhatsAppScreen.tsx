'use client';

import React from 'react';
import {
  ChevronLeft,
  Phone,
  Video,
  MoreVertical,
  CheckCheck,
  Mic,
  Paperclip,
  Smile,
  ShieldCheck,
} from 'lucide-react';

type WhatsAppScreenProps = {
  activeStep?: number;
};

export function WhatsAppScreen({ activeStep = 4 }: WhatsAppScreenProps) {
  return (
    <div className="flex h-full w-full flex-col bg-[#efeae2] font-sans text-slate-900 select-none">
      {/* Top Status Bar Placeholder */}
      <div className="flex items-center justify-between bg-[#075e54] px-5 pt-3 pb-1 text-[11px] font-semibold text-white">
        <span>9:41</span>
        <div className="flex items-center gap-1.5">
          <span className="text-[10px]">5G</span>
          <div className="h-2.5 w-4 rounded-sm border border-white p-0.5">
            <div className="h-full w-full bg-white rounded-xs" />
          </div>
        </div>
      </div>

      {/* WhatsApp Header */}
      <header className="relative z-10 flex items-center gap-2 bg-[#075e54] px-3 py-2 text-white shadow-md">
        <ChevronLeft className="h-5 w-5 opacity-90" />
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/20 font-semibold text-xs text-white">
          B
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1">
            <p className="truncate text-xs font-semibold leading-tight">BizMate Sales Agent</p>
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-300 fill-emerald-400/20" />
          </div>
          <p className="text-[9.5px] text-white/80">online · business account</p>
        </div>

        <div className="flex items-center gap-3 text-white/90">
          <Video className="h-4 w-4 cursor-pointer" />
          <Phone className="h-4 w-4 cursor-pointer" />
          <MoreVertical className="h-4 w-4 cursor-pointer" />
        </div>
      </header>

      {/* Chat Background & Content */}
      <main
        className="relative flex-1 space-y-2.5 overflow-y-auto p-3 text-[11px] scrollbar-hide"
        style={{
          backgroundImage: `url('/whatsappChatWallPaper.jpg')`,
          backgroundSize: '320px auto',
          backgroundRepeat: 'repeat',
        }}
      >
        {/* Semi-transparent white layer over wallpaper */}
        <div className="absolute inset-0 bg-white/40 pointer-events-none" />

        {/* Date Stamp */}
        <div className="relative mx-auto w-fit rounded-lg bg-white/80 px-2.5 py-0.5 text-[9px] font-medium text-slate-600 shadow-xs">
          Today
        </div>

        {/* Message 1: Customer */}
        <div className="relative flex justify-end">
          <div className="max-w-[82%] rounded-2xl rounded-tr-xs bg-[#d9fdd3] px-3 py-1.5 text-slate-800 shadow-xs">
            <p className="leading-snug">10 black kurtis chahiye, size mix chalega?</p>
            <div className="mt-0.5 flex justify-end gap-1 text-[8.5px] text-slate-500">
              <span>09:24</span>
              <CheckCheck className="h-3 w-3 text-[#53bdeb]" />
            </div>
          </div>
        </div>

        {/* Message 2: Sales Agent */}
        <div className="relative flex justify-start">
          <div className="max-w-[84%] rounded-2xl rounded-tl-xs bg-white px-3 py-1.5 text-slate-800 shadow-xs">
            <p className="leading-snug">Sure! Checking available stock and current pricing for you now.</p>
            <div className="mt-0.5 text-[8.5px] text-slate-400">09:24</div>
          </div>
        </div>

        {/* System Pill: Inventory status */}
        <div className="relative mx-auto w-fit rounded-full bg-white/90 px-3 py-1 text-[9.5px] font-medium text-slate-600 shadow-xs flex items-center gap-1.5">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
          Stock check: 7 Black Kurtis in stock
        </div>

        {/* Message 3: Sales Agent Proposal */}
        <div className="relative flex justify-start">
          <div className="max-w-[86%] rounded-2xl rounded-tl-xs bg-white px-3 py-1.5 text-slate-800 shadow-xs">
            <p className="leading-snug">
              We have 7 ready to ship right now. I can prepare the quote for 7, or check next stock arrival.
            </p>
            <div className="mt-0.5 text-[8.5px] text-slate-400">09:25</div>
          </div>
        </div>

        {/* Message 4: Customer Reply */}
        <div className="relative flex justify-end">
          <div className="max-w-[65%] rounded-2xl rounded-tr-xs bg-[#d9fdd3] px-3 py-1.5 text-slate-800 shadow-xs">
            <p className="leading-snug">Quote for 7.</p>
            <div className="mt-0.5 flex justify-end gap-1 text-[8.5px] text-slate-500">
              <span>09:26</span>
              <CheckCheck className="h-3 w-3 text-[#53bdeb]" />
            </div>
          </div>
        </div>

        {/* Quotation Card */}
        <div className="relative mx-auto rounded-xl bg-white p-2.5 shadow-md border border-slate-100 max-w-[92%]">
          <div className="flex items-center justify-between border-b border-slate-100 pb-1.5">
            <span className="text-[9px] font-bold tracking-wider uppercase text-[#128c7e]">
              Quotation #Q7842
            </span>
            <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[8.5px] font-semibold text-emerald-700">
              Approved
            </span>
          </div>

          <div className="mt-2 space-y-1">
            <div className="flex justify-between text-[11px] font-semibold text-slate-900">
              <span>7 × Black Kurti (Mix sizes)</span>
              <span>₹3,500</span>
            </div>
            <div className="flex justify-between text-[9.5px] text-slate-500">
              <span>Delivery Charges</span>
              <span>₹350</span>
            </div>
            <div className="flex justify-between border-t border-dashed border-slate-200 pt-1.5 text-[12px] font-bold text-slate-900">
              <span>Total Payable</span>
              <span className="text-[#075e54]">₹3,850</span>
            </div>
          </div>

          {/* Payment CTA button inside WhatsApp */}
          <div className="mt-2.5">
            <button className="w-full rounded-lg bg-[#25d366] py-1.5 text-center text-[10.5px] font-bold text-white shadow-sm hover:bg-[#20bd5a] transition-colors">
              Pay Securely — ₹3,850
            </button>
          </div>
        </div>
      </main>

      {/* Input Bar */}
      <footer className="flex items-center gap-1.5 bg-[#f0f2f5] px-2 py-2">
        <div className="flex flex-1 items-center gap-2 rounded-full bg-white px-3 py-1.5 text-slate-400 text-[10px]">
          <Smile className="h-4 w-4 text-slate-400" />
          <span className="flex-1 text-slate-400 truncate">Type a message...</span>
          <Paperclip className="h-4 w-4 text-slate-400" />
        </div>
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#075e54] text-white">
          <Mic className="h-4 w-4" />
        </div>
      </footer>
    </div>
  );
}
