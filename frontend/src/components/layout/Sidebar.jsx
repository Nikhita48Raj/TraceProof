import {
  FlaskConical,
  FileCheck,
  GitBranch,
  LayoutDashboard,
  Settings,
  Shield,
  Trash2,
} from 'lucide-react'
import { NAV_ITEMS } from '../../data/sampleData'

const ICONS = {
  LayoutDashboard,
  GitBranch,
  Trash2,
  FileCheck,
  FlaskConical,
  Settings,
}

export default function Sidebar({ activePage, onNavigate, mobileOpen, onCloseMobile }) {
  const nav = (
    <nav className="flex flex-1 flex-col gap-1 px-3 py-4" aria-label="Main">
      {NAV_ITEMS.map(({ id, label, icon }) => {
        const Icon = ICONS[icon]
        const active = activePage === id
        return (
          <button
            key={id}
            type="button"
            onClick={() => {
              onNavigate(id)
              onCloseMobile?.()
            }}
            className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium transition-colors ${
              active
                ? 'bg-white/10 text-white'
                : 'text-slate-300 hover:bg-white/5 hover:text-white'
            }`}
            aria-current={active ? 'page' : undefined}
          >
            <Icon className="h-4 w-4 shrink-0 opacity-90" aria-hidden />
            {label}
          </button>
        )
      })}
    </nav>
  )

  return (
    <>
      {mobileOpen && (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-slate-900/60 lg:hidden"
          aria-label="Close menu"
          onClick={onCloseMobile}
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col bg-navy-950 text-white transition-transform lg:static lg:translate-x-0 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center gap-2.5 border-b border-white/10 px-5 py-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-navy-800 ring-1 ring-white/10">
            <Shield className="h-5 w-5 text-slate-100" aria-hidden />
          </div>
          <div>
            <p className="text-sm font-semibold tracking-tight">TraceProof</p>
            <p className="text-xs text-slate-400">Deletion verification</p>
          </div>
        </div>
        {nav}
        <p className="border-t border-white/10 px-5 py-4 text-xs text-slate-500">
          Milestone 1 · Frontend demo
        </p>
      </aside>
    </>
  )
}
