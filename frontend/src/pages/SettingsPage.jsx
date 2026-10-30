import { useEffect, useState } from 'react'
import {
  Activity,
  CheckCircle2,
  Cloud,
  Database,
  ExternalLink,
  HardDrive,
  Info,
  Layers,
  Server,
  Shield,
  Zap,
} from 'lucide-react'
import DemoDataBanner from '../components/ui/DemoDataBanner'
import { getApiBaseUrl, getHealthCheck } from '../api/traceproof'

export default function SettingsPage() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const apiBaseUrl = getApiBaseUrl()
  const isAwsMode = apiBaseUrl.includes('amazonaws.com') || apiBaseUrl.includes('execute-api')

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError('')

    getHealthCheck()
      .then((data) => {
        if (!cancelled) setHealth(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || 'Unable to reach backend API.')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-xl font-bold tracking-tight text-slate-900">
          Platform Configuration & System Architecture
        </h1>
        <p className="mt-0.5 text-xs text-slate-500">
          Environment configuration, live health diagnostics, and AWS serverless architecture overview.
        </p>
      </div>

      <DemoDataBanner />

      {/* Execution Environment Card */}
      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2.5">
            <div className={`rounded-lg p-2 ${isAwsMode ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'}`}>
              {isAwsMode ? <Cloud className="h-5 w-5" /> : <Server className="h-5 w-5" />}
            </div>
            <div>
              <h2 className="text-sm font-semibold text-slate-900">
                Active Execution Mode: {isAwsMode ? 'AWS Cloud Serverless' : 'Local FastAPI Simulation'}
              </h2>
              <p className="text-xs text-slate-500">
                Configured via <code>VITE_API_BASE_URL</code>
              </p>
            </div>
          </div>
          <span
            className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
              isAwsMode
                ? 'bg-purple-50 text-purple-700 border border-purple-200'
                : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
            }`}
          >
            {isAwsMode ? 'AWS MODE' : 'LOCAL MODE'}
          </span>
        </div>

        <dl className="mt-4 grid gap-3 sm:grid-cols-2 text-xs">
          <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
            <dt className="text-slate-500">API Gateway Base URL:</dt>
            <dd className="mt-1 font-mono font-medium text-slate-900 break-all">
              {apiBaseUrl}
            </dd>
          </div>

          <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
            <dt className="text-slate-500">Backend API Health Status:</dt>
            <dd className="mt-1 flex items-center gap-2">
              {loading ? (
                <span className="text-slate-400">Pinging backend...</span>
              ) : error ? (
                <span className="font-semibold text-red-600">Disconnected ({error})</span>
              ) : (
                <span className="inline-flex items-center gap-1 font-semibold text-emerald-700">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  {health?.status === 'running' || health?.status === 'healthy' ? 'Operational' : health?.status}
                  {health?.mode && ` (${health.mode})`}
                </span>
              )}
            </dd>
          </div>
        </dl>

        <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50/60 p-3 text-xs text-slate-600">
          <p className="font-semibold text-slate-800">To Switch Between Modes:</p>
          <ul className="mt-1.5 list-disc pl-4 space-y-1 text-slate-600">
            <li>
              <strong>Local Mode:</strong> Set <code>VITE_API_BASE_URL=http://localhost:8000</code> in <code>frontend/.env.local</code>. Runs with the FastAPI backend without requiring AWS credentials.
            </li>
            <li>
              <strong>AWS Mode:</strong> Set <code>VITE_API_BASE_URL=https://&lt;api-id&gt;.execute-api.&lt;region&gt;.amazonaws.com</code> after running <code>sam deploy</code>. Connects to API Gateway, Lambda, DynamoDB, SQS, and S3.
            </li>
          </ul>
        </div>
      </section>

      {/* Five AWS Services Architecture Breakdown */}
      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-sm font-semibold text-slate-900 border-b border-slate-100 pb-3">
          AWS Five-Service Cloud Architecture
        </h2>

        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          {/* Service 1 */}
          <div className="rounded-lg border border-slate-200 p-3.5 text-xs">
            <div className="flex items-center gap-2 font-semibold text-slate-900">
              <Zap className="h-4 w-4 text-amber-500" />
              1. Amazon API Gateway (HTTP API)
            </div>
            <p className="mt-1 text-slate-600">
              Low-latency serverless routing, CORS policy enforcement for the Vite frontend origin, and request proxying to ApiFunction.
            </p>
          </div>

          {/* Service 2 */}
          <div className="rounded-lg border border-slate-200 p-3.5 text-xs">
            <div className="flex items-center gap-2 font-semibold text-slate-900">
              <Server className="h-4 w-4 text-orange-500" />
              2. AWS Lambda Functions
            </div>
            <p className="mt-1 text-slate-600">
              <strong>ApiFunction:</strong> Synchronous request handling, input validation, DynamoDB reads/writes, SQS enqueueing.<br />
              <strong>WorkerFunction:</strong> Asynchronous SQS consumer, dependency verification simulation, S3 report storage.
            </p>
          </div>

          {/* Service 3 */}
          <div className="rounded-lg border border-slate-200 p-3.5 text-xs">
            <div className="flex items-center gap-2 font-semibold text-slate-900">
              <Database className="h-4 w-4 text-blue-600" />
              3. Amazon DynamoDB Tables
            </div>
            <p className="mt-1 text-slate-600">
              Three on-demand tables: <code>ResourceTable</code> (synthetic resources), <code>RequestTable</code> (deletion request lifecycles), and <code>ExperimentTable</code> (7-day TTL experiment summaries).
            </p>
          </div>

          {/* Service 4 */}
          <div className="rounded-lg border border-slate-200 p-3.5 text-xs">
            <div className="flex items-center gap-2 font-semibold text-slate-900">
              <Layers className="h-4 w-4 text-purple-600" />
              4. Amazon SQS Queues & DLQ
            </div>
            <p className="mt-1 text-slate-600">
              <code>DeletionQueue:</code> Decouples submission from asynchronous verification.<br />
              <code>DeletionDeadLetterQueue:</code> Retains jobs exceeding retry count for investigation.
            </p>
          </div>

          {/* Service 5 */}
          <div className="rounded-lg border border-slate-200 p-3.5 text-xs sm:col-span-2">
            <div className="flex items-center gap-2 font-semibold text-slate-900">
              <HardDrive className="h-4 w-4 text-emerald-600" />
              5. Amazon S3 (Encrypted Private Report Bucket)
            </div>
            <p className="mt-1 text-slate-600">
              Private AES-256 encrypted bucket storing deletion reports (<code>reports/&lt;request_id&gt;.json</code>) and full trial datasets (<code>experiments/&lt;experiment_id&gt;/trial_records.json</code>) with 90-day automatic lifecycle expiration. Served via short-lived presigned URLs.
            </p>
          </div>
        </div>
      </section>

      {/* Safety & Compliance Policy */}
      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm text-xs text-slate-600">
        <h3 className="font-semibold text-slate-900">Research Prototype Safety Invariants</h3>
        <p className="mt-1 text-slate-500">
          TraceProof operates strictly within synthetic research boundaries. The application never invokes cloud data deletion primitives (such as DynamoDB <code>DeleteItem</code> or S3 <code>DeleteObject</code>). All deletion tracking is evaluated against registered simulated data models.
        </p>
      </section>
    </div>
  )
}
