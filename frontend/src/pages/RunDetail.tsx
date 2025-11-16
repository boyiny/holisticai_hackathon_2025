import { useParams } from 'react-router-dom'
import { useApi } from '../hooks/useApi'
import type { RunDetail as RunDetailT } from '../types'

export default function RunDetail() {
  const { id } = useParams()
  const { data } = useApi<RunDetailT>(`/api/runs/${id}`, '/mocks/run_detail_sample.json')
  if (!data) return <div className="card p-6">Loading...</div>
  const summary = data.summary || {}
  return (
    <div className="space-y-6">
      <div className="card p-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="font-display font-bold text-xl">Run {data.id}</div>
            <div className="text-sm text-slate-500">Appointments and plan for {summary.user_name || 'Unknown'}</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card p-6 space-y-3">
          <div className="font-display font-bold text-xl">Plan</div>
          <ul className="text-sm list-disc pl-4">
            {summary.items?.map((it: any, idx: number) => (
              <li key={idx}>M{it.month}: {it.service} — {it.appointment?.start_iso} — ${it.appointment?.price} — [evidence: {it.evidence_flag}]</li>
            ))}
          </ul>
          <div className="text-sm mt-3">Total cost: ${summary.total_cost}</div>
          {summary.warnings?.length ? (
            <div className="text-sm text-yellow-700 bg-yellow-50 border border-yellow-200 p-3 rounded-lg">
              <div className="font-medium">Warnings</div>
              <ul className="list-disc pl-4">
                {summary.warnings.map((w: string, i: number) => <li key={i}>{w}</li>)}
              </ul>
            </div>
          ) : null}
        </div>
        <div className="card p-6 space-y-3">
          <div className="font-display font-bold text-xl">Transcript</div>
          <div className="text-xs text-slate-700 whitespace-pre-wrap bg-slate-50 p-3 rounded-lg border border-slate-200 max-h-[420px] overflow-auto">{data.conversation || 'No transcript found.'}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card p-6">
          <div className="font-display font-bold text-xl mb-3">Claims</div>
          <div className="overflow-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500">
                  <th className="py-2">Claim</th>
                  <th className="py-2">Validity</th>
                  <th className="py-2">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {data.validations?.map((v, i) => (
                  <tr key={i} className="border-t border-slate-100 dark:border-white/10">
                    <td className="py-2">{v.claim?.text || ''}</td>
                    <td className="py-2">{v.validity}</td>
                    <td className="py-2">{v.confidence?.toFixed ? v.confidence.toFixed(2) : v.confidence}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className="card p-6">
          <div className="font-display font-bold text-xl mb-3">Metrics</div>
          <div className="text-sm">Latency events: {data.telemetry?.length || 0}</div>
          <ul className="text-xs list-disc pl-4 mt-2">
            {data.telemetry?.slice(0, 8).map((t, i) => (
              <li key={i}>latency: {t.latency_s?.toFixed ? t.latency_s.toFixed(3) : t.latency_s}s</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
