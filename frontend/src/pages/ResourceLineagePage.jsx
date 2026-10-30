import { useState, useMemo } from 'react'
import {
  ArrowRight,
  Database,
  FileText,
  GitBranch,
  HardDrive,
  Info,
  Layers,
  Search,
  ShieldCheck,
  Trash2,
} from 'lucide-react'
import DependencyGraph from '../components/overview/DependencyGraph'
import DemoDataBanner from '../components/ui/DemoDataBanner'

export default function ResourceLineagePage({
  resources = [],
  onNewRequestWithResource,
}) {
  const [selectedId, setSelectedId] = useState(resources[0]?.id || null)
  const [filterType, setFilterType] = useState('ALL')
  const [searchQuery, setSearchQuery] = useState('')

  // Compute relationships map
  const { resourceMap, dependentsMap, closureMap } = useMemo(() => {
    const map = new Map(resources.map((r) => [r.id, r]))
    const dependents = new Map()
    for (const r of resources) {
      dependents.set(r.id, [])
    }
    for (const r of resources) {
      for (const parentId of r.depends_on || []) {
        if (!dependents.has(parentId)) dependents.set(parentId, [])
        dependents.get(parentId).push(r.id)
      }
    }

    // Compute closure for each resource
    const closures = new Map()
    for (const r of resources) {
      const set = new Set()
      const queue = [r.id]
      while (queue.length > 0) {
        const curr = queue.shift()
        if (set.has(curr)) continue
        set.add(curr)
        for (const childId of dependents.get(curr) || []) {
          queue.push(childId)
        }
      }
      closures.set(r.id, Array.from(set))
    }

    return { resourceMap: map, dependentsMap: dependents, closureMap: closures }
  }, [resources])

  const selectedResource = resourceMap.get(selectedId) || resources[0] || null
  const selectedClosure = selectedResource ? closureMap.get(selectedResource.id) || [] : []
  const selectedDirectDependents = selectedResource ? dependentsMap.get(selectedResource.id) || [] : []

  const filteredResources = useMemo(() => {
    return resources.filter((r) => {
      const matchesType = filterType === 'ALL' || r.type.toUpperCase() === filterType.toUpperCase()
      const matchesSearch =
        searchQuery === '' ||
        r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.id.toLowerCase().includes(searchQuery.toLowerCase())
      return matchesType && matchesSearch
    })
  }, [resources, filterType, searchQuery])

  const typeOptions = useMemo(() => {
    const types = new Set(resources.map((r) => r.type))
    return ['ALL', ...Array.from(types)]
  }, [resources])

  const getTypeIcon = (type) => {
    switch ((type || '').toLowerCase()) {
      case 'dynamodb':
        return <Database className="h-4 w-4 text-indigo-600" />
      case 's3':
        return <HardDrive className="h-4 w-4 text-amber-600" />
      default:
        return <FileText className="h-4 w-4 text-slate-500" />
    }
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">
            Resource Lineage & Dependency Closure
          </h1>
          <p className="mt-0.5 text-xs text-slate-500">
            Inspect registered cloud resources, upstream prerequisites, and downstream dependent datasets.
          </p>
        </div>
      </div>

      <DemoDataBanner />

      {/* Dependency Graph */}
      <DependencyGraph
        resources={resources}
        selectedResourceId={selectedResource?.id}
        onSelectResource={(id) => setSelectedId(id)}
      />

      {/* Directory & Inspector Grid */}
      <div className="grid gap-6 lg:grid-cols-12">
        {/* Left Column: Registered Resources List */}
        <section className="flex flex-col rounded-xl border border-slate-200 bg-white shadow-sm lg:col-span-7">
          <div className="border-b border-slate-200 p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-sm font-semibold text-slate-900">
                  Registered Resources ({filteredResources.length})
                </h2>
                <p className="text-xs text-slate-500">
                  Click any resource to inspect its full dependency closure.
                </p>
              </div>

              {/* Filters */}
              <div className="flex flex-wrap items-center gap-2">
                <div className="relative">
                  <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search resources..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-40 rounded-lg border border-slate-200 py-1.5 pl-8 pr-3 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-navy-900"
                  />
                </div>
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="rounded-lg border border-slate-200 py-1.5 pl-2 pr-6 text-xs text-slate-700 focus:outline-none focus:ring-1 focus:ring-navy-900"
                >
                  {typeOptions.map((t) => (
                    <option key={t} value={t}>
                      {t === 'ALL' ? 'All Types' : t}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="max-h-[520px] divide-y divide-slate-100 overflow-y-auto">
            {filteredResources.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500">
                No matching resources found.
              </div>
            ) : (
              filteredResources.map((res) => {
                const isSelected = selectedResource?.id === res.id
                const downstreamCount = dependentsMap.get(res.id)?.length || 0
                const closureCount = (closureMap.get(res.id)?.length || 1) - 1

                return (
                  <div
                    key={res.id}
                    onClick={() => setSelectedId(res.id)}
                    className={`flex cursor-pointer items-start justify-between gap-3 p-4 transition-colors ${
                      isSelected
                        ? 'bg-blue-50/70 border-l-4 border-l-blue-600'
                        : 'hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-start gap-3 min-w-0">
                      <div className="mt-0.5 rounded-lg bg-slate-100 p-2 shrink-0">
                        {getTypeIcon(res.type)}
                      </div>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="truncate text-sm font-semibold text-slate-900">
                            {res.name}
                          </p>
                          <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-600">
                            {res.type}
                          </span>
                        </div>
                        <p className="mt-0.5 font-mono text-xs text-slate-500">
                          ID: {res.id}
                        </p>
                        <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-slate-500">
                          <span>
                            Prerequisites: <strong className="text-slate-700">{(res.depends_on || []).length}</strong>
                          </span>
                          <span>·</span>
                          <span>
                            Direct dependents: <strong className="text-slate-700">{downstreamCount}</strong>
                          </span>
                          <span>·</span>
                          <span>
                            Closure size: <strong className="text-blue-700">{closureCount + 1}</strong>
                          </span>
                        </div>
                      </div>
                    </div>

                    <ArrowRight
                      className={`h-4 w-4 shrink-0 transition-transform ${
                        isSelected ? 'translate-x-1 text-blue-600' : 'text-slate-300'
                      }`}
                    />
                  </div>
                )
              })
            )}
          </div>
        </section>

        {/* Right Column: Selected Resource Inspector */}
        <section className="flex flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm lg:col-span-5">
          {selectedResource ? (
            <div className="space-y-5">
              <div className="flex items-start justify-between border-b border-slate-100 pb-4">
                <div className="flex items-start gap-3">
                  <div className="rounded-lg bg-navy-900/10 p-2.5 text-navy-900">
                    {getTypeIcon(selectedResource.type)}
                  </div>
                  <div>
                    <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-slate-600">
                      {selectedResource.type} Resource
                    </span>
                    <h2 className="mt-1 text-base font-bold text-slate-900">
                      {selectedResource.name}
                    </h2>
                    <p className="font-mono text-xs text-slate-500">
                      {selectedResource.id}
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => onNewRequestWithResource?.(selectedResource.id)}
                  className="inline-flex items-center gap-1.5 rounded-lg bg-navy-900 px-3 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-navy-800"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  Simulate Deletion
                </button>
              </div>

              {/* Direct Prerequisites */}
              <div>
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Direct Prerequisites ({selectedResource.depends_on?.length || 0})
                </h3>
                <p className="text-[11px] text-slate-400">
                  Resources that this record directly depends on.
                </p>
                <div className="mt-2 space-y-1.5">
                  {(!selectedResource.depends_on || selectedResource.depends_on.length === 0) ? (
                    <div className="rounded-lg border border-dashed border-slate-200 p-2.5 text-center text-xs text-slate-400">
                      Root resource (No upstream dependencies).
                    </div>
                  ) : (
                    selectedResource.depends_on.map((pId) => {
                      const parent = resourceMap.get(pId)
                      return (
                        <div
                          key={pId}
                          onClick={() => setSelectedId(pId)}
                          className="flex cursor-pointer items-center justify-between rounded-lg border border-slate-200 bg-slate-50/60 p-2.5 text-xs hover:bg-slate-100"
                        >
                          <div className="flex items-center gap-2">
                            {getTypeIcon(parent?.type)}
                            <span className="font-medium text-slate-800">
                              {parent?.name || pId}
                            </span>
                            <span className="font-mono text-[10px] text-slate-400">
                              ({pId})
                            </span>
                          </div>
                          <span className="rounded bg-slate-200/80 px-1.5 py-0.5 text-[10px] text-slate-600">
                            Prerequisite
                          </span>
                        </div>
                      )
                    })
                  )}
                </div>
              </div>

              {/* Downstream Dependents */}
              <div>
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Direct Downstream Dependents ({selectedDirectDependents.length})
                </h3>
                <p className="text-[11px] text-slate-400">
                  Resources that directly depend on this record.
                </p>
                <div className="mt-2 space-y-1.5">
                  {selectedDirectDependents.length === 0 ? (
                    <div className="rounded-lg border border-dashed border-slate-200 p-2.5 text-center text-xs text-slate-400">
                      Leaf resource (No downstream dependents).
                    </div>
                  ) : (
                    selectedDirectDependents.map((depId) => {
                      const dep = resourceMap.get(depId)
                      return (
                        <div
                          key={depId}
                          onClick={() => setSelectedId(depId)}
                          className="flex cursor-pointer items-center justify-between rounded-lg border border-slate-200 bg-slate-50/60 p-2.5 text-xs hover:bg-slate-100"
                        >
                          <div className="flex items-center gap-2">
                            {getTypeIcon(dep?.type)}
                            <span className="font-medium text-slate-800">
                              {dep?.name || depId}
                            </span>
                            <span className="font-mono text-[10px] text-slate-400">
                              ({depId})
                            </span>
                          </div>
                          <span className="rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-medium text-amber-800">
                            Dependent
                          </span>
                        </div>
                      )
                    })
                  )}
                </div>
              </div>

              {/* Full Dependency Closure */}
              <div>
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-blue-900">
                    Full Transitive Closure ({selectedClosure.length} Targets)
                  </h3>
                  <span className="rounded bg-blue-100 px-2 py-0.5 text-[10px] font-semibold text-blue-800">
                    TraceProof Scope
                  </span>
                </div>
                <p className="mt-0.5 text-[11px] text-slate-500">
                  If this resource is requested for deletion, TraceProof verifies all {selectedClosure.length} registered targets:
                </p>
                <div className="mt-2.5 max-h-48 space-y-1.5 overflow-y-auto rounded-lg border border-blue-100 bg-blue-50/30 p-2.5 text-xs">
                  {selectedClosure.map((cId) => {
                    const item = resourceMap.get(cId)
                    const isRoot = cId === selectedResource.id
                    return (
                      <div
                        key={cId}
                        className={`flex items-center justify-between rounded p-2 text-xs ${
                          isRoot ? 'bg-white font-semibold shadow-xs' : 'bg-white/70'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[10px] text-slate-400">
                            {isRoot ? 'ROOT' : 'DEP'}
                          </span>
                          <span className="text-slate-800">{item?.name || cId}</span>
                        </div>
                        <span className="font-mono text-[10px] text-slate-500">
                          {cId}
                        </span>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex h-64 items-center justify-center text-center text-xs text-slate-400">
              Select a resource to inspect its lineage.
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
