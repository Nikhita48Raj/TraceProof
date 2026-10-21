import { useState } from 'react'
import Sidebar from './Sidebar'
import TopNav from './TopNav'
import { PAGE_TITLES } from '../../data/sampleData'

export default function DashboardLayout({ activePage, onNavigate, children }) {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="flex min-h-svh min-w-0 overflow-x-hidden bg-slate-50">
      <Sidebar
        activePage={activePage}
        onNavigate={onNavigate}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
      />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopNav
          title={PAGE_TITLES[activePage] ?? 'TraceProof'}
          onMenuClick={() => setMobileOpen(true)}
        />
        <main className="flex-1 p-4 sm:p-6">{children}</main>
      </div>
    </div>
  )
}
