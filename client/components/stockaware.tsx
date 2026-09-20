'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'
import type { ReactNode } from 'react'
import type { LucideIcon } from 'lucide-react'
import {
  Bell,
  Box,
  CircleDot,
  Command,
  ChevronRight,
  FileText,
  LayoutDashboard,
  Maximize2,
  Menu,
  Network,
  Package,
  Play,
  RotateCcw,
  Settings2,
  Sparkles,
  Wallet,
  X,
  Zap,
} from 'lucide-react'
import { agents, inventory, nav, timeline } from '@/lib/stockaware'

export function Logo({ dark = false }: { dark?: boolean }) {
  return (
    <Link
      href="/"
      className={`flex items-center gap-2 font-semibold tracking-tight ${
        dark ? 'text-white' : 'text-[#111B21]'
      }`}
    >
      <img src="/bizmate-logo-icon.png" alt="BizMate Logo" className="h-7 w-7 rounded-lg object-contain" />
      <span>
        Biz<span className="text-[#128C7E]">Mate</span>
      </span>
    </Link>
  )
}

export function StatusPill({
  children,
  tone = 'muted',
}: {
  children: ReactNode
  tone?: string
}) {
  return (
    <span className={`status-pill ${tone}`}>
      <span className="size-1.5 rounded-full bg-current" />
      {children}
    </span>
  )
}

export function NetworkVisual({ compact = false }: { compact?: boolean }) {
  return (
    <div className={`network-visual ${compact ? 'compact' : ''}`}>
      <div className="network-grid" />

      {['RFQ', 'INVENTORY', 'PRICING', 'APPROVAL', 'PAYMENT', 'INVOICE'].map(
        (label, i) => (
          <div
            key={label}
            className="network-node"
            style={{
              left: `${15 + (i % 3) * 34}%`,
              top: `${20 + Math.floor(i / 3) * 48}%`,
              animationDelay: `${i * 300}ms`,
            }}
          >
            <span className="node-orb" />
            <span className="node-label">{label}</span>
          </div>
        ),
      )}

      <svg
        className="network-lines"
        viewBox="0 0 600 300"
        preserveAspectRatio="none"
      >
        <path d="M90 75 C180 10, 220 140, 300 75 S430 10, 510 75 M90 225 C180 160, 220 290, 300 225 S430 160, 510 225 M90 75 L90 225 M300 75 L300 225 M510 75 L510 225" />
      </svg>

      <div className="network-center">
        <Sparkles />
        <span>Manager</span>
      </div>
    </div>
  )
}

export function AgentSimulationStage({
  runId,
  status,
}: {
  runId: string
  status: string
}) {
  return (
    <section
      className="simulation-stage"
      aria-label="Live agent simulation mounting area"
    >
      <div className="simulation-atmosphere" />

      <div className="simulation-toolbar">
        <div className="simulation-controls">
          <button className="ghost-control" disabled>
            <Play /> Run
          </button>

          <button className="ghost-control" disabled>
            Ⅱ Pause
          </button>

          <button className="ghost-control" disabled>
            <RotateCcw /> Restart
          </button>

          <span className="simulation-speed">1×</span>
        </div>

        <button
          className="ghost-control focus-control"
          aria-label="Focus simulation"
        >
          <Maximize2 /> Focus
        </button>
      </div>

      <div className="simulation-reserved">
        <div className="reserved-mark">
          <Network />
        </div>

        <p className="eyebrow">LIVE AGENT SIMULATION</p>

        <strong>Reserved visualization stage</strong>

        <span>Interactive control-room visualization mounts here</span>

        <small className="mono">
          {runId} · {status}
        </small>
      </div>
    </section>
  )
}

export function AgentStatusStrip() {
  return (
    <div className="agent-status-strip" aria-label="Agent workflow status">
      {[
        ['Manager', 'Active', 'active'],
        ['Sales', 'Done', 'done'],
        ['Catalogue', 'Done', 'done'],
        ['Inventory', 'Done', 'done'],
        ['Finance', 'Blocked', 'blocked'],
        ['Quote', 'Waiting', 'waiting'],
      ].map(([role, state, tone]) => (
        <div className="agent-status" key={role}>
          <span className={`agent-status-dot ${tone}`}>
            {tone === 'done'
              ? '✓'
              : tone === 'blocked'
                ? '!'
                : tone === 'waiting'
                  ? '◷'
                  : '•'}
          </span>

          <span>
            <b>{role}</b>
            <small>{state}</small>
          </span>
        </div>
      ))}
    </div>
  )
}

