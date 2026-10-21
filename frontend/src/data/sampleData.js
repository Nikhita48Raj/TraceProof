/** Fictional demo data — not connected to any cloud account. */

export const SAMPLE_RESOURCES = [
  {
    id: 'res-student-001',
    name: 'Student record — Alice Chen',
    type: 'DynamoDB',
    table: 'Students',
    partitionKey: 'STU#00142',
    dependents: [
      {
        id: 'dep-report-001',
        name: 'Report file — alice_chen_q3.pdf',
        type: 'S3',
        bucket: 'district-reports-prod',
        key: 'reports/2026/q3/alice_chen_q3.pdf',
      },
      {
        id: 'dep-derived-001',
        name: 'Derived aggregate — cohort summary row',
        type: 'DynamoDB',
        table: 'CohortSummaries',
        partitionKey: 'COHORT#2026-Q3',
      },
    ],
  },
  {
    id: 'res-report-002',
    name: 'Report file — maria_lopez_q3.pdf',
    type: 'S3',
    bucket: 'district-reports-prod',
    key: 'reports/2026/q3/maria_lopez_q3.pdf',
    dependents: [
      {
        id: 'dep-derived-002',
        name: 'Derived aggregate — cohort summary row',
        type: 'DynamoDB',
        table: 'CohortSummaries',
        partitionKey: 'COHORT#2026-Q3',
      },
    ],
  },
  {
    id: 'res-derived-003',
    name: 'Derived record — cohort summary row',
    type: 'DynamoDB',
    table: 'CohortSummaries',
    partitionKey: 'COHORT#2026-Q3',
    dependents: [],
  },
]

export const INITIAL_DELETION_REQUESTS = [
  {
    id: 'DR-2026-0041',
    resourceId: 'res-student-001',
    resourceLabel: 'Student record — Alice Chen (DynamoDB)',
    status: 'Verified',
    targetsChecked: 3,
    timestamp: '2026-10-18T14:22:00Z',
  },
  {
    id: 'DR-2026-0040',
    resourceId: 'res-report-002',
    resourceLabel: 'Report file — maria_lopez_q3.pdf (S3)',
    status: 'Incomplete',
    targetsChecked: 2,
    timestamp: '2026-10-17T09:05:00Z',
  },
  {
    id: 'DR-2026-0039',
    resourceId: 'res-derived-003',
    resourceLabel: 'Derived record — cohort summary (DynamoDB)',
    status: 'Pending',
    targetsChecked: 0,
    timestamp: '2026-10-16T16:40:00Z',
  },
  {
    id: 'DR-2026-0038',
    resourceId: 'res-student-001',
    resourceLabel: 'Student record — Alice Chen (DynamoDB)',
    status: 'Verified',
    targetsChecked: 3,
    timestamp: '2026-10-15T11:18:00Z',
  },
]

export const GRAPH_NODES = [
  {
    id: 'node-student',
    label: 'Student record',
    subtitle: 'DynamoDB · Students',
    x: 80,
    y: 120,
  },
  {
    id: 'node-report',
    label: 'Report file',
    subtitle: 'S3 · district-reports-prod',
    x: 320,
    y: 60,
  },
  {
    id: 'node-derived',
    label: 'Derived record',
    subtitle: 'DynamoDB · CohortSummaries',
    x: 320,
    y: 200,
  },
]

export const GRAPH_EDGES = [
  { from: 'node-student', to: 'node-report', label: 'generates' },
  { from: 'node-student', to: 'node-derived', label: 'feeds aggregate' },
  { from: 'node-report', to: 'node-derived', label: 'referenced by' },
]

export const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: 'LayoutDashboard' },
  { id: 'lineage', label: 'Resource Lineage', icon: 'GitBranch' },
  { id: 'requests', label: 'Deletion Requests', icon: 'Trash2' },
  { id: 'reports', label: 'Verification Reports', icon: 'FileCheck' },
  { id: 'experiments', label: 'Experiments', icon: 'FlaskConical' },
  { id: 'settings', label: 'Settings', icon: 'Settings' },
]

export const PAGE_TITLES = {
  overview: 'Overview',
  lineage: 'Resource Lineage',
  requests: 'Deletion Requests',
  reports: 'Verification Reports',
  experiments: 'Experiments',
  settings: 'Settings',
}

export const TOTAL_REGISTERED_RESOURCES = 47
