import { useState } from 'react'
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

function rate(value) {
  return value == null ? 'N/A' : `${(value * 100).toFixed(1)}%`
}

function MetricRow({ label, baseline, traceproof }) {
  return (
    <tr className="border-t border-slate-100">
      <th scope="row" className="px-4 py-3 text-left font-medium text-slate-700">{label}</th>
      <td className="px-4 py-3 tabular-nums text-slate-700">{baseline}</td>
      <td className="px-4 py-3 tabular-nums text-slate-700">{traceproof}</td>
    </tr>
  )
}

export default function ExperimentsPage() {
  const [config, setConfig] = useState(INITIAL_CONFIG)
  const [result, setResult] = useState(null)
  const [lastConfig, setLastConfig] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const update = (key, value) => setConfig((current) => ({ ...current, [key]: value }))

  const execute = async (nextConfig) => {
    setLoading(true)
    setError('')
    try {
      const data = await runExperiment(nextConfig)
      setResult(data)
      setLastConfig({ ...nextConfig })
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
    <div className="mx-auto max-w-6xl space-y-6">
      <DemoDataBanner />
      <header>
        <h1 className="text-xl font-semibold text-slate-900">Research experiment runner</h1>
        <p className="mt-1 max-w-3xl text-sm text-slate-600">
          Compare root-only checks with dependency-closure verification using deterministic synthetic graphs. No real data or cloud resources are touched.
        </p>
      </header>

      <form onSubmit={submit} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-base font-semibold text-slate-900">Experiment configuration</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <label className="text-sm text-slate-700">Resources
            <input className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2" type="number" min="4" max="100" value={config.num_resources} disabled={loading} onChange={(e) => update('num_resources', Number(e.target.value))} />
          </label>
          <label className="text-sm text-slate-700">Dependency density
            <input className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2" type="number" min="0" max="1" step="0.01" value={config.dependency_density} disabled={loading} onChange={(e) => update('dependency_density', Number(e.target.value))} />
          </label>
          <label className="text-sm text-slate-700">Failure rate (randomized scenario)
            <input className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2" type="number" min="0" max="1" step="0.01" value={config.failure_rate} disabled={loading} onChange={(e) => update('failure_rate', Number(e.target.value))} />
          </label>
          <label className="text-sm text-slate-700">Trials per scenario
            <input className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2" type="number" min="1" max="100" value={config.trials} disabled={loading} onChange={(e) => update('trials', Number(e.target.value))} />
          </label>
          <label className="text-sm text-slate-700">Random seed
            <input className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2" type="number" min="0" max="2147483647" value={config.random_seed} disabled={loading} onChange={(e) => update('random_seed', Number(e.target.value))} />
          </label>
          <label className="text-sm text-slate-700">Dependency depth
            <input className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2" type="number" min="1" max={config.num_resources - 1} value={config.dependency_depth} disabled={loading} onChange={(e) => update('dependency_depth', Number(e.target.value))} />
          </label>
        </div>
        <div className="mt-5 flex flex-wrap gap-3">
          <button className="rounded-lg bg-navy-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-60" disabled={loading} type="submit">
            {loading ? 'Running experiment…' : 'Run experiment'}
          </button>
          {lastConfig && <button className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 disabled:opacity-60" disabled={loading} type="button" onClick={() => execute(lastConfig)}>Rerun same configuration and seed</button>}
        </div>
      </form>

      {error && <div role="alert" className="rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-800">Experiment error: {error}</div>}
      {loading && <p role="status" className="text-sm text-slate-600">Generating synthetic cases and measuring both methods…</p>}
      {!result && !loading && !error && <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-600">Set the parameters and run an experiment to see measured results.</div>}

      {result && <>
        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h2 className="text-base font-semibold text-slate-900">Aggregate comparison</h2>
              <p className="mt-1 text-sm text-slate-600">{result.interpretation}</p>
            </div>
            <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-800">Controlled simulation only</span>
          </div>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead><tr className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500"><th className="px-4 py-3 text-left">Metric</th><th className="px-4 py-3 text-left">Baseline</th><th className="px-4 py-3 text-left">TraceProof</th></tr></thead>
              <tbody>
                <MetricRow label="Detection rate" baseline={rate(baseline.detection_rate)} traceproof={rate(traceproof.detection_rate)} />
                <MetricRow label="False-negative rate" baseline={rate(baseline.false_negative_rate)} traceproof={rate(traceproof.false_negative_rate)} />
                <MetricRow label="Incomplete cases detected" baseline={`${baseline.incomplete_deletion_scenarios_detected} / ${baseline.true_positive_count + baseline.false_negative_count}`} traceproof={`${traceproof.incomplete_deletion_scenarios_detected} / ${traceproof.true_positive_count + traceproof.false_negative_count}`} />
                <MetricRow label="False positives" baseline={baseline.false_positive_count} traceproof={traceproof.false_positive_count} />
                <MetricRow label="Deletion attempts" baseline={baseline.deletion_attempts} traceproof={traceproof.deletion_attempts} />
                <MetricRow label="False-positive rate" baseline={rate(baseline.false_positive_rate)} traceproof={rate(traceproof.false_positive_rate)} />
                <MetricRow label="Mean / median time (ms)" baseline={`${baseline.mean_execution_time_ms.toFixed(4)} / ${baseline.median_execution_time_ms.toFixed(4)}`} traceproof={`${traceproof.mean_execution_time_ms.toFixed(4)} / ${traceproof.median_execution_time_ms.toFixed(4)}`} />
                <MetricRow label="Timing standard deviation (ms)" baseline={baseline.stddev_execution_time_ms.toFixed(4)} traceproof={traceproof.stddev_execution_time_ms.toFixed(4)} />
                <MetricRow label="Remaining resources in full closure" baseline={baseline.resources_remaining_in_dependency_closure} traceproof={traceproof.resources_remaining_in_dependency_closure} />
              </tbody>
            </table>
          </div>
          <details className="mt-4 text-sm text-slate-600"><summary className="cursor-pointer font-medium">Configuration and metric definitions</summary>
            <pre className="mt-2 overflow-x-auto rounded-lg bg-slate-50 p-3 text-xs">{JSON.stringify({ ...result.configuration, methodology: result.methodology }, null, 2)}</pre>
          </details>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="font-semibold text-slate-900">Exports and paired comparison</h2>
          <p className="mt-1 text-sm text-slate-600">Experiment <code>{result.experiment_id}</code> · seed {result.configuration.random_seed} · local simulation</p>
          <div className="mt-3 flex flex-wrap gap-3">
            {[['trials.csv', 'Download trial CSV'], ['aggregates.csv', 'Download aggregate CSV'], ['report.md', 'Download research report']].map(([kind, label]) => <a key={kind} className="rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50" href={experimentExportUrl(result.experiment_id, kind)}>{label}</a>)}
          </div>
          <p className="mt-3 text-sm text-slate-600">Paired exact McNemar comparison of correctness: {result.paired_comparison.correctness_discordances_traceproof_better} TraceProof wins, {result.paired_comparison.correctness_discordances_baseline_better} baseline wins; p={result.paired_comparison.exact_mcnemar_two_sided_p_value == null ? 'N/A' : result.paired_comparison.exact_mcnemar_two_sided_p_value.toFixed(4)}. Treat as descriptive.</p>
        </section>

        <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 p-5"><h2 className="font-semibold text-slate-900">Scenario results</h2><p className="mt-1 text-sm text-slate-600">{result.configuration.trials} independent trials per scenario; both methods start from equivalent datasets.</p></div>
          <div className="overflow-x-auto"><table className="min-w-full text-sm">
            <thead><tr className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500"><th className="px-4 py-3">Scenario</th><th className="px-4 py-3">Trials</th><th className="px-4 py-3">Mean targets checked</th><th className="px-4 py-3">Baseline TP / FN</th><th className="px-4 py-3">TraceProof TP / FN</th></tr></thead>
            <tbody>{result.scenarios.map((scenario) => <tr className="border-t border-slate-100" key={scenario.scenario}>
              <th scope="row" className="px-4 py-3 text-left font-medium text-slate-700">{scenario.scenario.replaceAll('_', ' ')}</th>
              <td className="px-4 py-3 tabular-nums">{scenario.baseline.total_trials}</td>
              <td className="px-4 py-3 tabular-nums">{scenario.traceproof.dependency_targets_checked / scenario.traceproof.total_trials}</td>
              <td className="px-4 py-3 tabular-nums">{scenario.baseline.true_positive_count} / {scenario.baseline.false_negative_count}</td>
              <td className="px-4 py-3 tabular-nums">{scenario.traceproof.true_positive_count} / {scenario.traceproof.false_negative_count}</td>
            </tr>)}</tbody>
          </table></div>
        </section>
        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm" aria-label="Detection rates by scenario">
          <h2 className="font-semibold text-slate-900">Detection rate by scenario</h2>
          <p className="mt-1 text-xs text-slate-600">Gray = baseline · blue = TraceProof</p>
          <div className="mt-4 space-y-3">{result.scenarios.map((scenario) => <div key={scenario.scenario} className="grid grid-cols-[9rem_1fr] items-center gap-3 text-sm"><span className="capitalize text-slate-600">{scenario.scenario.replaceAll('_', ' ')}</span><div className="space-y-1"><div className="h-3 rounded bg-slate-100" role="img" aria-label={`Baseline detection rate: ${rate(scenario.baseline.detection_rate)}`}><div className="h-3 rounded bg-slate-500" style={{ width: `${(scenario.baseline.detection_rate ?? 0) * 100}%` }} /></div><div className="h-3 rounded bg-slate-100" role="img" aria-label={`TraceProof detection rate: ${rate(scenario.traceproof.detection_rate)}`}><div className="h-3 rounded bg-blue-700" style={{ width: `${(scenario.traceproof.detection_rate ?? 0) * 100}%` }} /></div><span className="text-xs text-slate-500">Baseline {rate(scenario.baseline.detection_rate)} · TraceProof {rate(scenario.traceproof.detection_rate)}</span></div></div>)}</div>
          <p className="mt-3 text-xs text-slate-500">Bars show rates from returned trial outcomes. N/A rates have no denominator and display as zero-width.</p>
        </section>
      </>}
    </div>
  )
}