export function AgentDetailsPanel() {
  const [decision, setDecision] = useState<string | null>(null)

  return (
    <aside className="agent-details-panel">
      <div className="details-heading">
        <div>
          <p className="eyebrow">SELECTED AGENT</p>
          <h2>Finance / Pricing</h2>
        </div>

        <StatusPill tone="amber">Policy blocked</StatusPill>
      </div>

      <div className="detail-task">
        <span>Current task</span>
        <strong>Check quote pricing</strong>
      </div>

      <div className="detail-section">
        <span className="detail-label">Tool calls</span>

        <div className="tool-call-list">
          <code>pricing.read</code>
          <code>policy.read</code>
          <code>margin.calculate</code>
        </div>
      </div>

      <div className="detail-metrics">
        <div>
          <span>Requested discount</span>
          <b>12%</b>
        </div>

        <div>
          <span>Allowed</span>
          <b>7%</b>
        </div>

        <div>
          <span>Confidence</span>
          <b className="text-[#25D366]">94%</b>
        </div>
      </div>

      <div className="detail-result">
        <span className="detail-label">Result</span>
        <strong>Policy exception detected</strong>
        <p>
          Pricing is outside the approved margin band and needs owner review.
        </p>
      </div>

      <div className="detail-row">
        <span>Requires approval</span>
        <b className="text-[#F7B731]">YES</b>
      </div>

      <div className="detail-row">
        <span>Next action</span>
        <b>Owner approval</b>
      </div>

      <div className="approval-card">
        <p className="eyebrow">OWNER APPROVAL</p>

        <strong>RFQ-1042 · Pricing exception</strong>

        <div className="approval-amount">
          <span>Recommended quote</span>
          <b>₹124,000</b>
        </div>

        {decision ? (
          <div className="decision-state">
            {decision} recorded for this run.
          </div>
        ) : (
          <div className="approval-actions">
            <button
              className="btn btn-primary"
              onClick={() => setDecision('Approval')}
            >
              Approve
            </button>

            <button
              className="btn btn-secondary"
              onClick={() => setDecision('Revision')}
            >
              Revise
            </button>

            <button
              className="btn btn-quiet"
              onClick={() => setDecision('Decline')}
            >
              Decline
            </button>
          </div>
        )}
      </div>
    </aside>
  )
}

export function AdminShell({ children }: { children: ReactNode }) {
  const [mobile, setMobile] = useState(false)
  const pathname = usePathname()

  return (
    <div className="admin-shell">
      <aside className={`admin-sidebar ${mobile ? 'open' : ''}`}>
        <div className="flex items-center justify-between">
          <Logo dark />

          <button
            className="icon-button md:hidden"
            onClick={() => setMobile(false)}
            aria-label="Close navigation"
          >
            <X />
          </button>
        </div>

        <div className="workspace-card">
          <div className="grid size-8 place-items-center rounded-lg bg-white/10">
            <Box />
          </div>

          <div>
            <p className="text-xs text-white/65">Workspace</p>
            <p className="text-sm font-medium text-white">
              Sharma Electricals
            </p>
          </div>

          <ChevronRight className="ml-auto size-4 text-white/45" />
        </div>

        <nav className="flex flex-col gap-1">
          {nav.map(([name, href], i) => {
            const active =
              pathname === href ||
              (href !== '/dashboard' && pathname.startsWith(`${href}/`))

            const icons: LucideIcon[] = [
              LayoutDashboard,
              Bell,
              Package,
              FileText,
              Wallet,
              FileText,
            ]

            const Icon = icons[i] ?? LayoutDashboard

            return (
              <Link
                key={href}
                href={href}
                onClick={() => setMobile(false)}
                className={`admin-nav ${active ? 'active' : ''}`}
              >
                <span>
                  <Icon />
                </span>

                {name}

                {name === 'Approvals' && <b>4</b>}
              </Link>
            )
          })}
        </nav>

        <div className="mt-auto flex flex-col gap-1">
          <Link
            className={`admin-nav ${
              pathname.startsWith('/settings') ? 'active' : ''
            }`}
            href="/settings"
          >
            <Settings2 />
            Settings
          </Link>

          <div className="health-card">
            <span className="size-2 rounded-full bg-[#25D366]" />
            <span>All systems operational</span>
          </div>
        </div>
      </aside>

      <div className="admin-main">
        <header className="admin-topbar">
          <button
            className="icon-button md:hidden"
            onClick={() => setMobile(true)}
            aria-label="Open navigation"
          >
            <Menu />
          </button>

          <div className="hidden items-center gap-2 text-sm text-[#54656F] md:flex">
            <Command className="size-4" />
            Search anything
            <kbd>⌘ K</kbd>
          </div>

          <div className="ml-auto flex items-center gap-3">
            <span className="live-sync">
              <span />
              Live sync
            </span>

            <button className="icon-button" aria-label="Notifications">
              <Bell />
            </button>

            <div className="avatar">AR</div>
          </div>
        </header>

        <main className="admin-content">{children}</main>
      </div>
    </div>
  )
}

export function PageHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow?: string
  title: string
  description?: string
  action?: ReactNode
}) {
  return (
    <div className="page-header">
      <div>
        <p className="eyebrow">
          {eyebrow ?? 'STOCKAWARE / CONTROL ROOM'}
        </p>

        <h1>{title}</h1>

        {description && (
          <p className="page-description">{description}</p>
        )}
      </div>

      {action}
    </div>
  )
}

