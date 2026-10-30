import { useMemo, useState } from 'react'
import { Database, FileText, HardDrive, Layers, ShieldCheck } from 'lucide-react'

const NODE_W = 180
const NODE_H = 64
const LAYER_GAP_X = 220
const NODE_GAP_Y = 88
const PADDING = 40

export default function DependencyGraph({
  resources = [],
  selectedResourceId = null,
  onSelectResource = null,
}) {
  const [activeRoot, setActiveRoot] = useState(null)

  // Determine current active root (from prop or local state)
  const rootId = selectedResourceId || activeRoot || (resources[0]?.id ?? null)

  // Compute graph layout dynamically based on real resources
  const { nodes, edges, width, height, rootClosure } = useMemo(() => {
    if (!resources || resources.length === 0) {
      return { nodes: [], edges: [], width: 500, height: 260, rootClosure: new Set() }
    }

    const resMap = new Map(resources.map((r) => [r.id, r]))

    // Find closure for currently selected root
    const closure = new Set()
    if (rootId && resMap.has(rootId)) {
      const queue = [rootId]
      while (queue.length > 0) {
        const curr = queue.shift()
        if (closure.has(curr)) continue
        closure.add(curr)
        for (const r of resources) {
          if ((r.depends_on || []).includes(curr)) {
            queue.push(r.id)
          }
        }
      }
    }

    // Assign layers (depth from root)
    const layers = new Map()
    for (const r of resources) {
      if (!r.depends_on || r.depends_on.length === 0) {
        layers.set(r.id, 0)
      }
    }

    // Propagate depths
    let changed = true
    let passes = 0
    while (changed && passes < 10) {
      changed = false
      passes += 1
      for (const r of resources) {
        const parentDepths = (r.depends_on || [])
          .map((pId) => layers.get(pId))
          .filter((d) => d !== undefined)
        if (parentDepths.length > 0) {
          const maxParent = Math.max(...parentDepths)
          const newDepth = maxParent + 1
          if (layers.get(r.id) !== newDepth) {
            layers.set(r.id, newDepth)
            changed = true
          }
        } else if (!layers.has(r.id)) {
          layers.set(r.id, 0)
          changed = true
        }
      }
    }

    // Group nodes by layer
    const byLayer = new Map()
    for (const r of resources) {
      const depth = layers.get(r.id) ?? 0
      if (!byLayer.has(depth)) byLayer.set(depth, [])
      byLayer.get(depth).push(r)
    }

    const sortedLayers = Array.from(byLayer.keys()).sort((a, b) => a - b)
    const maxLayerNodes = Math.max(...Array.from(byLayer.values()).map((l) => l.length), 1)

    const computedNodes = []
    const nodeCoords = new Map()

    sortedLayers.forEach((layerIdx) => {
      const layerResources = byLayer.get(layerIdx)
      const x = PADDING + layerIdx * LAYER_GAP_X
      layerResources.forEach((res, indexInLayer) => {
        const y = PADDING + indexInLayer * NODE_GAP_Y
        const nodeObj = {
          ...res,
          x,
          y,
          depth: layerIdx,
          inClosure: closure.has(res.id),
          isRoot: res.id === rootId,
        }
        computedNodes.push(nodeObj)
        nodeCoords.set(res.id, { x, y })
      })
    })

    // Compute directed edges: parent (prerequisite) -> child (dependent)
    const computedEdges = []
    for (const r of resources) {
      for (const parentId of r.depends_on || []) {
        if (nodeCoords.has(parentId) && nodeCoords.has(r.id)) {
          const from = nodeCoords.get(parentId)
          const to = nodeCoords.get(r.id)
          const isHighlighted = closure.has(parentId) && closure.has(r.id)
          computedEdges.push({
            id: `${parentId}->${r.id}`,
            from,
            to,
            parentId,
            childId: r.id,
            isHighlighted,
          })
        }
      }
    }

    const totalWidth = Math.max(560, PADDING * 2 + sortedLayers.length * LAYER_GAP_X)
    const totalHeight = Math.max(260, PADDING * 2 + maxLayerNodes * NODE_GAP_Y)

    return {
      nodes: computedNodes,
      edges: computedEdges,
      width: totalWidth,
      height: totalHeight,
      rootClosure: closure,
    }
  }, [resources, rootId])

  function edgePath(from, to) {
    const fx = from.x + NODE_W
    const fy = from.y + NODE_H / 2
    const tx = to.x
    const ty = to.y + NODE_H / 2
    const midX = (fx + tx) / 2
    return `M ${fx} ${fy} C ${midX} ${fy}, ${midX} ${ty}, ${tx} ${ty}`
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
    <section
      className="flex flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
      aria-labelledby="lineage-graph-title"
    >
      <div className="mb-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div>
          <h2 id="lineage-graph-title" className="text-base font-semibold text-slate-900">
            Registered dependency graph
          </h2>
          <p className="mt-0.5 text-xs text-slate-500">
            Live directed lineage graph of registered cloud resources. Select any resource to view its dependency closure.
          </p>
        </div>
        {resources.length > 0 && (
          <div className="flex items-center gap-2">
            <label htmlFor="graph-root-selector" className="text-xs font-medium text-slate-600">
              Focus root:
            </label>
            <select
              id="graph-root-selector"
              value={rootId || ''}
              onChange={(e) => {
                setActiveRoot(e.target.value)
                onSelectResource?.(e.target.value)
              }}
              className="rounded-lg border border-slate-300 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-800 focus:bg-white focus:outline-none focus:ring-1 focus:ring-navy-900"
            >
              {resources.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} ({r.id})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="relative overflow-x-auto rounded-lg border border-slate-200 bg-slate-50/70 p-4">
        {nodes.length === 0 ? (
          <div className="flex h-48 items-center justify-center text-sm text-slate-400">
            No registered resources loaded.
          </div>
        ) : (
          <svg
            viewBox={`0 0 ${width} ${height}`}
            className="min-h-[260px] w-full"
            style={{ minWidth: `${Math.min(width, 700)}px` }}
            role="img"
            aria-label="Interactive registered dependency graph"
          >
            <defs>
              <marker
                id="arrow-default"
                markerWidth="8"
                markerHeight="8"
                refX="7"
                refY="4"
                orient="auto"
              >
                <path d="M0,0 L8,4 L0,8 Z" fill="#94a3b8" />
              </marker>
              <marker
                id="arrow-highlighted"
                markerWidth="8"
                markerHeight="8"
                refX="7"
                refY="4"
                orient="auto"
              >
                <path d="M0,0 L8,4 L0,8 Z" fill="#2563eb" />
              </marker>
            </defs>

            {/* Edges */}
            {edges.map((edge) => (
              <g key={edge.id}>
                <path
                  d={edgePath(edge.from, edge.to)}
                  fill="none"
                  stroke={edge.isHighlighted ? '#2563eb' : '#cbd5e1'}
                  strokeWidth={edge.isHighlighted ? 2.2 : 1.5}
                  strokeDasharray={edge.isHighlighted ? 'none' : '4 2'}
                  markerEnd={edge.isHighlighted ? 'url(#arrow-highlighted)' : 'url(#arrow-default)'}
                />
              </g>
            ))}

            {/* Nodes */}
            {nodes.map((node) => {
              const isSelected = node.id === rootId
              return (
                <g
                  key={node.id}
                  transform={`translate(${node.x}, ${node.y})`}
                  className="cursor-pointer transition-transform hover:scale-[1.02]"
                  onClick={() => {
                    setActiveRoot(node.id)
                    onSelectResource?.(node.id)
                  }}
                >
                  <rect
                    width={NODE_W}
                    height={NODE_H}
                    rx="8"
                    fill={isSelected ? '#1e293b' : node.inClosure ? '#ffffff' : '#f8fafc'}
                    stroke={isSelected ? '#0f172a' : node.inClosure ? '#3b82f6' : '#cbd5e1'}
                    strokeWidth={isSelected ? 2 : node.inClosure ? 2 : 1}
                    className="shadow-sm transition-colors"
                  />
                  <foreignObject width={NODE_W} height={NODE_H}>
                    <div
                      className={`flex h-full flex-col justify-center px-3 text-left ${
                        isSelected ? 'text-white' : 'text-slate-900'
                      }`}
                    >
                      <div className="flex items-center gap-1.5">
                        <span className="shrink-0">{getTypeIcon(node.type)}</span>
                        <span className="truncate text-xs font-semibold" title={node.name}>
                          {node.name}
                        </span>
                      </div>
                      <div className="mt-1 flex items-center justify-between text-[10px]">
                        <span
                          className={`font-mono truncate ${
                            isSelected ? 'text-slate-300' : 'text-slate-500'
                          }`}
                        >
                          {node.id}
                        </span>
                        <span
                          className={`rounded px-1 py-0.2 font-medium ${
                            isSelected
                              ? 'bg-slate-700 text-slate-200'
                              : 'bg-slate-100 text-slate-600'
                          }`}
                        >
                          {node.type}
                        </span>
                      </div>
                    </div>
                  </foreignObject>
                </g>
              )
            })}
          </svg>
        )}
      </div>

      <div className="mt-3 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-slate-900" /> Focus Root
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-blue-600" /> Dependent in Closure ({rootClosure.size})
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-slate-300" /> Other Registered
          </span>
        </div>
        <span>Click any node to focus on its dependency tree</span>
      </div>
    </section>
  )
}
