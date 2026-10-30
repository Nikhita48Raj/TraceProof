import { useEffect, useMemo, useState } from 'react'

import DashboardLayout from './components/layout/DashboardLayout'
import NewDeletionRequestModal from './components/modals/NewDeletionRequestModal'

import {
  getResources,
  getDeletionRequests,
  createDeletionRequest,
  getExperimentComparison,
} from './api/traceproof'

import OverviewPage from './pages/OverviewPage'
import ResourceLineagePage from './pages/ResourceLineagePage'
import DeletionRequestsPage from './pages/DeletionRequestsPage'
import VerificationReportsPage from './pages/VerificationReportsPage'
import ExperimentsPage from './pages/ExperimentsPage'
import SettingsPage from './pages/SettingsPage'

function computeStats(requests, resources) {
  const verified = requests.filter((r) => r.status === 'Verified').length
  const incomplete = requests.filter((r) => r.status === 'Incomplete').length
  const failed = requests.filter((r) => r.status === 'Failed').length
  const pending = requests.filter((r) => ['Pending', 'Processing'].includes(r.status)).length
  const resolved = verified + incomplete + failed
  const successRate = resolved > 0 ? `${((verified / resolved) * 100).toFixed(1)}%` : 'N/A'

  return {
    totalResources: resources.length,
    totalRequests: requests.length,
    pending,
    verified,
    incomplete,
    failed,
    successRate,
  }
}

