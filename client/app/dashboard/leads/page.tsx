'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { 
  Users, 
  MessageSquare, 
  Mail, 
  PhoneCall, 
  Building2, 
  MapPin, 
  RefreshCw, 
  ArrowLeft,
  Calendar,
  Layers,
  Search,
  ExternalLink
} from 'lucide-react';
import { apiGet, ApiError } from '@/lib/api/client';

export interface EarlyAccessLead {
  id: string;
  full_name: string;
  business_name: string;
  phone: string;
  email: string;
  business_type: string;
  city: string;
  about_business: string;
  daily_whatsapp_orders?: string | null;
  source: string;
  status: string;
  payment_status: string;
  created_at: string;
  updated_at: string;
}

export default function AdminLeadsPage() {
  const router = useRouter();
  const [leads, setLeads] = useState<EarlyAccessLead[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedLead, setSelectedLead] = useState<EarlyAccessLead | null>(null);

  const fetchLeads = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiGet<EarlyAccessLead[]>('/early-access/leads');
      setLeads(data);
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 401) {
          router.replace('/login');
          return;
        }
        setError(err.message);
      } else {
        setError('Failed to fetch early access leads');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (typeof window !== 'undefined' && !window.localStorage.getItem('stockaware_owner_token')) {
      router.replace('/login');
      return;
    }
    fetchLeads();
  }, [router]);

  const cleanPhoneForWa = (phone: string) => {
    const digits = phone.replace(/\D/g, '');
    if (digits.length === 10) {
      return `91${digits}`;
    }
    return digits;
  };

  const filteredLeads = leads.filter((lead) => {
    const q = searchTerm.toLowerCase();
    return (
      lead.full_name.toLowerCase().includes(q) ||
      lead.business_name.toLowerCase().includes(q) ||
      lead.phone.toLowerCase().includes(q) ||
      lead.email.toLowerCase().includes(q) ||
      lead.city.toLowerCase().includes(q) ||
      lead.business_type.toLowerCase().includes(q)
    );
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-4 sm:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Navigation & Header Bar */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-indigo-400 transition-colors mb-2"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              <span>Back to Control Room</span>
            </Link>
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                <Users className="h-5 w-5" />
              </div>
              <div>
                <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
                  Early Access Leads
                </h1>
                <p className="text-xs text-slate-400">
                  BizMate founder cohort lead pipeline & direct customer actions
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchLeads}
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 px-4 py-2.5 text-xs font-semibold text-slate-200 transition-all cursor-pointer disabled:opacity-50"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* Stats & Search Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl flex items-center justify-between">
            <div>
              <span className="text-xs text-slate-400 font-medium block">Total Submissions</span>
              <span className="text-2xl font-extrabold text-white mt-1 block">{leads.length}</span>
            </div>
            <div className="h-10 w-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <Users className="h-5 w-5" />
            </div>
          </div>

          <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl flex items-center justify-between">
            <div>
              <span className="text-xs text-slate-400 font-medium block">New Leads</span>
              <span className="text-2xl font-extrabold text-emerald-400 mt-1 block">
                {leads.filter((l) => l.status === 'new').length}
              </span>
            </div>
            <div className="h-10 w-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <MessageSquare className="h-5 w-5" />
            </div>
          </div>

          <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl flex items-center justify-between">
            <div>
              <span className="text-xs text-slate-400 font-medium block">Payment Handoff</span>
              <span className="text-2xl font-extrabold text-amber-400 mt-1 block">
                ₹2,000 / lead
              </span>
            </div>
            <div className="h-10 w-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Layers className="h-5 w-5" />
            </div>
          </div>
        </div>

        {/* Filter Input */}
        <div className="relative">
          <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-500" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by name, business, phone, email, city or business type..."
            className="w-full bg-slate-900/90 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        {/* Loading / Error / Table Content */}
        {loading ? (
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center text-slate-400 text-xs">
            Loading early access leads...
          </div>
        ) : error ? (
          <div className="bg-rose-950/40 border border-rose-800 rounded-2xl p-6 text-center text-rose-300 text-xs">
            {error}
          </div>
        ) : filteredLeads.length === 0 ? (
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center text-slate-400 text-xs">
            No early access leads found.
          </div>
        ) : (
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-900 border-b border-slate-800 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                  <tr>
                    <th className="py-3.5 px-4">Name & Business</th>
                    <th className="py-3.5 px-4">Contact</th>
                    <th className="py-3.5 px-4">Type & City</th>
                    <th className="py-3.5 px-4">Daily Orders</th>
                    <th className="py-3.5 px-4">Submitted</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filteredLeads.map((lead) => {
                    const waDigits = cleanPhoneForWa(lead.phone);
                    const dateFormatted = new Date(lead.created_at).toLocaleDateString('en-IN', {
                      day: 'numeric',
                      month: 'short',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    });

                    return (
                      <tr key={lead.id} className="hover:bg-slate-800/40 transition-colors">
                        {/* Name & Business */}
                        <td className="py-4 px-4">
                          <div className="font-bold text-white text-sm">{lead.full_name}</div>
                          <div className="text-slate-400 flex items-center gap-1.5 mt-0.5 font-medium">
                            <Building2 className="h-3 w-3 text-indigo-400" />
                            <span>{lead.business_name}</span>
                          </div>
                        </td>

                        {/* Contact */}
                        <td className="py-4 px-4 space-y-1">
                          <div className="text-slate-200 font-mono text-xs">{lead.phone}</div>
                          <div className="text-slate-400 text-[11px] font-sans">{lead.email}</div>
                        </td>

                        {/* Type & City */}
                        <td className="py-4 px-4 space-y-1">
                          <div className="text-slate-200 font-semibold">{lead.business_type}</div>
                          <div className="text-slate-400 flex items-center gap-1 text-[11px]">
                            <MapPin className="h-3 w-3 text-slate-500" />
                            <span>{lead.city}</span>
                          </div>
                        </td>

                        {/* Daily Orders */}
                        <td className="py-4 px-4 text-slate-300">
                          {lead.daily_whatsapp_orders || '—'}
                        </td>

                        {/* Submitted */}
                        <td className="py-4 px-4 text-slate-400 text-[11px] whitespace-nowrap">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3 text-slate-500" />
                            <span>{dateFormatted}</span>
                          </div>
                        </td>

                        {/* Status */}
                        <td className="py-4 px-4 space-y-1">
                          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-0.5 text-[10px] font-extrabold text-emerald-400 uppercase">
                            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                            {lead.status}
                          </span>
                          <div className="text-[10px] text-slate-400 font-mono">
                            Payment: {lead.payment_status}
                          </div>
                        </td>

                        {/* Direct Actions */}
                        <td className="py-4 px-4 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            {/* WhatsApp Button */}
                            <a
                              href={`https://wa.me/${waDigits}?text=Hi%20${encodeURIComponent(lead.full_name)},%20this%20is%20the%20BizMate%20team%20following%20up%20on%20your%20Early%20Access%20reservation%20for%20${encodeURIComponent(lead.business_name)}.`}
                              target="_blank"
                              rel="noreferrer"
                              title="Chat on WhatsApp"
                              className="p-2 rounded-lg bg-[#25D366]/15 hover:bg-[#25D366]/25 border border-[#25D366]/30 text-[#25D366] transition-all"
                            >
                              <MessageSquare className="h-3.5 w-3.5" />
                            </a>

                            {/* Email Button */}
                            <a
                              href={`mailto:${lead.email}?subject=BizMate%20Early%20Access%20Onboarding%20—%20${encodeURIComponent(lead.business_name)}`}
                              title="Send Email"
                              className="p-2 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/20 text-indigo-400 transition-all"
                            >
                              <Mail className="h-3.5 w-3.5" />
                            </a>

                            {/* Phone Call */}
                            <a
                              href={`tel:${waDigits}`}
                              title="Call Phone"
                              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 transition-all"
                            >
                              <PhoneCall className="h-3.5 w-3.5" />
                            </a>

                            {/* Details Button */}
                            <button
                              onClick={() => setSelectedLead(lead)}
                              className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-[11px] font-semibold text-slate-200 border border-slate-700 transition-all ml-1 cursor-pointer"
                            >
                              Details
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Lead Details Modal */}
        {selectedLead && (
          <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 space-y-5 shadow-2xl relative">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div>
                  <h3 className="text-lg font-bold text-white">{selectedLead.full_name}</h3>
                  <p className="text-xs text-indigo-400 font-semibold">{selectedLead.business_name}</p>
                </div>
                <button
                  onClick={() => setSelectedLead(null)}
                  className="text-slate-400 hover:text-white text-xs font-bold px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700"
                >
                  Close
                </button>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <span className="text-slate-500 font-semibold block">About Business:</span>
                  <p className="text-slate-200 bg-slate-950 p-3 rounded-xl border border-slate-800 mt-1 leading-relaxed whitespace-pre-wrap">
                    {selectedLead.about_business}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-3 pt-1">
                  <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                    <span className="text-slate-500 font-semibold block">City:</span>
                    <span className="text-slate-200 font-bold">{selectedLead.city}</span>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                    <span className="text-slate-500 font-semibold block">Business Type:</span>
                    <span className="text-slate-200 font-bold">{selectedLead.business_type}</span>
                  </div>
                </div>

                {selectedLead.daily_whatsapp_orders && (
                  <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                    <span className="text-slate-500 font-semibold block">Daily WhatsApp Enquiries:</span>
                    <span className="text-slate-200 font-medium">{selectedLead.daily_whatsapp_orders}</span>
                  </div>
                )}
              </div>

              <div className="pt-2 flex items-center justify-end gap-2 border-t border-slate-800">
                <a
                  href={`https://wa.me/${cleanPhoneForWa(selectedLead.phone)}`}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#25D366] hover:bg-[#128C7E] text-white text-xs font-bold transition-all"
                >
                  <MessageSquare className="h-3.5 w-3.5" />
                  <span>WhatsApp Lead</span>
                </a>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