export function Timeline({ limit }: { limit?: number }) {
  return (
    <div className="timeline">
      {timeline.slice(0, limit).map(([time, text, tone]) => (
        <div className="timeline-row" key={time + text}>
          <span className={`timeline-dot ${tone}`} />

          <time>{time}</time>

          <span>{text}</span>

          <ChevronRight className="ml-auto size-4 text-[#667781]" />
        </div>
      ))}
    </div>
  )
}

export function CommandCenter({ detail = false }: { detail?: boolean }) {
  const [selected, setSelected] = useState(4)

  return (
    <div className={`command-center ${detail ? 'detail' : ''}`}>
      <div className="command-toolbar">
        <div>
          <p className="eyebrow">LIVE ORCHESTRATION</p>
          <h2>Manager Command Center</h2>
        </div>

        <StatusPill tone="green">Runtime healthy</StatusPill>
      </div>

      <div className="command-world">
        <div className="world-ring ring-one" />
        <div className="world-ring ring-two" />

        {agents.map(([name, role, task, tone], i) => (
          <button
            key={name}
            onClick={() => setSelected(i)}
            className={`agent-node ${tone} ${
              selected === i ? 'selected' : ''
            }`}
            style={{
              left: `${
                50 +
                Math.cos((i / agents.length) * Math.PI * 2) * 36
              }%`,
              top: `${
                50 +
                Math.sin((i / agents.length) * Math.PI * 2) * 35
              }%`,
            }}
          >
            <span className="agent-avatar">{name[0]}</span>
            <strong>{name}</strong>
            <small>{task}</small>
          </button>
        ))}

        <div className="manager-core">
          <Sparkles />
          <strong>Manager</strong>
          <small>RFQ-1042 active</small>
        </div>
      </div>

      <div className="command-footer">
        <span>
          <CircleDot className="text-[#25D366]" />
          Active flow
        </span>

        <span className="mono">RUN-82F9 · 14:04:06</span>
      </div>

      {detail && (
        <div className="agent-inspector">
          <p className="eyebrow">SELECTED AGENT</p>

          <h3>{agents[selected][0]}</h3>

          <p className="text-sm text-[#54656F]">
            {agents[selected][1]}
          </p>

          <div className="inspector-status">
            <StatusPill tone={agents[selected][3]}>
              {agents[selected][2]}
            </StatusPill>
          </div>

          <div className="inspector-row">
            <span>Current task</span>
            <b>
              {selected === 4
                ? 'Verify discount policy'
                : 'Coordinate RFQ-1042'}
            </b>
          </div>

          <div className="inspector-row">
            <span>Confidence</span>
            <b className="text-[#25D366]">94%</b>
          </div>

          <div className="inspector-row">
            <span>Next action</span>
            <b>Owner approval required</b>
          </div>
        </div>
      )}
    </div>
  )
}

export function InventoryTable() {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Product</th>
            <th>SKU</th>
            <th>Stock</th>
            <th>Threshold</th>
            <th>Margin</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {inventory.map((item) => (
            <tr key={item.id}>
              <td>
                <Link
                  href={`/inventory/${item.id}`}
                  className="font-medium hover:text-[#128C7E]"
                >
                  {item.name}
                </Link>

                <small>{item.category}</small>
              </td>

              <td className="mono text-[#667781]">{item.sku}</td>

              <td>
                <div className="stock-cell">
                  <span>{item.stock}</span>

                  <div className="stock-bar">
                    <i
                      style={{
                        width: `${Math.min(
                          (item.stock / item.threshold) * 40,
                          100,
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              </td>

              <td className="mono text-[#667781]">
                {item.threshold}
              </td>

              <td>{item.margin}</td>

              <td>
                <StatusPill
                  tone={item.status === 'Healthy' ? 'green' : 'amber'}
                >
                  {item.status}
                </StatusPill>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function Metric({
  label,
  value,
  change,
  icon: Icon,
}: {
  label: string
  value: string
  change: string
  icon: LucideIcon
}) {
  return (
    <div className="metric-card">
      <div className="metric-top">
        <span>{label}</span>
        <Icon />
      </div>

      <strong>{value}</strong>

      <small className={change.startsWith('+') ? 'positive' : undefined}>
        {change}
      </small>
    </div>
  )
}

export function BuyerLayout({ children }: { children: ReactNode }) {
  return (
    <div className="buyer-shell">
      <header>
        <Logo />

        <span className="text-sm text-[#54656F]">
          Need help?{' '}
          <a href="mailto:support@stockaware.app">
            Contact support
          </a>
        </span>
      </header>

      <main>{children}</main>

      <footer>
        StockAware · Intelligent commerce infrastructure
      </footer>
    </div>
  )
}

export function DocumentCard({
  type = 'QUOTE',
}: {
  type?: string
}) {
  return (
    <div className="document-card">
      <div className="document-brand">
        <Logo />
        <span>{type}</span>
      </div>

      <div className="doc-lines">
        <i />
        <i />
        <i />
        <i />
      </div>

      <div className="flex items-center justify-between">
        <StatusPill tone="green">Paid</StatusPill>

        <span className="mono text-xs">INV-1042</span>
      </div>
    </div>
  )
}