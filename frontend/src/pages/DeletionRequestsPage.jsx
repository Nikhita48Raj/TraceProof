import { Inbox, Plus } from 'lucide-react'
import RecentActivityTable from '../components/overview/RecentActivityTable'
import DemoDataBanner from '../components/ui/DemoDataBanner'
import EmptyState from '../components/ui/EmptyState'

export default function DeletionRequestsPage({
  requests = [],
  resources = [],
  onNewRequest,
}) {
  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">
            Deletion Requests & Verification Log
          </h1>
          <p className="mt-0.5 text-xs text-slate-500">
            Monitor queued, processing, verified, incomplete, and failed synthetic deletion requests.
          </p>
        </div>
        <button
          type="button"
          onClick={onNewRequest}
          className="inline-flex items-center gap-2 rounded-lg bg-navy-900 px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-navy-800"
        >
          <Plus className="h-4 w-4" aria-hidden />
          New deletion request
        </button>
      </div>

      <DemoDataBanner />

      {requests.length === 0 ? (
        <EmptyState
          icon={Inbox}
          title="No deletion requests found"
          description="Submit a simulated deletion request to inspect dependency tracking and verification outcomes."
          action={
            <button
              type="button"
              onClick={onNewRequest}
              className="rounded-lg bg-navy-900 px-4 py-2 text-sm font-medium text-white hover:bg-navy-800"
            >
              New deletion request
            </button>
          }
        />
      ) : (
        <RecentActivityTable
          requests={requests}
          resources={resources}
          limit={100}
        />
      )}
    </div>
  )
}
