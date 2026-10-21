import { AlertTriangle, CheckCircle2, Clock, Database } from 'lucide-react'

const CARDS = [
  {
    key: 'total',
    label: 'Total registered resources',
    icon: Database,
    iconBg: 'bg-navy-900/5 text-navy-800',
  },
  {
    key: 'pending',
    label: 'Pending deletion requests',
    icon: Clock,
    iconBg: 'bg-amber-50 text-amber-700',
  },
  {
    key: 'verified',
    label: 'Verified deletion requests',
    icon: CheckCircle2,
    iconBg: 'bg-emerald-50 text-emerald-700',
  },
  {
    key: 'incomplete',
    label: 'Incomplete deletion requests',
    icon: AlertTriangle,
    iconBg: 'bg-red-50 text-red-700',
  },
]

export default function StatCards({ stats }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {CARDS.map(({ key, label, icon: Icon, iconBg }) => (
        <article
          key={key}
          className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-medium text-slate-500">{label}</p>
              <p className="mt-2 text-3xl font-semibold tabular-nums text-slate-900">
                {stats[key]}
              </p>
            </div>
            <div className={`rounded-lg p-2.5 ${iconBg}`}>
              <Icon className="h-5 w-5" aria-hidden />
            </div>
          </div>
        </article>
      ))}
    </div>
  )
}
