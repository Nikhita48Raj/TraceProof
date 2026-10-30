import { useState } from 'react'
import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  Check,
  CheckCircle2,
  Clock,
  Copy,
  Download,
  FileSpreadsheet,
  FileText,
  FlaskConical,
  HelpCircle,
  History,
  RotateCcw,
  Sparkles,
} from 'lucide-react'
import DemoDataBanner from '../components/ui/DemoDataBanner'
import { experimentExportUrl, runExperiment } from '../api/traceproof'

const INITIAL_CONFIG = {
  num_resources: 12,
  dependency_density: 0.15,
  failure_rate: 0.2,
  trials: 5,
  random_seed: 42,
  dependency_depth: 4,
}

const PRESETS = [
  {
    name: 'Standard Benchmark',
    config: { num_resources: 12, dependency_density: 0.15, failure_rate: 0.2, trials: 5, random_seed: 42, dependency_depth: 4 },
  },
  {
    name: 'Deep Dependency Chain',
    config: { num_resources: 16, dependency_density: 0.3, failure_rate: 0.25, trials: 5, random_seed: 101, dependency_depth: 8 },
  },
  {
    name: 'High Failure Stress',
    config: { num_resources: 20, dependency_density: 0.2, failure_rate: 0.45, trials: 10, random_seed: 777, dependency_depth: 5 },
  },
]

function formatRate(value) {
  if (value === null || value === undefined) return 'N/A'
  return `${(value * 100).toFixed(1)}%`
}

function formatCi(interval) {
  if (!interval || interval.length !== 2) return null
  return `[${(interval[0] * 100).toFixed(1)}%, ${(interval[1] * 100).toFixed(1)}%]`
}

