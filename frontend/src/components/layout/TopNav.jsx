import { Menu, UserCircle } from 'lucide-react'
import DemoDataBanner from '../ui/DemoDataBanner'

export default function TopNav({ title, onMenuClick }) {
  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80">
      <div className="flex h-14 items-center justify-between gap-4 px-4 sm:px-6">
        <div className="flex min-w-0 items-center gap-3">
          <button
            type="button"
            className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 lg:hidden"
            aria-label="Open navigation menu"
            onClick={onMenuClick}
          >
            <Menu className="h-5 w-5" />
          </button>
          <h1 className="truncate text-lg font-semibold text-slate-900">{title}</h1>
        </div>
        <div className="flex shrink-0 flex-wrap items-center justify-end gap-2 sm:gap-3">
          <DemoDataBanner compact />
          <span className="hidden rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-xs font-medium text-slate-600 sm:inline">
            Demo mode
          </span>
          <button
            type="button"
            disabled
            className="flex cursor-not-allowed items-center gap-2 rounded-lg border border-slate-200 px-2 py-1.5 text-sm text-slate-400 opacity-80"
            aria-label="Profile (unavailable in demo)"
            title="Profile unavailable in demo mode"
          >
            <UserCircle className="h-5 w-5" aria-hidden />
            <span className="hidden sm:inline">Analyst</span>
          </button>
        </div>
      </div>
    </header>
  )
}
