import { useMemo, useState } from 'react'
import DashboardLayout from './components/layout/DashboardLayout'
import NewDeletionRequestModal from './components/modals/NewDeletionRequestModal'
import { INITIAL_DELETION_REQUESTS, TOTAL_REGISTERED_RESOURCES } from './data/sampleData'
import OverviewPage from './pages/OverviewPage'
import ResourceLineagePage from './pages/ResourceLineagePage'
import DeletionRequestsPage from './pages/DeletionRequestsPage'
import VerificationReportsPage from './pages/VerificationReportsPage'
import ExperimentsPage from './pages/ExperimentsPage'
import SettingsPage from './pages/SettingsPage'

function computeStats(requests) {
  return {
    total: TOTAL_REGISTERED_RESOURCES,
    pending: requests.filter((r) => r.status === 'Pending').length,
    verified: requests.filter((r) => r.status === 'Verified').length,
    incomplete: requests.filter((r) => r.status === 'Incomplete').length,
  }
}

export default function App() {
  const [activePage, setActivePage] = useState('overview')
  const [requests, setRequests] = useState(INITIAL_DELETION_REQUESTS)
  const [modalOpen, setModalOpen] = useState(false)

  const stats = useMemo(() => computeStats(requests), [requests])

  const handleSimulatedSubmit = (newRequest) => {
    setRequests((prev) => [newRequest, ...prev])
  }

  const renderPage = () => {
    switch (activePage) {
      case 'lineage':
        return <ResourceLineagePage />
      case 'requests':
        return (
          <DeletionRequestsPage
            requests={requests}
            onNewRequest={() => setModalOpen(true)}
          />
        )
      case 'reports':
        return <VerificationReportsPage />
      case 'experiments':
        return <ExperimentsPage />
      case 'settings':
        return <SettingsPage />
      case 'overview':
      default:
        return (
          <OverviewPage
            requests={requests}
            stats={stats}
            onNewRequest={() => setModalOpen(true)}
          />
        )
    }
  }

  return (
    <>
      <DashboardLayout activePage={activePage} onNavigate={setActivePage}>
        {renderPage()}
      </DashboardLayout>
      <NewDeletionRequestModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleSimulatedSubmit}
      />
    </>
  )
}
