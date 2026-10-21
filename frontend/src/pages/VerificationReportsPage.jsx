import { FileText } from 'lucide-react'
import DemoDataBanner from '../components/ui/DemoDataBanner'
import StatusBadge from '../components/ui/StatusBadge'

const SAMPLE_REPORTS = [
  {
    id: 'VR-2026-0012',
    requestId: 'DR-2026-0041',
    summary: 'All lineage targets absent after verification pass',
    status: 'Verified',
    generated: '2026-10-18T15:00:00Z',
  },
  {
    id: 'VR-2026-0011',
    requestId: 'DR-2026-0040',
    summary:
      'Derived DynamoDB row still present — verification incomplete (demo scenario)',
    status: 'Incomplete',
    generated: '2026-10-17T10:30:00Z',
  },
]

function formatDate(iso) {
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(
    new Date(iso),
  )
}

export default function VerificationReportsPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <DemoDataBanner />
      <ul className="list-none space-y-4 p-0">
        {SAMPLE_REPORTS.map((report) => (
          <li
            key={report.id}
            className="flex gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
          >
            <div className="rounded-lg bg-slate-100 p-2.5 text-slate-600">
              <FileText className="h-5 w-5" aria-hidden />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-sm text-slate-800">{report.id}</span>
                <StatusBadge status={report.status} />
              </div>
              <p className="mt-2 text-sm text-slate-700">{report.summary}</p>
              <p className="mt-2 text-xs text-slate-500">
                Request {report.requestId} · Generated {formatDate(report.generated)}{' '}
                (demo)
              </p>
            </div>
          </li>
        ))}
      </ul>
      <p className="text-sm text-slate-500">
        PDF export and audit trails will be available in a later milestone.
      </p>
    </div>
  )
}
