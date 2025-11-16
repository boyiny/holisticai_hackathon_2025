import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLife } from '../../context/LifeContext'

export default function LifeExplain() {
  const nav = useNavigate()
  const { persona, focus } = useLife()
  useEffect(() => {
    // placeholder hook to keep page consistent with context updates
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="font-display font-bold text-2xl">What’s happening in this simulation</div>
        <button aria-label="Close" title="Back to dashboard" className="w-8 h-8 rounded-full border border-slate-200 dark:border-white/20 flex items-center justify-center hover:bg-slate-50 dark:hover:bg-white/10" onClick={() => nav('/overview')}>×</button>
      </div>

      {/* Removed the two explainer cards; keeping streamlined view with agent personas below */}

      {/* LEO/LUNA persona cards moved here */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <AgentPersonaCard
          title="LEO — Intake & Coaching"
          description="User-facing intake, coaching context building, and plan drafting. Maintains friendly, supportive tone and non-medical guidance."
          badge="LEO"
          ballVariant="gold"
          personaName={persona?.name || undefined}
        />
        <AgentPersonaCard
          title="LUNA — Audit & Scheduling"
          description="Backend safety review, evidence tagging, final approval, and scheduling logistics. Clear, policy-aligned operations."
          badge="LUNA"
          ballVariant="silver"
        />
      </div>

      {/* Plain-text details below cards for clarity */}
      <div className="text-sm text-slate-600 dark:text-slate-300 space-y-2">
        {focus && (
          <div className="text-xs text-slate-500 dark:text-slate-400">Selected Focus: <span className="font-semibold">{focus.title}</span></div>
        )}
        <p className="text-[11px]">This is an educational lifestyle demo. It does not provide medical advice, diagnosis, or treatment.</p>
      </div>

      <div className="flex items-center justify-between">
        <button className="btn-ghost border border-slate-200 dark:border-white/10" onClick={() => nav('/life/persona')}>Back</button>
        <button className="btn" onClick={() => nav('/life/simulate')}>Start conversation</button>
      </div>
    </div>
  )
}

function AgentPersonaCard({ title, description, badge, ballVariant, personaName }: { title: string; description: string; badge: 'LEO' | 'LUNA'; ballVariant: 'silver' | 'gold'; personaName?: string }) {
  const ballClass = ballVariant === 'gold'
    ? 'from-amber-200 via-amber-400 to-yellow-500 shadow-amber-300/50'
    : 'from-zinc-200 via-slate-300 to-gray-400 shadow-slate-300/50'
  const badgeClass = badge === 'LEO' ? 'bg-teal-100 text-teal-700' : 'bg-violet-100 text-violet-700'
  return (
    <div className="relative card p-4 overflow-visible">
      {/* Larger decorative orb that can overflow the card */}
      <div className={`absolute -top-10 -right-10 w-28 h-28 rounded-full bg-gradient-to-br ${ballClass} opacity-90 ${ballVariant === 'gold' ? 'animate-spin' : 'animate-bounce'} shadow-xl`} />
      <div className="flex items-center justify-between mb-2">
        <div className="font-display font-bold">{title}</div>
        <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${badgeClass}`}>{badge}</span>
      </div>
      <div className="text-sm text-slate-600 dark:text-slate-300">{description}</div>
      {badge === 'LEO' && personaName ? (
        <div className="text-xs text-slate-500 mt-2">Persona: <span className="font-medium">{personaName}</span></div>
      ) : null}
      <div className="mt-3 h-1 bg-gradient-to-r from-transparent via-slate-200 dark:via-white/10 to-transparent" />
    </div>
  )
}
