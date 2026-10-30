import { ArrowRight, FlaskConical } from 'lucide-react'

export default function ExperimentPanel() {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm" aria-labelledby="experiment-title">
      <div className="flex items-start gap-3">
        <div className="rounded-lg bg-navy-900/5 p-2 text-navy-800"><FlaskConical className="h-5 w-5" aria-hidden /></div>
        <div>
          <h2 id="experiment-title" className="text-base font-semibold text-slate-900">Reproducible research experiments</h2>
          <p className="mt-1 text-sm text-slate-500">Compare root-only deletion checks with dependency-closure verification using seeded synthetic graphs and measured outcomes.</p>
        </div>
      </div>
      <p className="mt-4 flex items-center gap-2 text-xs text-slate-500">
        <ArrowRight className="h-3.5 w-3.5" aria-hidden />
        Open Experiments to configure a run, review scenario-level results, and rerun with the same seed.
      </p>
    </section>
  )
}
