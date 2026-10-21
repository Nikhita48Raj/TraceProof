import ExperimentPanel from '../components/overview/ExperimentPanel'
import DemoDataBanner from '../components/ui/DemoDataBanner'

export default function ExperimentsPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <DemoDataBanner />
      <ExperimentPanel />
      <section className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center">
        <p className="text-sm font-medium text-slate-700">Experiment runner (placeholder)</p>
        <p className="mt-2 text-sm text-slate-500">
          Configure cohorts, run A/B verification batches, and export results once the
          research backend is connected.
        </p>
      </section>
    </div>
  )
}
