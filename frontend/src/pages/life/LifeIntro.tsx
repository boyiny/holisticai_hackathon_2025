import { useNavigate } from 'react-router-dom'

export default function LifeIntro() {
  const nav = useNavigate()
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-center">
      <div className="card p-6 h-full flex items-center justify-center">
        <div className="w-full aspect-[16/9] rounded-2xl overflow-hidden border border-slate-200 dark:border-white/10 bg-black">
          <video className="w-full h-full object-cover" src="/assets/intro.mp4" autoPlay muted loop playsInline controls />
        </div>
      </div>
      <div className="card p-6 space-y-4">
        <div className="font-display font-bold text-2xl md:text-3xl">Simulated Longevity Intake Demo</div>
        <div className="space-y-3 text-sm text-slate-600 dark:text-slate-200/90">
          <p>
            Many people are trying to optimize their long-term healthspan: more energy, better sleep, and better
            metabolic and cognitive outcomes. This demo shows how an AI-driven intake agent could collect
            high-quality lifestyle information before a coaching or clinic visit.
          </p>
          <p>
            First, an intake agent asks structured questions about your goals, routines, and constraints. After collecting
            enough information, the demo generates a pre-visit longevity report.
          </p>
          <p>
            This type of intelligent pre-visit summary can help professionals spend more time advising and less time gathering
            basic information, while giving individuals a clearer view of where they currently are.
          </p>
        </div>
        <div className="p-4 rounded-xl border border-amber-300 bg-amber-50 text-amber-900 dark:bg-white/10 dark:border-white/20 dark:text-white/90 text-xs leading-relaxed">
          <strong>Disclaimer:</strong> This demonstration is for educational purposes only. It does not provide medical advice, diagnosis, or treatment, and is not designed to meet regulatory or clinical safety standards. Any real-world use would require expert validation and safeguards. This demo focuses on <strong>lifestyle and longevity planning only.</strong>
        </div>
        <div>
          <button className="btn" onClick={() => nav('/life/persona')}>Select Persona</button>
        </div>
      </div>
    </div>
  )
}
