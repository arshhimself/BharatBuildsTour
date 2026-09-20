'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Sparkles, ArrowRight, Menu, X } from 'lucide-react';

const NAV_ITEMS = [
  { label: 'Product', href: '/#product' },
  { label: 'How it works', href: '/#how-it-works' },
  { label: 'AI Team', href: '/#ai-team' },
  { label: 'Voice', href: '/#voice' },
  { label: 'Stories', href: '/#stories' },
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    function handleScroll() {
      if (window.scrollY > 20) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    }
    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 transition-all duration-300 px-4 pt-4 sm:px-6">
      <nav
        className={`mx-auto max-w-6xl rounded-full transition-all duration-300 px-4 sm:px-6 py-2.5 flex items-center justify-between ${
          scrolled
            ? 'bg-white/90 backdrop-blur-md border border-slate-200/90 shadow-md py-2'
            : 'bg-white/70 backdrop-blur-sm border border-slate-200/60'
        }`}
      >
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2">
          <img src="/bizmate-logo-icon.png" alt="BizMate Logo" className="h-7 w-7 rounded-lg object-contain" />
          <span className="text-lg font-extrabold tracking-tight text-slate-900">
            BizMate
          </span>
        </Link>

        {/* Center Nav Links (Desktop) */}
        <div className="hidden md:flex items-center gap-7 text-xs font-semibold text-slate-600">
          {NAV_ITEMS.map((item) => (
            <a
              key={item.label}
              href={item.href}
              className="hover:text-indigo-600 transition-colors"
            >
              {item.label}
            </a>
          ))}
        </div>

        {/* Right CTA Actions */}
        <div className="hidden md:flex items-center gap-3">
          <Link
            href="/login"
            className="text-xs font-bold text-slate-700 hover:text-indigo-600 px-3 py-1.5 transition-colors"
          >
            Log in
          </Link>
          <Link
            href="/early-access"
            className="inline-flex items-center gap-1.5 rounded-full bg-[#25D366] px-4 py-2 text-xs font-bold text-white shadow-md shadow-emerald-500/20 hover:bg-[#128C7E] transition-all duration-200 hover:scale-[1.02]"
          >
            <span>Reserve early access</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        {/* Mobile Menu Toggle Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden text-slate-700 p-1"
          aria-label="Toggle Menu"
        >
          {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </nav>

      {/* Mobile Dropdown Sheet */}
      {mobileMenuOpen && (
        <div className="md:hidden mt-2 rounded-2xl bg-white/95 backdrop-blur-lg border border-slate-200 p-5 shadow-xl space-y-4 font-semibold text-sm">
          {NAV_ITEMS.map((item) => (
            <a
              key={item.label}
              href={item.href}
              onClick={() => setMobileMenuOpen(false)}
              className="block text-slate-800 hover:text-indigo-600"
            >
              {item.label}
            </a>
          ))}
          <div className="pt-2 border-t border-slate-100 flex flex-col gap-2">
            <Link
              href="/login"
              onClick={() => setMobileMenuOpen(false)}
              className="text-slate-700 hover:text-indigo-600 py-1"
            >
              Log in
            </Link>
            <Link
              href="/early-access"
              onClick={() => setMobileMenuOpen(false)}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#25D366] py-2.5 text-xs font-bold text-white shadow-md shadow-emerald-500/20 hover:bg-[#128C7E]"
            >
              <span>Reserve early access</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
