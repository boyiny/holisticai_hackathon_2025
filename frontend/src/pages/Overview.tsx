import MetricCard from '../components/MetricCard'
import { useApi } from '../hooks/useApi'
import type { OverviewMetrics, RunListItem } from '../types'
import { Link } from 'react-router-dom'

export default function Overview() {
  const { data: metrics } = useApi<OverviewMetrics>('/api/metrics/overview', '/mocks/metrics_overview.json')
  const { data: runs } = useApi<RunListItem[]>('/api/runs', '/mocks/runs.json')
  return (
    <div className="space-y-6">
      <div className="card p-6">
        <div className="font-display font-bold text-2xl md:text-3xl">Longevity Agent Reliability Dashboard</div>
        <div className="text-slate-500 text-sm mt-1">Multi-agent longevity planning with scientific validation and scheduling.</div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard title="Avg Latency" value={metrics?.avg_latency_s ? `${metrics?.avg_latency_s.toFixed(2)}s` : null} />
        <MetricCard title="Avg Tokens" value={metrics?.avg_tokens ?? null} />
        <MetricCard title="Consistency" value={metrics?.plan_consistency_score ?? null} subtitle="from tests" />
        <MetricCard title="Scientific Coverage" value={metrics?.scientific_validity_coverage_pct != null ? `${metrics?.scientific_validity_coverage_pct}%` : null} />
      </div>
      <div className="card p-6">
        <div className="font-display font-bold text-xl mb-4">Recent Runs</div>
        <div className="overflow-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500">
                <th className="py-2">Run ID</th>
                <th className="py-2">Timestamp</th>
                <th className="py-2">User</th>
                <th className="py-2">Outcome</th>
                <th className="py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {runs?.map(r => (
                <tr key={r.id} className="border-t border-slate-100 dark:border-white/10 hover:bg-slate-50 dark:hover:bg-white/10">
                  <td className="py-2"><Link to={`/runs/${r.id}`} className="text-accent underline">{r.id}</Link></td>
                  <td className="py-2">{r.timestamp}</td>
                  <td className="py-2">{r.user}</td>
                  <td className="py-2">{r.plan_score ?? '—'}</td>
                  <td className="py-2">
                    <span className={`px-2 py-1 rounded-full text-xs ${r.status === 'success' ? 'bg-green-100 text-green-700' : r.status === 'warning' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>{r.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
