import { FileText } from 'lucide-react'
import DemoDataBanner from '../components/ui/DemoDataBanner'
import StatusBadge from '../components/ui/StatusBadge'
import { getVerificationReportUrl } from '../api/traceproof'

function formatDate(iso) {
  if (!iso) return 'Date unavailable'
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(iso))
}

export default function VerificationReportsPage({ requests }) {
  const reports = requests.filter((request) => request.report_key)
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <DemoDataBanner />
      <header>
        <h1 className="text-xl font-semibold text-slate-900">Verification reports</h1>
        <p className="mt-1 text-sm text-slate-600">Reports contain synthetic simulation results and are available through short-lived private download links.</p>
      </header>
      {reports.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center">
          <FileText className="mx-auto h-7 w-7 text-slate-400" aria-hidden />
          <p className="mt-3 text-sm font-medium text-slate-700">No completed reports yet</p>
          <p className="mt-1 text-sm text-slate-500">A report link will appear after an asynchronous request finishes.</p>
        </div>
      ) : (
        <ul className="list-none space-y-4 p-0">
          {reports.map((request) => (
            <li key={request.request_id} className="flex gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="rounded-lg bg-slate-100 p-2.5 text-slate-600"><FileText className="h-5 w-5" aria-hidden /></div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-sm text-slate-800">{request.request_id}</span>
                  <StatusBadge status={request.status} />
                </div>
                <p className="mt-2 text-sm text-slate-700">Resource: {request.resource_id}</p>
                <p className="mt-1 text-xs text-slate-500">Generated {formatDate(request.report_created_at)} · JSON simulation report</p>
                <a className="mt-3 inline-block text-sm font-medium text-blue-700 hover:underline" href={getVerificationReportUrl(request.request_id)} target="_blank" rel="noreferrer">Open private report download</a>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
