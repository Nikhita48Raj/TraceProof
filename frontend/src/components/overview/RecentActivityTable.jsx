import { useState } from 'react'
import StatusBadge from '../ui/StatusBadge'
import EmptyState from '../ui/EmptyState'
import Modal from '../ui/Modal'
import { Inbox, ExternalLink, FileText, CheckCircle2, AlertTriangle, AlertOctagon, X, Copy, Check } from 'lucide-react'
import { getVerificationReportUrl } from '../../api/traceproof'

function formatTimestamp(iso) {
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(iso))
  } catch {
    return iso || '—'
  }
}

export default function RecentActivityTable({
  requests = [],
  resources = [],
  limit = 20,
  onViewReport = null,
}) {
  const [selectedRequest, setSelectedRequest] = useState(null)
  const [copiedId, setCopiedId] = useState(false)

  const rows = limit ? requests.slice(0, limit) : requests

  const handleCopyId = (text) => {
    navigator.clipboard?.writeText(text)
    setCopiedId(true)
    setTimeout(() => setCopiedId(false), 2000)
  }

  const getResourceName = (id) => {
    return resources.find((r) => r.id === id)?.name || id
  }

  return (
    <>
      <section
        className="rounded-xl border border-slate-200 bg-white shadow-sm"
        aria-labelledby="recent-activity-title"
      >
        <div className="border-b border-slate-200 px-5 py-4">
          <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 id="recent-activity-title" className="text-base font-semibold text-slate-900">
                Recent Deletion Activity
              </h2>
              <p className="text-xs text-slate-500">
                Track asynchronous deletion simulation jobs, dependency verification, and report outcomes.
              </p>
            </div>
            <span className="text-xs text-slate-500">
              Showing {rows.length} of {requests.length} requests
            </span>
          </div>
        </div>

        {rows.length === 0 ? (
          <div className="p-8">
            <EmptyState
              icon={Inbox}
              title="No deletion requests yet"
              description="Create a simulated deletion request to see real-time verification and dependency tracking."
            />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/80 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                  <th scope="col" className="px-5 py-3">Request ID</th>
                  <th scope="col" className="px-5 py-3">Root Resource</th>
                  <th scope="col" className="px-5 py-3">Status</th>
                  <th scope="col" className="px-5 py-3 text-center">Targets Checked</th>
                  <th scope="col" className="px-5 py-3">Timestamp</th>
                  <th scope="col" className="px-5 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {rows.map((row) => {
                  const reqId = row.request_id || row.id
                  const resId = row.resource_id || row.resourceId
                  const resName = getResourceName(resId)
                  const targets = row.targets_checked ?? row.targetsChecked ?? 0

                  return (
                    <tr
                      key={reqId}
                      className="cursor-pointer hover:bg-slate-50/70 transition-colors"
                      onClick={() => setSelectedRequest(row)}
                    >
                      <td className="whitespace-nowrap px-5 py-3.5 font-mono text-xs font-medium text-slate-800">
                        {reqId.length > 18 ? `${reqId.slice(0, 8)}…${reqId.slice(-4)}` : reqId}
                      </td>
                      <td className="max-w-[220px] truncate px-5 py-3.5 text-xs text-slate-800" title={resName}>
                        <div className="font-medium text-slate-900">{resName}</div>
                        <div className="font-mono text-[10px] text-slate-400">{resId}</div>
                      </td>
                      <td className="px-5 py-3.5 whitespace-nowrap">
                        <StatusBadge status={row.status} />
                      </td>
                      <td className="px-5 py-3.5 text-center tabular-nums text-xs font-semibold text-slate-700">
                        {targets}
                      </td>
                      <td className="whitespace-nowrap px-5 py-3.5 text-xs text-slate-500">
                        {formatTimestamp(row.created_at || row.timestamp)}
                      </td>
                      <td className="whitespace-nowrap px-5 py-3.5 text-right">
                        <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                          <button
                            type="button"
                            onClick={() => setSelectedRequest(row)}
                            className="rounded px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                          >
                            Details
                          </button>
                          {row.status === 'Verified' || row.status === 'Incomplete' ? (
                            <a
                              href={getVerificationReportUrl(reqId)}
                              target="_blank"
                              rel="noreferrer"
                              className="inline-flex items-center gap-1 rounded px-2 py-1 text-xs font-medium text-blue-700 hover:bg-blue-50"
                              title="Download JSON Verification Report"
                            >
                              <FileText className="h-3 w-3" />
                              Report
                            </a>
                          ) : (
                            <span className="text-xs text-slate-400">—</span>
                          )}
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Request Inspection Modal */}
      {selectedRequest && (
        <Modal
          open={Boolean(selectedRequest)}
          onClose={() => setSelectedRequest(null)}
          title="Deletion Request Details"
          footer={
            <div className="flex justify-between w-full items-center">
              <span className="text-xs text-slate-400">
                Simulation Only · No Physical Erasure
              </span>
              <div className="flex gap-2">
                {(selectedRequest.status === 'Verified' || selectedRequest.status === 'Incomplete') && (
                  <a
                    href={getVerificationReportUrl(selectedRequest.request_id || selectedRequest.id)}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 rounded-lg bg-navy-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-navy-800"
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                    Open JSON Report
                  </a>
                )}
                <button
                  type="button"
                  onClick={() => setSelectedRequest(null)}
                  className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
                >
                  Close
                </button>
              </div>
            </div>
          }
        >
          <div className="space-y-4">
            {/* ID & Status Header */}
            <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-200 bg-slate-50 p-3">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                  Request Identifier
                </p>
                <div className="mt-1 flex items-center gap-2">
                  <span className="font-mono text-xs font-semibold text-slate-900">
                    {selectedRequest.request_id || selectedRequest.id}
                  </span>
                  <button
                    type="button"
                    onClick={() => handleCopyId(selectedRequest.request_id || selectedRequest.id)}
                    className="rounded p-1 text-slate-400 hover:bg-slate-200 hover:text-slate-700"
                    title="Copy Request ID"
                  >
                    {copiedId ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
                  </button>
                </div>
              </div>
              <div className="text-right">
                <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                  Verification Status
                </p>
                <div className="mt-1">
                  <StatusBadge status={selectedRequest.status} />
                </div>
              </div>
            </div>

            {/* Request Summary Metadata */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="rounded-lg border border-slate-200 p-3">
                <span className="text-slate-500">Target Root Resource:</span>
                <p className="mt-1 font-semibold text-slate-900">
                  {getResourceName(selectedRequest.resource_id || selectedRequest.resourceId)}
                </p>
                <p className="font-mono text-[10px] text-slate-400">
                  {selectedRequest.resource_id || selectedRequest.resourceId}
                </p>
              </div>
              <div className="rounded-lg border border-slate-200 p-3">
                <span className="text-slate-500">Submitted At:</span>
                <p className="mt-1 font-semibold text-slate-900">
                  {formatTimestamp(selectedRequest.created_at || selectedRequest.timestamp)}
                </p>
                <span className="text-slate-500">Verification Approach:</span>
                <p className="font-medium text-blue-700">
                  {selectedRequest.approach || 'TraceProof Engine'}
                </p>
              </div>
            </div>

            {/* Failure Message if any */}
            {selectedRequest.failure_message && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-xs text-red-800">
                <strong>Failure Details:</strong> {selectedRequest.failure_message}
              </div>
            )}

            {/* Remaining Targets if Incomplete */}
            {selectedRequest.remaining_targets?.length > 0 && (
              <div className="rounded-lg border border-orange-200 bg-orange-50/70 p-3 text-xs">
                <div className="flex items-center gap-1.5 font-semibold text-orange-900">
                  <AlertTriangle className="h-4 w-4 text-orange-600" />
                  Incomplete Deletion Scenario Detected
                </div>
                <p className="mt-1 text-orange-800">
                  The following dependent resources remained unaddressed after simulated execution:
                </p>
                <ul className="mt-2 space-y-1">
                  {selectedRequest.remaining_targets.map((targetId) => (
                    <li key={targetId} className="flex items-center justify-between rounded bg-white px-2 py-1 text-xs">
                      <span className="font-medium text-slate-800">{getResourceName(targetId)}</span>
                      <span className="font-mono text-[10px] text-red-600">{targetId}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Task Breakdown if available */}
            {selectedRequest.task_results && Object.keys(selectedRequest.task_results).length > 0 && (
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-600">
                  Simulated Operations Per Target ({Object.keys(selectedRequest.task_results).length})
                </h4>
                <div className="mt-2 max-h-40 space-y-1 overflow-y-auto rounded-lg border border-slate-200 bg-slate-50 p-2 text-xs">
                  {Object.entries(selectedRequest.task_results).map(([targetId, success]) => (
                    <div
                      key={targetId}
                      className="flex items-center justify-between rounded bg-white px-2.5 py-1.5"
                    >
                      <div className="flex items-center gap-2">
                        {success ? (
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                        ) : (
                          <AlertTriangle className="h-3.5 w-3.5 text-orange-600" />
                        )}
                        <span className="text-slate-800">{getResourceName(targetId)}</span>
                        <span className="font-mono text-[10px] text-slate-400">({targetId})</span>
                      </div>
                      <span
                        className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                          success
                            ? 'bg-emerald-50 text-emerald-700'
                            : 'bg-orange-50 text-orange-700'
                        }`}
                      >
                        {success ? 'Simulated Delete Success' : 'Simulated Error Injected'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Modal>
      )}
    </>
  )
}
