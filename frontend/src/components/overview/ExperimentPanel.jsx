import { ArrowRight, FlaskConical } from 'lucide-react'

export default function ExperimentPanel() {
  return (
    <section
      className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
      aria-labelledby="experiment-title"
    >
      <div className="mb-4 flex items-start gap-3">
        <div className="rounded-lg bg-navy-900/5 p-2 text-navy-800">
          <FlaskConical className="h-5 w-5" aria-hidden />
        </div>
        <div>
          <h2 id="experiment-title" className="text-base font-semibold text-slate-900">
            Research experiment: deletion verification approaches
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Compare baseline primary-record deletion against dependency-aware
            verification (conceptual — demo metrics only).
          </p>
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <article className="rounded-lg border border-slate-200 bg-slate-50/50 p-4">
          <h3 className="text-sm font-semibold text-slate-800">Baseline</h3>
          <p className="mt-1 text-xs text-slate-500">Primary record deletion only</p>
          <ul className="mt-3 space-y-2 text-sm text-slate-700">
            <li className="flex justify-between">
              <span>Orphan risk (sample)</span>
              <span className="font-medium text-red-600">High</span>
            </li>
            <li className="flex justify-between">
              <span>Targets verified</span>
              <span className="font-medium tabular-nums">1 / 3</span>
            </li>
            <li className="flex justify-between">
              <span>False &quot;complete&quot; rate</span>
              <span className="font-medium tabular-nums">42%</span>
            </li>
          </ul>
        </article>
        <article className="rounded-lg border border-navy-800/20 bg-navy-950/5 p-4 ring-1 ring-navy-800/10">
          <h3 className="text-sm font-semibold text-navy-900">
            TraceProof (dependency-aware)
          </h3>
          <p className="mt-1 text-xs text-slate-500">Lineage-guided verification</p>
          <ul className="mt-3 space-y-2 text-sm text-slate-700">
            <li className="flex justify-between">
              <span>Orphan risk (sample)</span>
              <span className="font-medium text-emerald-700">Low</span>
            </li>
            <li className="flex justify-between">
              <span>Targets verified</span>
              <span className="font-medium tabular-nums">3 / 3</span>
            </li>
            <li className="flex justify-between">
              <span>False &quot;complete&quot; rate</span>
              <span className="font-medium tabular-nums">4%</span>
            </li>
          </ul>
        </article>
      </div>
      <p className="mt-4 flex items-center gap-2 text-xs text-slate-500">
        <ArrowRight className="h-3.5 w-3.5" aria-hidden />
        Full experiment tooling will connect when the backend milestone ships.
      </p>
    </section>
  )
}
