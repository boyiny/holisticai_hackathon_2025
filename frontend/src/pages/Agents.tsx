import { useApi } from '../hooks/useApi'
import type { RunListItem } from '../types'

export default function Agents() {
  // Static presentation; prompts are in backend, this view shows excerpts
  const advocatePrompt = `You are Health Advocate... (excerpt)`
  const plannerPrompt = `You are Service Planner... (excerpt)`
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div className="card p-6 space-y-3">
        <div className="font-display font-bold text-xl">Health Advocate</div>
        <div className="text-sm text-slate-600">Represents the user; ensures goals, budget, and safety are respected.</div>
        <div className="text-xs text-slate-500 bg-slate-50 p-3 rounded-lg border border-slate-200 whitespace-pre-wrap">{advocatePrompt}</div>
        <div className="text-xs text-slate-500">Model: <span className="font-mono">gpt-4o-mini</span> (configurable)</div>
      </div>
      <div className="card p-6 space-y-3">
        <div className="font-display font-bold text-xl">Service Planner</div>
        <div className="text-sm text-slate-600">Proposes services; adheres to company eligibility and policies.</div>
        <div className="text-xs text-slate-500 bg-slate-50 p-3 rounded-lg border border-slate-200 whitespace-pre-wrap">{plannerPrompt}</div>
        <div className="text-xs text-slate-500">Model: <span className="font-mono">gpt-4o-mini</span> (configurable)</div>
      </div>
    </div>
  )
}
