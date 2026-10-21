import DemoDataBanner from '../components/ui/DemoDataBanner'

export default function SettingsPage() {
  return (
    <div className="mx-auto max-w-lg space-y-6">
      <DemoDataBanner />
      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-base font-semibold text-slate-900">Workspace</h2>
        <p className="mt-1 text-sm text-slate-500">Demo workspace — not persisted.</p>
        <dl className="mt-4 space-y-3 text-sm">
          <div className="flex justify-between">
            <dt className="text-slate-500">Organization</dt>
            <dd className="font-medium text-slate-800">Acme District (fictional)</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-slate-500">AWS connection</dt>
            <dd className="font-medium text-slate-400">Not configured</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-slate-500">Environment</dt>
            <dd className="font-medium text-amber-700">Demo mode</dd>
          </div>
        </dl>
      </section>
    </div>
  )
}
