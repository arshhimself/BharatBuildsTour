'use client';

import React from 'react';
import Link from 'next/link';
import { Sparkles, ArrowUp } from 'lucide-react';

export function Footer() {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="bg-white border-t border-slate-200 text-slate-600 text-xs py-14">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-12">
        
        {/* Main Footer Grid */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-8">
          
          {/* Brand Info */}
          <div className="md:col-span-2 space-y-4">
            <Link href="/" className="flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 text-white font-bold text-xs shadow-xs">
                <Sparkles className="h-3.5 w-3.5" />
              </div>
              <span className="text-lg font-extrabold tracking-tight text-slate-900">
                BizMate
              </span>
            </Link>
            <p className="text-slate-500 text-xs leading-relaxed max-w-sm">
              Simple on the surface. Intelligent underneath. Your AI team for sales, operations, finance and growth.
            </p>
          </div>

          {/* Column 1: Product */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Product</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/dashboard" className="hover:text-indigo-600 transition-colors">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/agent-office" className="hover:text-indigo-600 transition-colors">
                  Agent Office
                </Link>
              </li>
              <li>
                <a href="/#how-it-works" className="hover:text-indigo-600 transition-colors">
                  How it works
                </a>
              </li>
              <li>
                <a href="/#ai-team" className="hover:text-indigo-600 transition-colors">
                  AI Team
                </a>
              </li>
              <li>
                <a href="/#voice" className="hover:text-indigo-600 transition-colors">
                  Voice
                </a>
              </li>
            </ul>
          </div>

          {/* Column 2: Operations */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Operations</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/runs" className="hover:text-indigo-600 transition-colors">
                  Runs
                </Link>
              </li>
              <li>
                <Link href="/quotes" className="hover:text-indigo-600 transition-colors">
                  Quotes
                </Link>
              </li>
              <li>
                <Link href="/invoices" className="hover:text-indigo-600 transition-colors">
                  Invoices
                </Link>
              </li>
              <li>
                <Link href="/payments" className="hover:text-indigo-600 transition-colors">
                  Payments
                </Link>
              </li>
            </ul>
          </div>

          {/* Column 3: Company */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Company</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/early-access" className="text-indigo-600 font-bold hover:text-indigo-700 transition-colors">
                  Early Access
                </Link>
              </li>
              <li>
                <Link href="/login" className="hover:text-indigo-600 transition-colors">
                  Login
                </Link>
              </li>
            </ul>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-slate-400">
          <span>© {new Date().getFullYear()} BizMate AI Inc. All rights reserved.</span>

          <button
            onClick={scrollToTop}
            className="inline-flex items-center gap-1.5 text-slate-600 hover:text-slate-900 transition-colors cursor-pointer"
          >
            <span>Back to top</span>
            <ArrowUp className="h-3.5 w-3.5" />
          </button>
        </div>

      </div>
    </footer>
  );
}
