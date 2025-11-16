import { useApi } from '../hooks/useApi'

type TestItem = { name: string; file: string; description: string; status: string }

export default function Tests() {
  const { data: tests } = useApi<TestItem[]>('/api/tests', '/mocks/tests.json')
  return (
    <div className="card p-6">
      <div className="font-display font-bold text-xl mb-4">Test Suites</div>
      <div className="overflow-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500">
              <th className="py-2">Name</th>
              <th className="py-2">Description</th>
              <th className="py-2">File</th>
              <th className="py-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {tests?.map(t => (
              <tr key={t.name} className="border-t border-slate-100">
                <td className="py-2">{t.name}</td>
                <td className="py-2">{t.description}</td>
                <td className="py-2 font-mono text-xs">{t.file}</td>
                <td className="py-2 text-xs"><span className="px-2 py-1 rounded-full bg-slate-100">{t.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
