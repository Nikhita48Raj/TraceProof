import { Plus } from 'lucide-react'
import DemoDataBanner from '../components/ui/DemoDataBanner'
import StatCards from '../components/overview/StatCards'
import DependencyGraph from '../components/overview/DependencyGraph'
import RecentActivityTable from '../components/overview/RecentActivityTable'
import ExperimentPanel from '../components/overview/ExperimentPanel'
import { TOTAL_REGISTERED_RESOURCES } from '../data/sampleData'

export default function OverviewPage({ requests, stats, onNewRequest }) {
  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm text-slate-600">
            Monitor simulated deletion verification workflows using demo sample
            resources (no cloud connection).
          </p>
        </div>
        <button
          type="button"
          onClick={onNewRequest}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-navy-900 px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-navy-800"
        >
          <Plus className="h-4 w-4" aria-hidden />
          New deletion request
        </button>
      </div>

      <DemoDataBanner />

      <StatCards stats={stats} />

      <div className="grid gap-6 lg:grid-cols-2">
        <DependencyGraph />
        <ExperimentPanel />
      </div>

      <RecentActivityTable requests={requests} />

      <p className="text-center text-xs text-slate-400">
        Registered resources (demo total): {TOTAL_REGISTERED_RESOURCES} · Metrics
        derived from sample request set
      </p>
    </div>
  )
}
