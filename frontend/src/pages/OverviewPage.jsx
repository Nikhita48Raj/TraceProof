import { Plus } from 'lucide-react'
import DemoDataBanner from '../components/ui/DemoDataBanner'
import StatCards from '../components/overview/StatCards'
import DependencyGraph from '../components/overview/DependencyGraph'
import RecentActivityTable from '../components/overview/RecentActivityTable'
import ExperimentPanel from '../components/overview/ExperimentPanel'

export default function OverviewPage({
  requests = [],
  resources = [],
  stats = {},
  comparison = null,
  onNewRequest,
  onOpenExperiments,
  onSelectResource,
}) {
  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">
            System Overview & Research Metrics
          </h1>
          <p className="mt-0.5 text-xs text-slate-500">
            Real-time monitoring of dependency-aware deletion verification across registered resources.
          </p>
        </div>
        <button
          type="button"
          onClick={onNewRequest}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-navy-900 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-navy-800"
        >
          <Plus className="h-4 w-4" aria-hidden />
          New deletion request
        </button>
      </div>

      <DemoDataBanner />

      <StatCards stats={stats} />

      <div className="grid gap-6 lg:grid-cols-2">
        <DependencyGraph
          resources={resources}
          onSelectResource={onSelectResource}
        />
        <ExperimentPanel
          comparison={comparison}
          onOpenExperiments={onOpenExperiments}
        />
      </div>

      <RecentActivityTable requests={requests} resources={resources} limit={10} />

      <p className="text-center text-xs text-slate-400">
        Live data loaded from the backend simulation API. Physical cloud resources are not deleted.
      </p>
    </div>
  )
}
