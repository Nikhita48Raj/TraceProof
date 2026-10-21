import { useState } from 'react'
import Modal from '../ui/Modal'
import { SAMPLE_RESOURCES } from '../../data/sampleData'

function generateRequestId() {
  const n = Math.floor(Math.random() * 900) + 100
  return `DR-2026-${n}`
}

export default function NewDeletionRequestModal({ open, onClose, onSubmit }) {
  const [resourceId, setResourceId] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const selected = SAMPLE_RESOURCES.find((r) => r.id === resourceId)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!resourceId) {
      setError('Select a sample resource to continue.')
      return
    }
    setError('')
    setSubmitting(true)

    const resource = SAMPLE_RESOURCES.find((r) => r.id === resourceId)
    const targetsChecked = 1 + (resource?.dependents?.length ?? 0)

    onSubmit({
      id: generateRequestId(),
      resourceId: resource.id,
      resourceLabel: `${resource.name} (${resource.type})`,
      status: 'Pending',
      targetsChecked: 0,
      timestamp: new Date().toISOString(),
      _simulatedTargets: targetsChecked,
    })

    setSubmitting(false)
    setResourceId('')
    onClose()
  }

  const handleClose = () => {
    setError('')
    setResourceId('')
    onClose()
  }

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title="New deletion request"
      footer={
        <div className="flex flex-col gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            onClick={handleClose}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            form="new-deletion-request-form"
            disabled={submitting}
            className="rounded-lg bg-navy-900 px-4 py-2 text-sm font-medium text-white hover:bg-navy-800 disabled:opacity-60"
          >
            Simulate request
          </button>
        </div>
      }
    >
      <form id="new-deletion-request-form" onSubmit={handleSubmit}>
        <p className="mb-4 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-600">
          Simulation only — no real deletion performed.
        </p>

        <label htmlFor="resource-select" className="block text-sm font-medium text-slate-700">
          Sample resource
        </label>
        <select
          id="resource-select"
          value={resourceId}
          required
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={error ? 'resource-select-error' : undefined}
          onChange={(e) => {
            setResourceId(e.target.value)
            setError('')
          }}
          className={`mt-1.5 w-full rounded-lg border px-3 py-2 text-sm text-slate-900 focus:ring-2 focus:ring-navy-800/20 ${
            error ? 'border-red-300' : 'border-slate-200'
          }`}
        >
          <option value="">Choose a resource…</option>
          {SAMPLE_RESOURCES.map((r) => (
            <option key={r.id} value={r.id}>
              {r.name} ({r.type})
            </option>
          ))}
        </select>
        {error && (
          <p id="resource-select-error" className="mt-2 text-sm text-red-600" role="alert">
            {error}
          </p>
        )}

        {selected && (
          <div className="mt-5">
            <h3 className="text-sm font-semibold text-slate-800">
              Dependent targets to verify
            </h3>
            <p className="mt-1 text-xs text-slate-500">
              These would be checked in a full TraceProof workflow (demo list).
            </p>
            <ul className="mt-3 space-y-2">
              <li className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm">
                <span className="font-medium text-slate-800">Primary:</span>{' '}
                {selected.name} ({selected.type})
              </li>
              {selected.dependents.length === 0 ? (
                <li className="text-sm text-slate-500 italic">No downstream dependents.</li>
              ) : (
                selected.dependents.map((dep) => (
                  <li
                    key={dep.id}
                    className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700"
                  >
                    {dep.name} ({dep.type})
                  </li>
                ))
              )}
            </ul>
          </div>
        )}
      </form>
    </Modal>
  )
}
