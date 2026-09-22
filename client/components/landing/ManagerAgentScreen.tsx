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
  Sparkles,
} from 'lucide-react';

export function ManagerAgentScreen() {
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
        <ChevronLeft className="h-5 w-5 opacity-90 cursor-pointer" />
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-500 font-bold text-xs text-white shadow-inner">
          <Sparkles className="h-4 w-4" />
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1">
            <p className="truncate text-xs font-semibold leading-tight">BizMate Manager Agent</p>
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-300 fill-emerald-400/20" />
          </div>
          <p className="text-[9.5px] text-white/80">online · manager account</p>
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

        {/* Message 1: Owner */}
        <div className="relative flex justify-end">
          <div className="max-w-[85%] rounded-2xl rounded-tr-xs bg-[#d9fdd3] px-3 py-2 text-slate-800 shadow-xs">
            <p className="leading-snug">Good morning, kal ka business kaisa tha? Aur kya important hai?</p>
            <div className="mt-0.5 flex justify-end gap-1 text-[8.5px] text-slate-500">
              <span>09:14</span>
              <CheckCheck className="h-3 w-3 text-[#53bdeb]" />
            </div>
          </div>
        </div>

        {/* Message 2: Manager Agent */}
        <div className="relative flex justify-start">
          <div className="max-w-[88%] rounded-2xl rounded-tl-xs bg-white px-3.5 py-2 text-slate-800 shadow-xs space-y-1.5">
            <p className="font-semibold text-slate-900 leading-snug">Good morning 👋</p>
            <p className="leading-snug">Yesterday&apos;s sales were <strong className="text-slate-900">₹1.84L</strong>.</p>
            <div className="text-[10.5px] leading-relaxed text-slate-700 space-y-0.5 pl-1 border-l-2 border-indigo-500 my-1 bg-indigo-50/50 p-1.5 rounded-r-lg">
              <p className="font-medium text-slate-800">You have:</p>
              <p>• 3 pending payments</p>
              <p>• 2 customer follow-ups</p>
              <p>• 1 vendor price update</p>
              <p>• 7 low-stock items</p>
            </div>
            <p className="text-[10px] text-slate-500">I&apos;ll keep these organized for you.</p>
            <div className="mt-0.5 text-[8.5px] text-slate-400">09:14</div>
          </div>
        </div>

        {/* Message 3: Owner */}
        <div className="relative flex justify-end">
          <div className="max-w-[65%] rounded-2xl rounded-tr-xs bg-[#d9fdd3] px-3 py-1.5 text-slate-800 shadow-xs">
            <p className="leading-snug">Black kurti ka stock?</p>
            <div className="mt-0.5 flex justify-end gap-1 text-[8.5px] text-slate-500">
              <span>09:15</span>
              <CheckCheck className="h-3 w-3 text-[#53bdeb]" />
            </div>
          </div>
        </div>

        {/* Message 4: Manager Agent */}
        <div className="relative flex justify-start">
          <div className="max-w-[85%] rounded-2xl rounded-tl-xs bg-white px-3 py-2 text-slate-800 shadow-xs space-y-1">
            <p className="leading-snug font-medium text-slate-900">7 pieces currently available.</p>
            <p className="leading-snug text-slate-600 text-[10.5px]">I can also prepare a follow-up for customers who asked about it.</p>
            <div className="mt-0.5 text-[8.5px] text-slate-400">09:15</div>
          </div>
        </div>

        {/* Message 5: Owner */}
        <div className="relative flex justify-end">
          <div className="max-w-[75%] rounded-2xl rounded-tr-xs bg-[#d9fdd3] px-3 py-1.5 text-slate-800 shadow-xs">
            <p className="leading-snug">Social media ke liye kuch suggest karo.</p>
            <div className="mt-0.5 flex justify-end gap-1 text-[8.5px] text-slate-500">
              <span>09:16</span>
              <CheckCheck className="h-3 w-3 text-[#53bdeb]" />
            </div>
          </div>
        </div>

        {/* Message 6: Manager Agent */}
        <div className="relative flex justify-start">
          <div className="max-w-[88%] rounded-2xl rounded-tl-xs bg-white px-3 py-2 text-slate-800 shadow-xs space-y-1">
            <p className="leading-snug text-slate-800">
              <strong className="text-pink-600 font-semibold">Social Agent</strong> has prepared 3 new-arrival post ideas. Want to review them?
            </p>
            <div className="mt-0.5 text-[8.5px] text-slate-400">09:16</div>
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
