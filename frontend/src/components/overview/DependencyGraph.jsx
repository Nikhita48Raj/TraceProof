import { GRAPH_EDGES, GRAPH_NODES } from '../../data/sampleData'

const NODE_W = 160
const NODE_H = 56
const SVG_W = 480
const SVG_H = 280

function edgePath(from, to) {
  const fx = from.x + NODE_W
  const fy = from.y + NODE_H / 2
  const tx = to.x
  const ty = to.y + NODE_H / 2
  const midX = (fx + tx) / 2
  return `M ${fx} ${fy} C ${midX} ${fy}, ${midX} ${ty}, ${tx} ${ty}`
}

function edgeLabelPos(from, to) {
  return {
    x: (from.x + NODE_W + to.x) / 2,
    y: (from.y + to.y) / 2 + NODE_H / 2 - 8,
  }
}

export default function DependencyGraph() {
  const nodeMap = Object.fromEntries(GRAPH_NODES.map((n) => [n.id, n]))

  return (
    <section
      className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
      aria-labelledby="lineage-graph-title"
    >
      <div className="mb-4">
        <h2 id="lineage-graph-title" className="text-base font-semibold text-slate-900">
          Sample dependency lineage
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Fictional student data flow across DynamoDB and S3 (demo visualization).
        </p>
      </div>
      <div className="overflow-x-auto rounded-lg border border-slate-100 bg-slate-50/80 p-4">
        <svg
          viewBox={`0 0 ${SVG_W} ${SVG_H}`}
          className="mx-auto h-auto w-full max-w-xl"
          role="img"
          aria-label="Dependency graph: student record connects to report file and derived record"
        >
          <defs>
            <marker
              id="arrow"
              markerWidth="8"
              markerHeight="8"
              refX="7"
              refY="4"
              orient="auto"
            >
              <path d="M0,0 L8,4 L0,8 Z" fill="#64748b" />
            </marker>
          </defs>
          {GRAPH_EDGES.map((edge) => {
            const from = nodeMap[edge.from]
            const to = nodeMap[edge.to]
            const labelPos = edgeLabelPos(from, to)
            return (
              <g key={`${edge.from}-${edge.to}`}>
                <path
                  d={edgePath(from, to)}
                  fill="none"
                  stroke="#94a3b8"
                  strokeWidth="1.5"
                  markerEnd="url(#arrow)"
                />
                <text
                  x={labelPos.x}
                  y={labelPos.y}
                  textAnchor="middle"
                  className="fill-slate-500 text-[10px]"
                >
                  {edge.label}
                </text>
              </g>
            )
          })}
          {GRAPH_NODES.map((node) => (
            <g key={node.id} transform={`translate(${node.x}, ${node.y})`}>
              <rect
                width={NODE_W}
                height={NODE_H}
                rx="8"
                fill="#fff"
                stroke="#cbd5e1"
                strokeWidth="1.5"
              />
              <text x="12" y="22" className="fill-slate-900 text-[11px] font-semibold">
                {node.label}
              </text>
              <text x="12" y="40" className="fill-slate-500 text-[9px]">
                {node.subtitle}
              </text>
            </g>
          ))}
        </svg>
      </div>
    </section>
  )
}
