import { AlertOctagon, AlertTriangle, CheckCircle2, Clock, Database, TrendingUp, Layers } from 'lucide-react'

const CARDS = [
  {
    key: 'totalResources',
    label: 'Registered resources',
    icon: Database,
    iconBg: 'bg-navy-900/10 text-navy-900',
  },
  {
    key: 'totalRequests',
    label: 'Total deletion requests',
    icon: Layers,
    iconBg: 'bg-blue-50 text-blue-700',
  },
  {
    key: 'pending',
    label: 'Pending / Processing',
    icon: Clock,
    iconBg: 'bg-amber-50 text-amber-700',
  },
  {
    key: 'verified',
    label: 'Verified requests',
    icon: CheckCircle2,
    iconBg: 'bg-emerald-50 text-emerald-700',
  },
  {
    key: 'incomplete',
    label: 'Incomplete requests',
    icon: AlertTriangle,
    iconBg: 'bg-orange-50 text-orange-700',
  },
  {
    key: 'failed',
    label: 'Failed jobs',
    icon: AlertOctagon,
    iconBg: 'bg-red-50 text-red-700',
  },
  {
    key: 'successRate',
    label: 'Verification success rate',
    icon: TrendingUp,
    iconBg: 'bg-indigo-50 text-indigo-700',
  },
]

export default function StatCards({ stats = {} }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-7">
      {CARDS.map(({ key, label, icon: Icon, iconBg }) => (
        <article
          key={key}
          className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:shadow"
        >
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <p className="truncate text-xs font-medium text-slate-500" title={label}>
                {label}
              </p>
              <p className="mt-2 text-2xl font-bold tabular-nums text-slate-900">
                {stats[key] ?? 0}
              </p>
            </div>
            <div className={`shrink-0 rounded-lg p-2 ${iconBg}`}>
              <Icon className="h-4 w-4" aria-hidden />
            </div>
          </div>
        </article>
      ))}
    </div>
  )
}
