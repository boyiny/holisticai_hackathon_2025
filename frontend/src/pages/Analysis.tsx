import { useApi } from '../hooks/useApi'
import type { RunListItem } from '../types'
import { Link } from 'react-router-dom'

export default function Analysis() {
  const { data: runs } = useApi<RunListItem[]>('/api/runs', '/mocks/runs.json')
  return (
    <div className="space-y-6">
      <div className="card p-6">
        <div className="font-display font-bold text-xl mb-2">Filters</div>
        <div className="text-sm text-slate-500">(Filters are stubbed; integrate date/user/status as needed.)</div>
      </div>
      <div className="card p-6">
        <div className="font-display font-bold text-xl mb-4">Runs</div>
        <div className="overflow-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500">
                <th className="py-2">Run ID</th>
                <th className="py-2">Timestamp</th>
                <th className="py-2">User</th>
                <th className="py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {runs?.map(r => (
                <tr key={r.id} className="border-t border-slate-100 dark:border-white/10 hover:bg-slate-50 dark:hover:bg-white/10">
                  <td className="py-2"><Link to={`/runs/${r.id}`} className="text-accent underline">{r.id}</Link></td>
                  <td className="py-2">{r.timestamp}</td>
                  <td className="py-2">{r.user}</td>
                  <td className="py-2">{r.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
