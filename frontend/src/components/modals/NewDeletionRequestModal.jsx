import { useState } from 'react'
import Modal from '../ui/Modal'

export default function NewDeletionRequestModal({ open, onClose, onSubmit, resources, submitting: requestSubmitting }) {
  const [resourceId, setResourceId] = useState('')
  const [error, setError] = useState('')
  const [simulateFailure, setSimulateFailure] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const selected = resources.find((r) => r.id === resourceId)
  const isSubmitting = submitting || requestSubmitting

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!selected) {
      setError('Select a registered resource to continue.')
      return
    }
    setError('')
    setSubmitting(true)
    try {
      const submitted = await onSubmit({ resource_id: selected.id, simulate_failure: simulateFailure })
      if (submitted) {
        setResourceId('')
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
            {isSubmitting ? 'Processing…' : 'Simulate request'}
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
          {resources.map((r) => (
            <option key={r.id} value={r.id}>
              {r.name} ({r.type})
            </option>
          ))}
        </select>
        <label className="mt-4 flex items-center gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={simulateFailure}
            disabled={isSubmitting}
            onChange={(e) => setSimulateFailure(e.target.checked)}
            className="rounded border-slate-300"
          />
          Simulate a dependent-resource deletion failure
        </label>
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
              These registered resources will be checked in the simulation.
            </p>
            <ul className="mt-3 space-y-2">
              <li className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm">
                <span className="font-medium text-slate-800">Primary:</span>{' '}
                {selected.name} ({selected.type})
              </li>
              {selected.depends_on.length === 0 && !resources.some((r) => r.depends_on.includes(selected.id)) ? (
                <li className="text-sm text-slate-500 italic">No downstream dependents.</li>
              ) : (
                resources.filter((r) => r.id === selected.id || r.depends_on.includes(selected.id)).filter((r) => r.id !== selected.id).map((dep) => (
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
