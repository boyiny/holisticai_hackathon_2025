export default function Tools() {
  const tools = [
    { name: 'Valyu Validator', by: 'Service Planner', config: 'URL from .env / CLI', status: 'OK' },
    { name: 'Clinic Scheduler', by: 'Service Planner', config: 'Mock slots (deterministic)', status: 'OK' },
    { name: 'Conversation Saver', by: 'Both', config: 'Writes to data/', status: 'OK' },
    { name: 'Summarizer', by: 'Pipeline', config: 'Final plan text + JSON', status: 'OK' },
  ]
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {tools.map(t => (
        <div key={t.name} className="card p-6">
          <div className="font-display font-bold text-xl">{t.name}</div>
          <div className="text-sm text-slate-600">Used by: {t.by}</div>
          <div className="text-xs text-slate-500 mt-2">Config: {t.config}</div>
          <div className="mt-3 text-xs">
            <span className={`px-2 py-1 rounded-full ${t.status === 'OK' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>{t.status}</span>
          </div>
        </div>
      ))}
    </div>
  )
}
