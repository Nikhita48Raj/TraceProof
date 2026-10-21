const STYLES = {
  Verified: 'bg-[var(--color-verified-bg)] text-[var(--color-verified)] border-emerald-200',
  Pending: 'bg-[var(--color-pending-bg)] text-[var(--color-pending)] border-amber-200',
  Incomplete:
    'bg-[var(--color-incomplete-bg)] text-[var(--color-incomplete)] border-red-200',
}

export default function StatusBadge({ status }) {
  const style = STYLES[status] ?? 'bg-slate-100 text-slate-600 border-slate-200'
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${style}`}
    >
      {status}
    </span>
  )
}
