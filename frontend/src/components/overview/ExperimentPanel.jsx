import { ArrowRight, CheckCircle2, AlertTriangle, FlaskConical, ShieldAlert, Sparkles } from 'lucide-react'

export default function ExperimentPanel({ comparison, onOpenExperiments }) {
  const baseline = comparison?.baseline
  const traceproof = comparison?.traceproof

  return (
    <section
      className="flex flex-col justify-between rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
      aria-labelledby="experiment-title"
    >
      <div>
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className="rounded-lg bg-navy-900/10 p-2 text-navy-900">
              <FlaskConical className="h-5 w-5" aria-hidden />
            </div>
            <div>
              <h2 id="experiment-title" className="text-base font-semibold text-slate-900">
                Baseline vs. TraceProof Verification
              </h2>
              <p className="mt-0.5 text-xs text-slate-500">
                Evaluating root-only deletion against dependency-closure tracking.
              </p>
            </div>
          </div>
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600">
            Sample Root
          </span>
        </div>

        {comparison ? (
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {/* Baseline Card */}
            <div className="rounded-lg border border-slate-200 bg-slate-50/80 p-3.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-600">
                  Conventional Baseline
                </span>
                <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-700">
                  <AlertTriangle className="h-3 w-3" /> Root Only
                </span>
              </div>
              <p className="mt-1 text-xs text-slate-500">
                Deletes root record only without traversing dependencies.
              </p>

              <div className="mt-3 space-y-1.5 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-500">Targets checked:</span>
                  <span className="font-semibold text-slate-800">{baseline?.targets_checked ?? 1}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Unaddressed dependents:</span>
                  <span className="font-semibold text-red-600">
                    {baseline?.remaining_targets?.length ?? 2} remaining
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Simulated outcome:</span>
                  <span className="rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-semibold text-amber-800">
                    Silent Incomplete Deletion
                  </span>
                </div>
              </div>
            </div>

            {/* TraceProof Card */}
            <div className="rounded-lg border border-blue-200 bg-blue-50/40 p-3.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-blue-900">
                  TraceProof Engine
                </span>
                <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700">
                  <CheckCircle2 className="h-3 w-3" /> Full Closure
                </span>
              </div>
              <p className="mt-1 text-xs text-slate-500">
                Traverses registered DAG and verifies all dependent resources.
              </p>

              <div className="mt-3 space-y-1.5 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-500">Targets checked:</span>
                  <span className="font-semibold text-slate-800">{traceproof?.targets_checked ?? 3}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Unaddressed dependents:</span>
                  <span className="font-semibold text-emerald-600">
                    {traceproof?.remaining_targets?.length ?? 0} remaining
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Verification status:</span>
                  <span className="rounded bg-emerald-100 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-800">
                    {traceproof?.status ?? 'Verified'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="my-6 rounded-lg border border-dashed border-slate-200 p-4 text-center text-xs text-slate-500">
            Loading comparative benchmark...
          </div>
        )}
      </div>

      <div className="mt-4 border-t border-slate-100 pt-3">
        <button
          type="button"
          onClick={onOpenExperiments}
          className="inline-flex w-full items-center justify-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-100 hover:text-slate-900"
        >
          <span>Run multi-scenario statistical benchmark</span>
          <ArrowRight className="h-3.5 w-3.5" aria-hidden />
        </button>
      </div>
    </section>
  )
}
