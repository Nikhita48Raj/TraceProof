import { useState } from 'react'
import {
  AlertTriangle,
  CheckCircle2,
  Copy,
  Download,
  ExternalLink,
  Eye,
  FileCheck,
  FileText,
  ShieldAlert,
} from 'lucide-react'
import DemoDataBanner from '../components/ui/DemoDataBanner'
import StatusBadge from '../components/ui/StatusBadge'
import Modal from '../components/ui/Modal'
import { getVerificationReport, getVerificationReportUrl } from '../api/traceproof'

function formatDate(iso) {
  if (!iso) return 'Date unavailable'
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(iso))
  } catch {
    return iso
  }
}

export default function VerificationReportsPage({ requests = [], resources = [] }) {
  const [activeReport, setActiveReport] = useState(null)
  const [loadingReport, setLoadingReport] = useState(false)
  const [reportError, setReportError] = useState('')
  const [copied, setCopied] = useState(false)

  // In both local and AWS mode, completed requests have verification reports
  const completedRequests = requests.filter((r) =>
    ['Verified', 'Incomplete', 'Failed'].includes(r.status)
  )

  const handleOpenReport = async (reqId) => {
    setLoadingReport(true)
    setReportError('')
    setActiveReport(null)
    try {
      const data = await getVerificationReport(reqId)
      setActiveReport(data)
    } catch (err) {
      setReportError(err.message || 'Unable to load verification report.')
    } finally {
      setLoadingReport(false)
    }
  }

  const handleCopyJson = () => {
    if (!activeReport) return
    navigator.clipboard?.writeText(JSON.stringify(activeReport, null, 2))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const getResourceName = (id) => {
    return resources.find((r) => r.id === id)?.name || id
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <h1 className="text-xl font-bold tracking-tight text-slate-900">
          Verification Reports & Audit Artifacts
        </h1>
        <p className="mt-0.5 text-xs text-slate-500">
          Cryptographically auditable synthetic verification reports storing graph traversal outcomes, task executions, and remaining target states.
        </p>
      </div>

      <DemoDataBanner />

      {completedRequests.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-12 text-center shadow-sm">
          <FileText className="mx-auto h-8 w-8 text-slate-400" aria-hidden />
          <h3 className="mt-3 text-sm font-semibold text-slate-900">No completed verification reports yet</h3>
          <p className="mt-1 text-xs text-slate-500">
            Submit a deletion request from the Overview or Deletion Requests page. When the simulation finishes, its verification report will be generated here.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-500 px-1">
            <span>{completedRequests.length} verification report{completedRequests.length === 1 ? '' : 's'} available</span>
            <span>Reports stored securely in JSON format</span>
          </div>

          <div className="grid gap-4">
            {completedRequests.map((request) => {
              const reqId = request.request_id || request.id
              const resId = request.resource_id || request.resourceId
              const resName = getResourceName(resId)

              return (
                <article
                  key={reqId}
                  className="flex flex-col justify-between gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md sm:flex-row sm:items-center"
                >
                  <div className="flex items-start gap-3.5 min-w-0">
                    <div className="mt-0.5 rounded-lg bg-navy-900/5 p-2.5 text-navy-900 shrink-0">
                      <FileCheck className="h-5 w-5" aria-hidden />
                    </div>
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-mono text-xs font-semibold text-slate-900">
                          {reqId}
                        </span>
                        <StatusBadge status={request.status} />
                      </div>
                      <p className="mt-1 text-xs font-medium text-slate-800">
                        Target Resource: <span className="text-slate-600">{resName} ({resId})</span>
                      </p>
                      <div className="mt-1.5 flex flex-wrap items-center gap-2 text-[11px] text-slate-500">
                        <span>Generated: {formatDate(request.report_created_at || request.created_at || request.timestamp)}</span>
                        <span>·</span>
                        <span>Targets Checked: {request.targets_checked ?? 0}</span>
                        <span>·</span>
                        <span>Scope: Registered Dependency Closure</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0 sm:self-center">
                    <button
                      type="button"
                      onClick={() => handleOpenReport(reqId)}
                      className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 shadow-xs hover:bg-slate-50"
                    >
                      <Eye className="h-3.5 w-3.5" />
                      View Report
                    </button>
                    <a
                      href={getVerificationReportUrl(reqId)}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1.5 rounded-lg bg-navy-900 px-3 py-1.5 text-xs font-medium text-white shadow-xs hover:bg-navy-800"
                    >
                      <Download className="h-3.5 w-3.5" />
                      Download JSON
                    </a>
                  </div>
                </article>
              )
            })}
          </div>
        </div>
      )}

      {/* Interactive Report Viewer Modal */}
      {(activeReport || loadingReport || reportError) && (
        <Modal
          open={Boolean(activeReport || loadingReport || reportError)}
          onClose={() => {
            setActiveReport(null)
            setReportError('')
          }}
          title="Verification Report Inspection"
          footer={
            <div className="flex w-full items-center justify-between">
              {activeReport && (
                <button
                  type="button"
                  onClick={handleCopyJson}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
                >
                  <Copy className="h-3.5 w-3.5" />
                  {copied ? 'Copied to Clipboard' : 'Copy JSON'}
                </button>
              )}
              <button
                type="button"
                onClick={() => {
                  setActiveReport(null)
                  setReportError('')
                }}
                className="rounded-lg bg-navy-900 px-4 py-1.5 text-xs font-medium text-white hover:bg-navy-800"
              >
                Close
              </button>
            </div>
          }
        >
          {loadingReport && (
            <div className="p-8 text-center text-xs text-slate-500">
              Fetching verification report artifact...
            </div>
          )}

          {reportError && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-xs text-red-800">
              <strong>Error:</strong> {reportError}
            </div>
          )}

          {activeReport && (
            <div className="space-y-4 text-xs">
              {/* Header Box */}
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <span className="text-[10px] uppercase font-semibold text-slate-500">
                      Report ID
                    </span>
                    <p className="font-mono text-xs font-bold text-slate-900">
                      {activeReport.request_id}
                    </p>
                  </div>
                  <StatusBadge status={activeReport.status} />
                </div>
                <div className="mt-2 grid grid-cols-2 gap-2 text-[11px] text-slate-600">
                  <div>
                    <span className="text-slate-400">Target Root:</span>{' '}
                    <strong>{activeReport.resource_id}</strong>
                  </div>
                  <div>
                    <span className="text-slate-400">Closure Scope:</span>{' '}
                    <span>{activeReport.scope || 'Registered dependency closure'}</span>
                  </div>
                </div>
              </div>

              {/* Task Breakdown */}
              {activeReport.task_results && (
                <div>
                  <h4 className="font-semibold uppercase tracking-wider text-slate-600 text-[11px]">
                    Verified Targets Execution State
                  </h4>
                  <div className="mt-1.5 max-h-36 space-y-1 overflow-y-auto rounded-lg border border-slate-200 p-2">
                    {Object.entries(activeReport.task_results).map(([tId, ok]) => (
                      <div
                        key={tId}
                        className="flex items-center justify-between rounded bg-slate-50 px-2 py-1 text-xs"
                      >
                        <span className="font-mono text-slate-800">{tId}</span>
                        <span
                          className={`rounded px-1.5 py-0.2 text-[10px] font-semibold ${
                            ok ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {ok ? 'SIMULATED_DELETED' : 'SIMULATED_FAILED'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Raw JSON View */}
              <div>
                <h4 className="font-semibold uppercase tracking-wider text-slate-600 text-[11px]">
                  Raw Report Payload
                </h4>
                <pre className="mt-1.5 max-h-48 overflow-x-auto rounded-lg bg-slate-900 p-3 font-mono text-[11px] text-slate-100">
                  {JSON.stringify(activeReport, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </Modal>
      )}
    </div>
  )
}
