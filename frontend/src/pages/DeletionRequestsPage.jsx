import { Inbox, Plus } from 'lucide-react'
import RecentActivityTable from '../components/overview/RecentActivityTable'
import DemoDataBanner from '../components/ui/DemoDataBanner'
import EmptyState from '../components/ui/EmptyState'

export default function DeletionRequestsPage({ requests, onNewRequest }) {
  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-600">
          Track simulated deletion requests and verification status.
        </p>
        <button
          type="button"
          onClick={onNewRequest}
          className="inline-flex items-center gap-2 rounded-lg bg-navy-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-navy-800"
        >
          <Plus className="h-4 w-4" aria-hidden />
          New deletion request
        </button>
      </div>
      <DemoDataBanner />
      {requests.length === 0 ? (
        <EmptyState
          icon={Inbox}
          title="No deletion requests"
          description="Create a simulated request to populate this view."
          action={
            <button
              type="button"
              onClick={onNewRequest}
              className="rounded-lg bg-navy-900 px-4 py-2 text-sm font-medium text-white"
            >
              New deletion request
            </button>
          }
        />
      ) : (
        <RecentActivityTable requests={requests} limit={50} />
      )}
    </div>
  )
}
