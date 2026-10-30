import StatusBadge from '../ui/StatusBadge'
import EmptyState from '../ui/EmptyState'
import { Inbox } from 'lucide-react'
import { getVerificationReportUrl } from '../../api/traceproof'

function formatTimestamp(iso) {
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(iso))
  } catch {
    return iso
  }
}

export default function RecentActivityTable({ requests, resources = [], limit = 5 }) {
  const rows = requests.slice(0, limit)

  return (
    <section
      className="rounded-xl border border-slate-200 bg-white shadow-sm"
      aria-labelledby="recent-activity-title"
    >
      <div className="border-b border-slate-200 px-5 py-4">
        <h2 id="recent-activity-title" className="text-base font-semibold text-slate-900">
          Recent deletion activity
        </h2>
        <p className="mt-1 text-sm text-slate-500">Sample request log (demo data).</p>
      </div>
      {rows.length === 0 ? (
        <div className="p-5">
          <EmptyState
            icon={Inbox}
            title="No deletion requests yet"
            description="Simulated requests you create will appear here."
          />
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/80 text-xs font-medium uppercase tracking-wide text-slate-500">
                <th scope="col" className="px-5 py-3">
                  Request ID
                </th>
                <th scope="col" className="px-5 py-3">
                  Resource
                </th>
                <th scope="col" className="px-5 py-3">
                  Status
                </th>
                <th scope="col" className="px-5 py-3">
                  Targets checked
                </th>
                <th scope="col" className="px-5 py-3">
                  Timestamp
                </th>
                <th scope="col" className="px-5 py-3">Report</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rows.map((row) => (
                <tr key={row.request_id ?? row.id} className="hover:bg-slate-50/50">
                  <td className="whitespace-nowrap px-5 py-3 font-mono text-xs text-slate-700">
                    {row.request_id ?? row.id}
                  </td>
                  <td className="max-w-[200px] truncate px-5 py-3 text-slate-700 sm:max-w-xs">
                    {row.resourceLabel ?? resources.find((resource) => resource.id === row.resource_id)?.name ?? row.resource_id}
                  </td>
                  <td className="px-5 py-3">
                    <StatusBadge status={row.status} />
                  </td>
                  <td className="px-5 py-3 tabular-nums text-slate-700">
                    {row.targets_checked ?? row.targetsChecked}
                  </td>
                  <td className="whitespace-nowrap px-5 py-3 text-slate-600">
                    {formatTimestamp(row.created_at ?? row.timestamp)}
                  </td>
                  <td className="whitespace-nowrap px-5 py-3">
                    {row.report_key ? (
                      <a className="font-medium text-blue-700 hover:underline" href={getVerificationReportUrl(row.request_id)} target="_blank" rel="noreferrer">
                        JSON report
                      </a>
                    ) : row.status === 'Pending' || row.status === 'Processing' ? (
                      <span className="text-slate-400">Preparing…</span>
                    ) : (
                      <span className="text-slate-400">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
