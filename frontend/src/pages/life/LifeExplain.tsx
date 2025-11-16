import { useNavigate } from 'react-router-dom'
import { useLife } from '../../context/LifeContext'

export default function LifeExplain() {
  const nav = useNavigate()
  const { persona, focus } = useLife()

  return (
    <div className="space-y-6">
      <div className="font-display font-bold text-2xl">What’s happening in this simulation</div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card p-6 space-y-2">
          <div className="font-display font-bold text-xl">Longevity Intake Agent</div>
          <div className="text-sm text-slate-600 dark:text-slate-300">
            In this demo, the AI agent acts as a longevity intake assistant. It will ask structured questions about your
            lifestyle, goals, and constraints in order to build a real-time intake report. Its purpose is to help coaches and
            clinicians spend more time advising and less time interviewing.
          </div>
        </div>
        <div className="card p-6 space-y-2">
          <div className="font-display font-bold text-xl">Persona: {persona?.name || '—'}</div>
          <div className="text-sm text-slate-600 dark:text-slate-300">
            This persona is a fictional individual with a specific age, background, and goal. They do not know any medical
            diagnoses — they simply describe habits, concerns, and goals in everyday language. This allows the agent to practice
            identifying what information matters most for longevity planning.
          </div>
          {focus && (
            <div className="text-xs text-slate-500 dark:text-slate-400">Selected Focus: <span className="font-semibold">{focus.title}</span></div>
          )}
        </div>
      </div>
      <div className="text-sm text-slate-600 dark:text-slate-300">
        As the conversation unfolds, the system generates and continually updates a longevity intake snapshot. At the end, the
        agent can evaluate its own output and highlight where the intake could be improved in future interactions.
      </div>
      <div className="flex items-center justify-between">
        <button className="btn-ghost border border-slate-200 dark:border-white/10" onClick={() => nav('/life/persona')}>Back</button>
        <button className="btn" onClick={() => nav('/overview')}>Start conversation</button>
      </div>
    </div>
  )
}
