import { Info } from 'lucide-react'

export default function DemoDataBanner({ compact = false }) {
  if (compact) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-md border border-amber-200 bg-amber-50 px-2 py-1 text-xs font-medium text-amber-800">
        <Info className="h-3.5 w-3.5 shrink-0" aria-hidden />
        Demo data
      </span>
    )
  }

  return (
    <div
      className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
      role="status"
    >
      <Info className="mt-0.5 h-4 w-4 shrink-0 text-amber-700" aria-hidden />
      <div>
        <p className="font-medium">Demo data</p>
        <p className="mt-0.5 text-amber-800/90">
          All resources, requests, and metrics shown here are fictional sample
          data. No AWS account is connected and no real deletions are performed.
        </p>
      </div>
    </div>
  )
}