export default function ExperimentsPage() {
  const [config, setConfig] = useState(INITIAL_CONFIG)
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])
  const [lastConfig, setLastConfig] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [copiedReport, setCopiedReport] = useState(false)

  const update = (key, value) => setConfig((current) => ({ ...current, [key]: value }))

  const execute = async (nextConfig) => {
    setLoading(true)
    setError('')
    try {
      const data = await runExperiment(nextConfig)
      setResult(data)
      setLastConfig({ ...nextConfig })
      setHistory((prev) => [
        {
          id: data.experiment_id,
          timestamp: new Date().toLocaleTimeString(),
          config: { ...nextConfig },
          result: data,
        },
        ...prev.slice(0, 9),
      ])
    } catch (err) {
      setError(err.message || 'The experiment could not be completed.')
    } finally {
      setLoading(false)
    }
  }

  const submit = (event) => {
    event.preventDefault()
    execute(config)
  }

  const baseline = result?.baseline
  const traceproof = result?.traceproof

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">
            Reproducible Research Experiment Engine
          </h1>
          <p className="mt-0.5 text-xs text-slate-500">
            Deterministic synthetic benchmark comparing root-only deletion against dependency-closure verification across controlled failure scenarios.
          </p>
        </div>
      </div>

      <DemoDataBanner />

      {/* Configuration Form */}
      <form onSubmit={submit} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between border-b border-slate-100 pb-3">
          <div>
            <h2 className="text-sm font-semibold text-slate-900">
              Experiment Parameters & Monte Carlo Configuration
            </h2>
            <p className="text-xs text-slate-500">
              Controlled synthetic graph generation and seeded failure injection.
            </p>
          </div>

          {/* Quick Presets */}
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] font-medium text-slate-400">Presets:</span>
            {PRESETS.map((p) => (
              <button
                key={p.name}
                type="button"
                disabled={loading}
                onClick={() => setConfig(p.config)}
                className="rounded border border-slate-200 bg-slate-50 px-2 py-1 text-[11px] font-medium text-slate-700 hover:bg-slate-100"
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-4 grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6">
          <label className="text-xs font-medium text-slate-700">
            Resources Count
            <input
              className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-1.5 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-navy-900"
              type="number"
              min="4"
              max="100"
              value={config.num_resources}
              disabled={loading}
              onChange={(e) => update('num_resources', Number(e.target.value))}
            />
          </label>

          <label className="text-xs font-medium text-slate-700">
            Dependency Density
            <input
              className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-1.5 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-navy-900"
              type="number"
              min="0"
              max="1"
              step="0.01"
              value={config.dependency_density}
              disabled={loading}
              onChange={(e) => update('dependency_density', Number(e.target.value))}
            />
          </label>

          <label className="text-xs font-medium text-slate-700">
            Failure Probability
            <input
              className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-1.5 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-navy-900"
              type="number"
              min="0"
              max="1"
              step="0.01"
              value={config.failure_rate}
              disabled={loading}
              onChange={(e) => update('failure_rate', Number(e.target.value))}
            />
          </label>

          <label className="text-xs font-medium text-slate-700">
            Trials Per Scenario
            <input
              className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-1.5 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-navy-900"
              type="number"
              min="1"
              max="100"
              value={config.trials}
              disabled={loading}
              onChange={(e) => update('trials', Number(e.target.value))}
            />
          </label>

          <label className="text-xs font-medium text-slate-700">
            Random Seed
            <input
              className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-1.5 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-navy-900"
              type="number"
              min="0"
              max="2147483647"
              value={config.random_seed}
              disabled={loading}
              onChange={(e) => update('random_seed', Number(e.target.value))}
            />
          </label>

          <label className="text-xs font-medium text-slate-700">
            Dependency Depth
            <input
              className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-1.5 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-navy-900"
              type="number"
              min="1"
              max={config.num_resources - 1}
              value={config.dependency_depth}
              disabled={loading}
              onChange={(e) => update('dependency_depth', Number(e.target.value))}
            />
          </label>
        </div>

        <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-3">
          <div className="flex flex-wrap items-center gap-3">
            <button
              className="rounded-lg bg-navy-900 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-navy-800 disabled:opacity-60"
              disabled={loading}
              type="submit"
            >
              {loading ? 'Running Synthetic Trials…' : 'Execute Benchmark'}
            </button>
            {lastConfig && (
              <button
                className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-60"
                disabled={loading}
                type="button"
                onClick={() => execute(lastConfig)}
              >
                <RotateCcw className="h-3.5 w-3.5" />
                Rerun Exact Seed ({lastConfig.random_seed})
              </button>
            )}
          </div>

          {/* History selector if available */}
          {history.length > 1 && (
            <div className="flex items-center gap-2 text-xs">
              <History className="h-3.5 w-3.5 text-slate-400" />
              <span className="text-slate-500">History:</span>
              <select
                onChange={(e) => {
                  const entry = history.find((h) => h.id === e.target.value)
                  if (entry) {
                    setResult(entry.result)
                    setConfig(entry.config)
                  }
                }}
                className="rounded border border-slate-200 py-1 pl-2 pr-6 text-xs text-slate-700"
              >
                {history.map((h, i) => (
                  <option key={h.id} value={h.id}>
                    Run #{history.length - i} ({h.timestamp} · seed {h.config.random_seed})
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </form>

      {error && (
        <div role="alert" className="rounded-lg border border-red-300 bg-red-50 p-3 text-xs text-red-800">
          <strong>Experiment error:</strong> {error}
        </div>
      )}

      {loading && (
        <div className="rounded-xl border border-blue-200 bg-blue-50/50 p-6 text-center text-xs text-blue-900 shadow-sm">
          <FlaskConical className="mx-auto h-6 w-6 animate-pulse text-blue-700" />
          <p className="mt-2 font-semibold">Running Paired Benchmark Simulations...</p>
          <p className="mt-0.5 text-blue-700">
            Generating synthetic DAG closures, injecting failures across 9 experimental scenarios, and evaluating confusion matrices.
          </p>
        </div>
      )}

      {!result && !loading && !error && (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-12 text-center text-xs text-slate-500 shadow-sm">
          <FlaskConical className="mx-auto h-8 w-8 text-slate-400" />
          <h3 className="mt-3 text-sm font-semibold text-slate-900">No Experiment Results Loaded</h3>
          <p className="mt-1 text-slate-500">
            Configure the parameters above and click <strong>Execute Benchmark</strong> to generate measured comparative data.
          </p>
        </div>
      )}

      {/* Measured Results Section */}
      {result && baseline && traceproof && (
        <div className="space-y-6">
          {/* Aggregate Comparison Section */}
          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between border-b border-slate-100 pb-3">
              <div>
                <span className="rounded bg-navy-900/10 px-2 py-0.5 text-[10px] font-semibold text-navy-900 uppercase tracking-wider">
                  Measured Research Summary
                </span>
                <h2 className="mt-1 text-base font-bold text-slate-900">
                  Aggregate Comparative Performance
                </h2>
                <p className="mt-0.5 text-xs text-slate-600">{result.interpretation}</p>
              </div>

              {/* Export Links */}
              <div className="flex flex-wrap items-center gap-2">
                <a
                  href={experimentExportUrl(result.experiment_id, 'trials.csv')}
                  className="inline-flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-700 shadow-xs hover:bg-slate-50"
                  title="Download Raw Trial Level CSV"
                >
                  <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-600" />
                  trials.csv
                </a>
                <a
                  href={experimentExportUrl(result.experiment_id, 'aggregates.csv')}
                  className="inline-flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-700 shadow-xs hover:bg-slate-50"
                  title="Download Summary Metrics CSV"
                >
                  <FileSpreadsheet className="h-3.5 w-3.5 text-blue-600" />
                  aggregates.csv
                </a>
                <a
                  href={experimentExportUrl(result.experiment_id, 'report.md')}
                  className="inline-flex items-center gap-1 rounded-lg bg-navy-900 px-2.5 py-1.5 text-xs font-medium text-white shadow-xs hover:bg-navy-800"
                  title="Download Research Report Markdown"
                >
                  <FileText className="h-3.5 w-3.5" />
                  report.md
                </a>
              </div>
            </div>

            {/* Comprehensive Metrics Table */}
            <div className="mt-4 overflow-x-auto">
              <table className="min-w-full text-xs">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50 text-[11px] font-semibold uppercase tracking-wider text-slate-600">
                    <th className="px-4 py-2.5 text-left">Evaluation Metric</th>
                    <th className="px-4 py-2.5 text-left">Baseline (Root Only)</th>
                    <th className="px-4 py-2.5 text-left">TraceProof (Dependency-Aware)</th>
                    <th className="px-4 py-2.5 text-left">Research Interpretation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {/* Detection Rate (Recall) */}
                  <tr className="hover:bg-slate-50/50">
                    <th scope="row" className="px-4 py-2.5 text-left font-semibold text-slate-800">
                      Detection Rate (Recall)
                    </th>
                    <td className="px-4 py-2.5 tabular-nums font-semibold text-slate-700">
                      {formatRate(baseline.detection_rate)}{' '}
                      <span className="text-[10px] text-slate-400 font-normal">
                        {formatCi(baseline.detection_rate_wilson_95_ci)}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 tabular-nums font-bold text-emerald-700">
                      {formatRate(traceproof.detection_rate)}{' '}
                      <span className="text-[10px] text-emerald-600/70 font-normal">
                        {formatCi(traceproof.detection_rate_wilson_95_ci)}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-slate-500">
                      Proportion of incomplete deletion scenarios correctly flagged (TP / [TP + FN]).
                    </td>
                  </tr>

                  {/* False Negative Rate */}
                  <tr className="hover:bg-slate-50/50">
                    <th scope="row" className="px-4 py-2.5 text-left font-semibold text-slate-800">
                      False Negative Rate (Miss Rate)
                    </th>
                    <td className="px-4 py-2.5 tabular-nums font-semibold text-red-600">
                      {formatRate(baseline.false_negative_rate)}
                    </td>
                    <td className="px-4 py-2.5 tabular-nums font-bold text-emerald-700">
                      {formatRate(traceproof.false_negative_rate)}
                    </td>
                    <td className="px-4 py-2.5 text-slate-500">
                      Missed incomplete deletions where unaddressed copies remained (FN / [TP + FN]).
                    </td>
                  </tr>

                  {/* Precision */}
                  <tr className="hover:bg-slate-50/50">
                    <th scope="row" className="px-4 py-2.5 text-left font-semibold text-slate-800">
                      Precision
                    </th>
                    <td className="px-4 py-2.5 tabular-nums text-slate-700">
                      {formatRate(baseline.precision)}
                    </td>
                    <td className="px-4 py-2.5 tabular-nums font-bold text-emerald-700">
                      {formatRate(traceproof.precision)}
                    </td>
                    <td className="px-4 py-2.5 text-slate-500">
                      Accuracy of incomplete deletion alarms (TP / [TP + FP]).
                    </td>
                  </tr>

                  {/* F1 Score */}
                  <tr className="hover:bg-slate-50/50">
                    <th scope="row" className="px-4 py-2.5 text-left font-semibold text-slate-800">
                      F1 Score
                    </th>
                    <td className="px-4 py-2.5 tabular-nums text-slate-700">
                      {formatRate(baseline.f1_score)}
                    </td>
                    <td className="px-4 py-2.5 tabular-nums font-bold text-emerald-700">
                      {formatRate(traceproof.f1_score)}
                    </td>
                    <td className="px-4 py-2.5 text-slate-500">
                      Harmonic mean of precision and recall.
                    </td>
                  </tr>

                  {/* False Positive Rate */}
                  <tr className="hover:bg-slate-50/50">
                    <th scope="row" className="px-4 py-2.5 text-left font-semibold text-slate-800">
                      False Positive Rate
                    </th>
                    <td className="px-4 py-2.5 tabular-nums text-slate-700">
                      {formatRate(baseline.false_positive_rate)}
                    </td>
                    <td className="px-4 py-2.5 tabular-nums font-semibold text-slate-700">
                      {formatRate(traceproof.false_positive_rate)}
                    </td>
                    <td className="px-4 py-2.5 text-slate-500">
                      Rate of false alarms on successfully cleaned closures (FP / [TN + FP]).
                    </td>
                  </tr>

                  {/* Dependency Coverage */}
                  <tr className="hover:bg-slate-50/50">
                    <th scope="row" className="px-4 py-2.5 text-left font-semibold text-slate-800">
                      Dependency Coverage
                    </th>
                    <td className="px-4 py-2.5 tabular-nums font-semibold text-slate-600">
                      {formatRate(baseline.dependency_coverage)}
                    </td>
                    <td className="px-4 py-2.5 tabular-nums font-bold text-blue-700">
                      {formatRate(traceproof.dependency_coverage)}
                    </td>
                    <td className="px-4 py-2.5 text-slate-500">
                      Mean share of registered dependency targets verified.
                    </td>
                  </tr>

                  {/* Confusion Matrix Counts */}
                  <tr className="hover:bg-slate-50/50">
                    <th scope="row" className="px-4 py-2.5 text-left font-semibold text-slate-800">
                      Confusion Matrix (TP / TN / FP / FN)
                    </th>
                    <td className="px-4 py-2.5 tabular-nums text-slate-700 font-mono">
                      {baseline.true_positive_count} / {baseline.true_negative_count} / {baseline.false_positive_count} / <strong className="text-red-600">{baseline.false_negative_count}</strong>
                    </td>
                    <td className="px-4 py-2.5 tabular-nums font-mono text-emerald-700">
                      {traceproof.true_positive_count} / {traceproof.true_negative_count} / {traceproof.false_positive_count} / <strong>{traceproof.false_negative_count}</strong>
                    </td>
                    <td className="px-4 py-2.5 text-slate-500">
                      Baseline exhibits severe false negatives on dependent failures.
                    </td>
                  </tr>

                  {/* Processing Time */}
                  <tr className="hover:bg-slate-50/50">
                    <th scope="row" className="px-4 py-2.5 text-left font-semibold text-slate-800">
                      Execution Time (Mean / Total ms)
                    </th>
                    <td className="px-4 py-2.5 tabular-nums text-slate-700">
                      {baseline.mean_execution_time_ms?.toFixed(4)} ms / {baseline.total_processing_time_ms?.toFixed(2)} ms
                    </td>
                    <td className="px-4 py-2.5 tabular-nums text-slate-700">
                      {traceproof.mean_execution_time_ms?.toFixed(4)} ms / {traceproof.total_processing_time_ms?.toFixed(2)} ms
                    </td>
                    <td className="px-4 py-2.5 text-slate-500">
                      Local simulation cpu timing via <code>perf_counter_ns</code>.
                    </td>
                  </tr>

                  {/* Targets & Attempts */}
                  <tr className="hover:bg-slate-50/50">
                    <th scope="row" className="px-4 py-2.5 text-left font-semibold text-slate-800">
                      Total Targets Checked / Attempts
                    </th>
                    <td className="px-4 py-2.5 tabular-nums text-slate-700">
                      {baseline.dependency_targets_checked} / {baseline.deletion_attempts}
                    </td>
                    <td className="px-4 py-2.5 tabular-nums font-semibold text-slate-800">
                      {traceproof.dependency_targets_checked} / {traceproof.deletion_attempts}
                    </td>
                    <td className="px-4 py-2.5 text-slate-500">
                      Total simulated operations performed across all {baseline.total_trials} trials.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          {/* Statistical Significance & Paired Analysis */}
          {result.paired_comparison && (
            <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
                <BarChart3 className="h-4 w-4 text-blue-700" />
                <h3 className="text-sm font-semibold text-slate-900">
                  Statistical Hypothesis Testing & Paired Discordance Analysis
                </h3>
              </div>
              <div className="mt-3 grid gap-4 sm:grid-cols-2 md:grid-cols-4 text-xs">
                <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <span className="text-slate-500">Paired Trials:</span>
                  <p className="mt-1 text-lg font-bold text-slate-900">
                    {result.paired_comparison.paired_trials}
                  </p>
                  <p className="text-[10px] text-slate-400">Identical starting graphs</p>
                </div>

                <div className="rounded-lg border border-blue-200 bg-blue-50/50 p-3">
                  <span className="text-blue-900 font-medium">TraceProof Correctness Wins:</span>
                  <p className="mt-1 text-lg font-bold text-blue-700">
                    {result.paired_comparison.correctness_discordances_traceproof_better}
                  </p>
                  <p className="text-[10px] text-blue-600">TraceProof correct, Baseline missed</p>
                </div>

                <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <span className="text-slate-600 font-medium">Baseline Correctness Wins:</span>
                  <p className="mt-1 text-lg font-bold text-slate-800">
                    {result.paired_comparison.correctness_discordances_baseline_better}
                  </p>
                  <p className="text-[10px] text-slate-400">Baseline correct, TraceProof missed</p>
                </div>

                <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <span className="text-slate-600 font-medium">Exact McNemar Two-Sided p-value:</span>
                  <p className="mt-1 text-lg font-bold text-slate-900">
                    {result.paired_comparison.exact_mcnemar_two_sided_p_value === null
                      ? 'N/A'
                      : result.paired_comparison.exact_mcnemar_two_sided_p_value < 0.0001
                      ? '< 0.0001'
                      : result.paired_comparison.exact_mcnemar_two_sided_p_value.toFixed(4)}
                  </p>
                  <p className="text-[10px] text-slate-500">
                    {result.paired_comparison.exact_mcnemar_two_sided_p_value < 0.05
                      ? 'Statistically significant (p < 0.05)'
                      : 'No statistically significant difference'}
                  </p>
                </div>
              </div>

              <p className="mt-3 text-[11px] text-slate-500">
                <strong>Methodological Note:</strong> {result.paired_comparison.test_note}
              </p>
            </section>
          )}

          {/* Scenario-Level Breakdown Table */}
          <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 p-4">
              <h3 className="text-sm font-semibold text-slate-900">
                Detailed Scenario Breakdown ({result.scenarios.length} Scenarios)
              </h3>
              <p className="text-xs text-slate-500">
                Independent evaluation across varying graph topologies and failure injection locations.
              </p>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full text-xs">
                <thead>
                  <tr className="border-b border-slate-100 bg-slate-50 text-[11px] uppercase tracking-wider text-slate-600">
                    <th className="px-4 py-2.5 text-left">Scenario</th>
                    <th className="px-4 py-2.5 text-center">Trials</th>
                    <th className="px-4 py-2.5 text-center">Baseline TP / FN</th>
                    <th className="px-4 py-2.5 text-center">TraceProof TP / FN</th>
                    <th className="px-4 py-2.5 text-center">Baseline Recall</th>
                    <th className="px-4 py-2.5 text-center">TraceProof Recall</th>
                    <th className="px-4 py-2.5 text-center">Coverage</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {result.scenarios.map((sc) => {
                    const baseTp = sc.baseline.true_positive_count
                    const baseFn = sc.baseline.false_negative_count
                    const tpTp = sc.traceproof.true_positive_count
                    const tpFn = sc.traceproof.false_negative_count
                    const baseRate = formatRate(sc.baseline.detection_rate)
                    const tpRate = formatRate(sc.traceproof.detection_rate)

                    return (
                      <tr key={sc.scenario} className="hover:bg-slate-50/50">
                        <td className="px-4 py-2.5 font-medium text-slate-800 capitalize">
                          {sc.scenario.replaceAll('_', ' ')}
                        </td>
                        <td className="px-4 py-2.5 text-center tabular-nums text-slate-600">
                          {sc.baseline.total_trials}
                        </td>
                        <td className="px-4 py-2.5 text-center tabular-nums font-mono">
                          {baseTp} / <span className={baseFn > 0 ? 'text-red-600 font-bold' : ''}>{baseFn}</span>
                        </td>
                        <td className="px-4 py-2.5 text-center tabular-nums font-mono text-emerald-700 font-semibold">
                          {tpTp} / {tpFn}
                        </td>
                        <td className="px-4 py-2.5 text-center tabular-nums text-slate-600">
                          {baseRate}
                        </td>
                        <td className="px-4 py-2.5 text-center tabular-nums font-bold text-emerald-700">
                          {tpRate}
                        </td>
                        <td className="px-4 py-2.5 text-center tabular-nums font-semibold text-blue-700">
                          {formatRate(sc.traceproof.dependency_coverage)}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </section>

          {/* Scenario Detection Rate Visualization */}
          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-900">
              Comparative Detection Rate by Scenario
            </h3>
            <p className="text-xs text-slate-500">
              Visualizing recall across failure scenarios: Gray = Baseline (Root-Only) · Blue = TraceProof (Closure-Aware)
            </p>

            <div className="mt-4 space-y-4">
              {result.scenarios.map((sc) => {
                const bRate = sc.baseline.detection_rate ?? 0
                const tRate = sc.traceproof.detection_rate ?? 0

                return (
                  <div key={sc.scenario} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-medium text-slate-800 capitalize">
                        {sc.scenario.replaceAll('_', ' ')}
                      </span>
                      <span className="text-[11px] text-slate-500">
                        Baseline: <strong>{formatRate(sc.baseline.detection_rate)}</strong> · TraceProof: <strong className="text-blue-700">{formatRate(sc.traceproof.detection_rate)}</strong>
                      </span>
                    </div>
                    <div className="space-y-1">
                      {/* Baseline bar */}
                      <div className="h-2 w-full rounded bg-slate-100 overflow-hidden">
                        <div
                          className="h-full bg-slate-400 transition-all"
                          style={{ width: `${bRate * 100}%` }}
                        />
                      </div>
                      {/* TraceProof bar */}
                      <div className="h-2 w-full rounded bg-slate-100 overflow-hidden">
                        <div
                          className="h-full bg-blue-600 transition-all"
                          style={{ width: `${tRate * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </section>
        </div>
      )}
    </div>
  )
}