export default function App() {
  const [activePage, setActivePage] = useState('overview')
  const [requests, setRequests] = useState([])
  const [resources, setResources] = useState([])
  const [comparison, setComparison] = useState(null)
  const [selectedResourceId, setSelectedResourceId] = useState('')

  const [modalOpen, setModalOpen] = useState(false)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  // Load data from the backend.
  useEffect(() => {
    let cancelled = false

    async function loadDashboard() {
      try {
        setLoading(true)
        setError('')

        const [resourceData, requestData, comparisonData] =
          await Promise.all([
            getResources(),
            getDeletionRequests(),
            getExperimentComparison(),
          ])

        if (cancelled) return

        setResources(resourceData)
        setRequests(requestData)
        setComparison(comparisonData)
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message ||
              'Unable to connect to the TraceProof backend.'
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadDashboard()

    return () => {
      cancelled = true
    }
  }, [])

  const stats = useMemo(
    () => computeStats(requests, resources),
    [requests, resources]
  )

  const activeRequestKey = requests
    .filter((request) => ['Pending', 'Processing'].includes(request.status))
    .map((request) => request.request_id ?? request.id)
    .filter(Boolean)
    .sort()
    .join(',')

  // Cloud requests finish asynchronously. Poll at most 30 times, then stop.
  useEffect(() => {
    if (!activeRequestKey) return undefined
    let cancelled = false
    let attempts = 0
    let timer
    const activeIds = new Set(activeRequestKey.split(','))

    const poll = async () => {
      if (cancelled || attempts >= 30) return
      attempts += 1
      try {
        const latest = await getDeletionRequests()
        if (cancelled) return
        setError('')
        setRequests(latest)
        const completed = latest.find((item) =>
          activeIds.has(item.request_id) && ['Verified', 'Incomplete', 'Failed'].includes(item.status)
        )
        if (completed) {
          const detail = completed.failure_message
            ? ` ${completed.failure_message}`
            : completed.remaining_targets?.length
              ? ` Remaining targets: ${completed.remaining_targets.join(', ')}.`
              : ''
          setNotice(`Request ${completed.status}.${detail} Simulation only; no real cloud data was deleted.`)
        } else if (attempts >= 30 && latest.some((item) => activeIds.has(item.request_id) && ['Pending', 'Processing'].includes(item.status))) {
          setNotice('Request is still processing. Status polling paused; refresh the page to check again.')
        }
      } catch (err) {
        if (!cancelled) setError(err.message || 'Unable to refresh request status.')
      }
      if (!cancelled && attempts < 30) timer = setTimeout(poll, 2000)
    }

    timer = setTimeout(poll, 1000)
    return () => {
      cancelled = true
      clearTimeout(timer)
    }
  }, [activeRequestKey])

  // Submit through the configured local or AWS API and reflect its request state.
  const handleDeletionSubmit = async (formData) => {
    const resourceId =
      typeof formData === 'string'
        ? formData
        : formData?.resource_id ?? formData?.resourceId ?? formData?.id

    if (!resourceId || !resources.some((resource) => resource.id === resourceId)) {
      setError('Please select a valid resource.')
      return false
    }

    try {
      setSubmitting(true)
      setError('')
      setNotice('')

      const result = await createDeletionRequest(
        resourceId,
        Boolean(formData?.simulate_failure ?? formData?.simulateFailure)
      )

      setRequests((previous) => [
        result,
        ...previous.filter(
          (request) => (request.request_id || request.id) !== (result.request_id || result.id)
        ),
      ])

      const failedTargets = (result.remaining_targets ?? []).map((id) =>
        resources.find((resource) => resource.id === id)?.name ?? id
      )
      setNotice(result.status === 'Pending' || result.status === 'Processing'
        ? `Request accepted. Current status: ${result.status}. Simulation only; no real cloud data was deleted.`
        : `Request created. Verification status: ${result.status}.${failedTargets.length ? ` Remaining targets: ${failedTargets.join(', ')}.` : ''} Simulation only; no real cloud data was deleted.`)

      setModalOpen(false)
      setSelectedResourceId('')
      return true
    } catch (err) {
      setError(
        err.message ||
          'Failed to submit the deletion request. Check that the backend is running.'
      )
      return false
    } finally {
      setSubmitting(false)
    }
  }

  const renderPage = () => {
    switch (activePage) {
      case 'lineage':
        return (
          <ResourceLineagePage
            resources={resources}
            onNewRequestWithResource={(id) => {
              setSelectedResourceId(id)
              setModalOpen(true)
            }}
          />
        )

      case 'requests':
        return (
          <DeletionRequestsPage
            requests={requests}
            resources={resources}
            onNewRequest={() => {
              setSelectedResourceId('')
              setModalOpen(true)
            }}
          />
        )

      case 'reports':
        return (
          <VerificationReportsPage
            requests={requests}
            resources={resources}
          />
        )

      case 'experiments':
        return <ExperimentsPage />

      case 'settings':
        return <SettingsPage />

      case 'overview':
      default:
        return (
          <OverviewPage
            requests={requests}
            resources={resources}
            stats={stats}
            comparison={comparison}
            onNewRequest={() => {
              setSelectedResourceId('')
              setModalOpen(true)
            }}
            onOpenExperiments={() => setActivePage('experiments')}
            onSelectResource={(id) => {
              setSelectedResourceId(id)
              setActivePage('lineage')
            }}
          />
        )
    }
  }

  return (
    <>
      <DashboardLayout
        activePage={activePage}
        onNavigate={setActivePage}
      >
        <div className="space-y-4">
          {error && (
            <div
              role="alert"
              className="rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-800"
            >
              <strong>API error:</strong> {error}
              <p className="mt-1">
                Check VITE_API_BASE_URL and confirm the configured API is available.
              </p>
            </div>
          )}

          {notice && (
            <div
              role="status"
              className="rounded-lg border border-emerald-300 bg-emerald-50 p-3 text-sm text-emerald-900"
            >
              {notice}
            </div>
          )}

          {loading ? (
            <div className="rounded-xl border border-slate-200 bg-white p-12 text-center text-sm text-slate-500 shadow-sm">
              Loading TraceProof data from the backend...
            </div>
          ) : (
            renderPage()
          )}

          {submitting && (
            <p className="text-sm text-slate-500" role="status">
              Processing deletion request...
            </p>
          )}

          {comparison && (
            <p className="text-xs text-slate-500">
              Research comparison loaded from the backend API.
              {' '}Simulation only; no real cloud data was deleted.
            </p>
          )}
        </div>
      </DashboardLayout>

      <NewDeletionRequestModal
        open={modalOpen}
        initialResourceId={selectedResourceId}
        onClose={() => {
          if (!submitting) {
            setModalOpen(false)
            setSelectedResourceId('')
          }
        }}
        onSubmit={handleDeletionSubmit}
        resources={resources}
        submitting={submitting || loading}
      />
    </>
  )
}
