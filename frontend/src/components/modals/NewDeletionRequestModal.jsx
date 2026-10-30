import { useState, useEffect, useMemo } from 'react'
import Modal from '../ui/Modal'
import { AlertTriangle, Database, HardDrive, FileText, CheckCircle2 } from 'lucide-react'

export default function NewDeletionRequestModal({
  open,
  onClose,
  onSubmit,
  resources = [],
  initialResourceId = '',
  submitting: requestSubmitting,
}) {
  const [resourceId, setResourceId] = useState(initialResourceId || '')
  const [error, setError] = useState('')
  const [simulateFailure, setSimulateFailure] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (initialResourceId) {
      setResourceId(initialResourceId)
    } else if (open && !resourceId && resources.length > 0) {
      setResourceId(resources[0].id)
    }
  }, [open, initialResourceId, resources])

  const selected = resources.find((r) => r.id === resourceId)
  const isSubmitting = submitting || requestSubmitting

  // Compute full closure of targets that will be verified
  const closureTargets = useMemo(() => {
    if (!selected) return []
    const closure = []
    const visited = new Set()
    const queue = [selected.id]

    while (queue.length > 0) {
      const current = queue.shift()
      if (visited.has(current)) continue
      visited.add(current)
      const res = resources.find((r) => r.id === current)
      if (res) closure.push(res)

      for (const r of resources) {
        if ((r.depends_on || []).includes(current)) {
          queue.push(r.id)
        }
      }
    }
    return closure
  }, [selected, resources])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!selected) {
      setError('Select a registered resource to continue.')
      return
    }
    setError('')
    setSubmitting(true)
    try {
      const submitted = await onSubmit({
        resource_id: selected.id,
        simulate_failure: simulateFailure,
      })
      if (submitted) {
        setError('')
        setSimulateFailure(false)
      }
    } finally {
      setSubmitting(false)
    }
  }

  const handleClose = () => {
    if (isSubmitting) return
    setError('')
    onClose()
  }

  const getTypeIcon = (type) => {
    switch ((type || '').toLowerCase()) {
      case 'dynamodb':
        return <Database className="h-3.5 w-3.5 text-indigo-600" />
      case 's3':
        return <HardDrive className="h-3.5 w-3.5 text-amber-600" />
      default:
        return <FileText className="h-3.5 w-3.5 text-slate-500" />
    }
  }

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title="Create Simulated Deletion Request"
      footer={
        <div className="flex flex-col gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            onClick={handleClose}
            disabled={isSubmitting}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            form="new-deletion-request-form"
            disabled={isSubmitting || !resources.length}
            className="rounded-lg bg-navy-900 px-4 py-2 text-sm font-medium text-white hover:bg-navy-800 disabled:opacity-60"
          >
            {isSubmitting ? 'Submitting job…' : 'Submit Deletion Request'}
          </button>
        </div>
      }
    >
      <form id="new-deletion-request-form" onSubmit={handleSubmit} className="space-y-4">
        <div className="rounded-lg border border-blue-200 bg-blue-50/70 p-3 text-xs text-blue-900">
          <p className="font-semibold">Research Prototype Simulation</p>
          <p className="mt-0.5 text-blue-800">
            TraceProof will evaluate dependency-aware verification against the registered dependency graph without deleting real cloud data.
          </p>
        </div>

        <div>
          <label htmlFor="resource-select" className="block text-sm font-medium text-slate-700">
            Target Resource
          </label>
          <select
            id="resource-select"
            value={resourceId}
            required
            disabled={isSubmitting}
            aria-invalid={error ? 'true' : undefined}
            onChange={(e) => {
              setResourceId(e.target.value)
              setError('')
            }}
            className={`mt-1.5 w-full rounded-lg border px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-navy-900 ${
              error ? 'border-red-300' : 'border-slate-300'
            }`}
          >
            <option value="">Choose a resource…</option>
            {resources.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name} ({r.id}) — {r.type}
              </option>
            ))}
          </select>
        </div>

        {/* Failure Simulation Option */}
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
          <label className="flex items-start gap-2.5 text-xs text-slate-800 cursor-pointer">
            <input
              type="checkbox"
              checked={simulateFailure}
              disabled={isSubmitting}
              onChange={(e) => setSimulateFailure(e.target.checked)}
              className="mt-0.5 rounded border-slate-300 text-navy-900 focus:ring-navy-900"
            />
            <div>
              <span className="font-semibold text-slate-900">Simulate dependent deletion failure</span>
              <p className="mt-0.5 text-slate-500">
                Injects a simulated deletion error on a downstream dependent resource to test whether TraceProof accurately flags the workflow as <strong className="text-orange-700">Incomplete</strong>.
              </p>
            </div>
          </label>
        </div>

        {error && (
          <p className="text-xs text-red-600" role="alert">
            {error}
          </p>
        )}

        {/* Transitive Closure Preview */}
        {selected && (
          <div className="rounded-lg border border-slate-200 bg-white p-3.5">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-700">
                Affected Dependency Closure ({closureTargets.length} Targets)
              </h4>
              <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-600">
                Pre-Execution Analysis
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              TraceProof will traverse and verify each of the following registered resources:
            </p>
            <ul className="mt-2.5 max-h-36 space-y-1.5 overflow-y-auto">
              {closureTargets.map((target, idx) => {
                const isRoot = target.id === selected.id
                return (
                  <li
                    key={target.id}
                    className={`flex items-center justify-between rounded px-2.5 py-1.5 text-xs ${
                      isRoot ? 'bg-navy-900/5 font-medium' : 'bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      {getTypeIcon(target.type)}
                      <span className="text-slate-800">{target.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-[10px] text-slate-500">{target.id}</span>
                      <span
                        className={`rounded px-1 text-[10px] ${
                          isRoot
                            ? 'bg-navy-900 text-white font-medium'
                            : 'bg-slate-200 text-slate-700'
                        }`}
                      >
                        {isRoot ? 'Root' : 'Dependent'}
                      </span>
                    </div>
                  </li>
                )
              })}
            </ul>
          </div>
        )}
      </form>
    </Modal>
  )
}
