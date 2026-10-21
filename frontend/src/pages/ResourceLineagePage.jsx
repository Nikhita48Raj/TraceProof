import DependencyGraph from '../components/overview/DependencyGraph'
import DemoDataBanner from '../components/ui/DemoDataBanner'
import { SAMPLE_RESOURCES } from '../data/sampleData'

export default function ResourceLineagePage() {
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <DemoDataBanner />
      <DependencyGraph />
      <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 px-5 py-4">
          <h2 className="text-base font-semibold text-slate-900">Registered resources</h2>
          <p className="mt-1 text-sm text-slate-500">Fictional inventory for demo navigation.</p>
        </div>
        <ul className="divide-y divide-slate-100">
          {SAMPLE_RESOURCES.map((r) => (
            <li key={r.id} className="px-5 py-4">
              <p className="font-medium text-slate-800">{r.name}</p>
              <p className="mt-1 text-sm text-slate-500">
                {r.type}
                {r.table && ` · ${r.table}`}
                {r.bucket && ` · ${r.bucket}`}
              </p>
              <p className="mt-2 text-xs text-slate-500">
                {r.dependents.length} dependent target
                {r.dependents.length === 1 ? '' : 's'} in lineage graph
              </p>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
