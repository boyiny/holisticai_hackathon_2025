import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLife } from '../../context/LifeContext'
import { WorkflowTimeline, type WorkflowStepState, type StepId } from '../../components/WorkflowTimeline'

type SnapshotSection = {
  primaryGoals: string[]
  lifestyleOverview: string
  strengths: string[]
  potentialConcerns: string[]
  focusAreas: string[]
  questionsForCoach: string[]
}

type ConversationStep = {
  id: number
  messages: { speaker: 'agent' | 'persona'; text: string }[]
  snapshot: SnapshotSection
}

export default function SimulationScreen() {
  const nav = useNavigate()
  const { persona, focus } = useLife()
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [stageIndex, setStageIndex] = useState(0)
  const startedAtRef = useRef<number>(Date.now())

  useEffect(() => {
    if (!persona || !focus) return
  }, [persona, focus])

  const conversationSteps: ConversationStep[] = useMemo(() => {
    const name = persona?.name || 'User'
    const focusTitle = focus?.title || 'Longevity'
    return [
      {
        id: 0,
        messages: [
          { speaker: 'agent', text: `Thanks for taking time to do this. I’m a longevity intake assistant, here to understand your daily routines and long-term goals so a human coach can make the most of your session. To start, in your own words, what matters most to you right now?` },
          { speaker: 'persona', text: `I’m ${name.split(' ')[0]}, and I’m just tired all the time. I work long days at my desk and by the evening I crash on the sofa. I don’t want this to catch up with me later.` },
        ],
        snapshot: {
          primaryGoals: [
            `Increase day-to-day energy within the next 3–6 months`,
            `Reduce long-term lifestyle risk by improving movement and sleep`,
            `Focus area: ${focusTitle}`,
          ],
          lifestyleOverview: `${name} works long desk hours and reports low evening energy. Basic routines not yet clarified.`,
          strengths: [],
          potentialConcerns: [
            'Energy dips and perceived fatigue (non-medical; lifestyle context)',
          ],
          focusAreas: [focusTitle],
          questionsForCoach: [
            'What would be the first 1–2 habits that could improve energy safely?',
          ],
        },
      },
      {
        id: 1,
        messages: [
          { speaker: 'agent', text: `Can you walk me through a typical weekday—wake time, work pattern, and bedtime?` },
          { speaker: 'persona', text: `Up around 7:30, coffee, straight to my laptop by 8. Mostly meetings until late afternoon. I often work until 7:30–8:00 pm and go to bed around midnight.` },
        ],
        snapshot: {
          primaryGoals: [
            `Increase day-to-day energy within the next 3–6 months`,
            `Reduce long-term lifestyle risk by improving movement and sleep`,
            `Focus area: ${focusTitle}`,
          ],
          lifestyleOverview: `Weekdays: 7:30 wake, desk work 8:00–19:30, bedtime near midnight; extended sitting and late cutoff from work.`,
          strengths: [],
          potentialConcerns: [
            'Chronic sleep restriction risk from late bedtime',
            'High sitting time across the workday',
          ],
          focusAreas: [focusTitle, 'Sleep timing window', 'Workday micro-breaks'],
          questionsForCoach: [
            'Could earlier evening wind-down improve sleep quality and energy?',
          ],
        },
      },
      {
        id: 2,
        messages: [
          { speaker: 'agent', text: `How much movement do you usually get in a normal week? Any structured exercise?` },
          { speaker: 'persona', text: `Barely any during the week. Sometimes a short walk on weekends, maybe 30 minutes.` },
        ],
        snapshot: {
          primaryGoals: [
            `Increase day-to-day energy within the next 3–6 months`,
            `Reduce long-term lifestyle risk by improving movement and sleep`,
            `Focus area: ${focusTitle}`,
          ],
          lifestyleOverview: `Minimal weekday movement; occasional short weekend walk. No current strength or aerobic practice.`,
          strengths: ['Willingness to improve and test small changes'],
          potentialConcerns: [
            'Very low weekly movement volume',
          ],
          focusAreas: ['Strength & Movement', 'Light daily steps', 'Beginner strength routine'],
          questionsForCoach: [
            'Best way to start with short, safe strength sessions at home?',
          ],
        },
      },
      {
        id: 3,
        messages: [
          { speaker: 'agent', text: `Tell me about nutrition and stress—typical meals, late eating, caffeine, or pressure during the day.` },
          { speaker: 'persona', text: `I often skip breakfast and eat takeout late. Lots of afternoon coffee. I feel wired at night even when I’m tired.` },
        ],
        snapshot: {
          primaryGoals: [
            `Increase day-to-day energy within the next 3–6 months`,
            `Reduce long-term lifestyle risk by improving movement and sleep`,
            `Focus area: ${focusTitle}`,
          ],
          lifestyleOverview: `Frequent late meals and high afternoon caffeine; evening alertness despite overall tiredness.`,
          strengths: ['Does not smoke', 'Alcohol likely modest or occasional'],
          potentialConcerns: [
            'Late eating may reduce perceived sleep quality',
            'High afternoon caffeine may delay wind-down',
          ],
          focusAreas: ['Evening routine', 'Earlier protein-forward meal', 'Caffeine cutoff timing'],
          questionsForCoach: [
            'How to shift dinner earlier on workdays?',
            'What’s a realistic caffeine cutoff to try next week?',
          ],
        },
      },
      {
        id: 4,
        messages: [
          { speaker: 'agent', text: `Thanks, I’ll compile a simple intake snapshot for your coach. We’ll focus on a few habits you can practice safely.` },
          { speaker: 'persona', text: `Great—short, doable steps would help a lot. I’m ready to try.` },
        ],
        snapshot: {
          primaryGoals: [
            `Increase day-to-day energy within the next 3–6 months`,
            `Reduce long-term lifestyle risk by improving movement and sleep`,
            `Focus area: ${focusTitle}`,
          ],
          lifestyleOverview: `Long desk days, late bedtime, minimal weekday movement, late takeout, high afternoon caffeine.`,
          strengths: ['Motivated to improve', 'Non-smoker', 'Willing to test small changes'],
          potentialConcerns: [
            'High sitting time and very low weekly movement',
            'Late eating and caffeine timing may affect perceived sleep quality',
          ],
          focusAreas: [
            'Two 20–25 min beginner strength sessions/week',
            'Light daily steps or movement snacks',
            'Wind-down routine + earlier dinner where possible',
          ],
          questionsForCoach: [
            'Confirm safe progression for strength routine',
            'Adjust evening routine and meal timing to fit work constraints',
          ],
        },
      },
    ]
  }, [persona, focus])

  const lastIndex = conversationSteps.length - 1
  const currentSnapshot = conversationSteps[Math.min(currentStepIndex, lastIndex)]?.snapshot

  // Auto-advance conversation steps
  useEffect(() => {
    if (!persona || !focus) return
    if (currentStepIndex >= lastIndex) return
    const id = setInterval(() => {
      setCurrentStepIndex((i) => (i < lastIndex ? i + 1 : i))
    }, 2500)
    return () => clearInterval(id)
  }, [persona, focus, currentStepIndex, lastIndex])

  // Flow stages progression (independent, covers full pipeline)
  const STAGES = useMemo(
    () => [
      'Start',
      'Intake',
      'PlanDraft',
      'PlanReview',
      'Audit',
      'Revision',
      'FinalPlan',
      'Scheduling',
      'FinalSummary',
    ],
    []
  )

  useEffect(() => {
    if (!persona || !focus) return
    if (stageIndex >= STAGES.length - 1) return
    const id = setInterval(() => {
      setStageIndex((s) => (s < STAGES.length - 1 ? s + 1 : s))
    }, 1800)
    return () => clearInterval(id)
  }, [persona, focus, stageIndex, STAGES.length])

  if (!persona || !focus) {
    return (
      <div className="card p-6">
        <div className="font-display font-bold text-xl mb-2">No persona selected</div>
        <div className="text-sm text-slate-600 dark:text-slate-300">Please restart the demo and choose a persona and focus area.</div>
        <div className="mt-4"><button className="btn" onClick={() => nav('/life/persona')}>Restart</button></div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <button className="btn-ghost border border-slate-200 dark:border-white/10" onClick={() => nav('/life/explain')}>Back</button>
        <div className="flex items-center gap-3">
          <button className="text-xs underline text-slate-600 dark:text-slate-300" onClick={() => alert('Details coming soon')}>Details about this demo</button>
          <button aria-label="Close" title="Back to dashboard" className="w-8 h-8 rounded-full border border-slate-200 dark:border-white/20 flex items-center justify-center hover:bg-slate-50 dark:hover:bg-white/10" onClick={() => nav('/overview')}>×</button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        <div className="lg:col-span-2 card p-4 flex flex-col min-h-[60vh]">
          <div className="mb-2">
            <div className="font-display font-bold">Simulated Interview</div>
            <div className="text-xs text-slate-500">audio by 11Labs (simulated)</div>
            <div className="text-xs text-slate-500 mt-1">Persona: <span className="font-medium">{persona.name}</span> — Focus: <span className="font-medium">{focus.title}</span></div>
          </div>
          <div className="flex-1 overflow-auto space-y-2 pr-1">
            {conversationSteps.slice(0, currentStepIndex + 1).flatMap(s => s.messages).map((m, idx) => (
              <div key={idx} className={`max-w-[88%] rounded-2xl px-3 py-2 text-sm ${m.speaker === 'agent' ? 'bg-violet-600 text-white self-start rounded-bl-sm' : 'bg-slate-100 dark:bg-white/10 text-slate-900 dark:text-white self-end rounded-br-sm ml-auto'}`}>
                <div className="text-[11px] opacity-80 mb-0.5">{m.speaker === 'agent' ? 'Intake Agent' : persona.name}</div>
                <div>{m.text}</div>
              </div>
            ))}
          </div>
          <div className="mt-3 text-[11px] text-slate-500 flex items-center justify-between">
            <div>Step {Math.min(currentStepIndex + 1, conversationSteps.length)} / {conversationSteps.length} — auto-playing…</div>
            <button className="btn-ghost border border-slate-200 dark:border-white/10 text-xs" onClick={() => nav('/life/persona')}>Skip to other simulations</button>
          </div>
        </div>

        <div className="lg:col-span-3 card p-4">
          <div className="font-display font-bold text-lg mb-2">Generated Longevity Snapshot</div>
          <div className="space-y-4 text-sm">
            <Section title="Primary goals">
              <ul className="list-disc pl-5 space-y-1">
                {currentSnapshot.primaryGoals.map((g, i) => <li key={i}>{g}</li>)}
              </ul>
            </Section>
            <Section title="Current lifestyle overview">
              <p>{currentSnapshot.lifestyleOverview}</p>
            </Section>
            <Section title="Existing strengths">
              {currentSnapshot.strengths.length ? (
                <ul className="list-disc pl-5 space-y-1">{currentSnapshot.strengths.map((s, i) => <li key={i}>{s}</li>)}</ul>
              ) : <div className="text-slate-500">To be identified.</div>}
            </Section>
            <Section title="Potential lifestyle concerns (not medical advice)">
              <ul className="list-disc pl-5 space-y-1">
                {currentSnapshot.potentialConcerns.map((c, i) => <li key={i}>{c}</li>)}
              </ul>
              <div className="text-[11px] text-slate-500 mt-2">These are lifestyle patterns to explore; they are not medical diagnoses.</div>
            </Section>
            <Section title="Suggested habit focus areas">
              <ul className="list-disc pl-5 space-y-1">
                {currentSnapshot.focusAreas.map((a, i) => <li key={i}>{a}</li>)}
              </ul>
            </Section>
            <Section title="Questions for human coach or clinician">
              <ul className="list-disc pl-5 space-y-1">
                {currentSnapshot.questionsForCoach.map((q, i) => <li key={i}>{q}</li>)}
              </ul>
            </Section>
            <div className="p-3 rounded-lg border border-amber-300 bg-amber-50 text-amber-900 dark:bg-white/10 dark:border-white/20 dark:text-white/90 text-[11px]">
              This snapshot is educational and not medical advice.
            </div>
          </div>
        </div>
      </div>

      {/* Bottom metrics and flow */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="card p-4">
          <div className="font-display font-bold mb-2">Run Metrics</div>
          <ul className="text-sm space-y-1">
            <li>Elapsed: {((Date.now() - startedAtRef.current) / 1000).toFixed(1)}s</li>
            <li>Messages shown: {conversationSteps.slice(0, currentStepIndex + 1).reduce((acc, s) => acc + s.messages.length, 0)}</li>
            <li>Snapshot completeness: {Math.round(((currentStepIndex + 1) / conversationSteps.length) * 100)}%</li>
            <li>Flow progress: {Math.round(((stageIndex + 1) / STAGES.length) * 100)}%</li>
          </ul>
        </div>
        <div className="card p-4">
          <div className="font-display font-bold mb-2">Quality Signals (simulated)</div>
          <ul className="text-sm space-y-1">
            <li>Evidence coverage: {currentStepIndex >= 3 ? 'Improving' : 'Collecting context'}</li>
            <li>Plan items (so far): {Math.min(3, currentStepIndex + 1)}</li>
            <li>Warnings noted: {currentSnapshot.potentialConcerns.length}</li>
          </ul>
        </div>
        <div className="card p-4">
          <div className="font-display font-bold mb-2">Agent Flow</div>
          <FlowBar stages={STAGES} activeIndex={stageIndex} />
        </div>
      </div>

      {/* Workflow lane */}
      <div className="card p-4">
        <div className="font-display font-bold text-lg mb-2">LEO ↔ LUNA Workflow</div>
        <WorkflowTimeline steps={deriveStepsFromStages(STAGES, stageIndex)} currentStepId={STAGES[stageIndex] as StepId} />
      </div>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-2">
      <div className="font-semibold">{title}</div>
      <div>{children}</div>
      <div className="border-b border-slate-100 dark:border-white/10" />
    </div>
  )
}

function deriveStepsFromStages(stages: string[], activeIdx: number): WorkflowStepState[] {
  const agentByStep: Record<string, 'LEO' | 'LUNA'> = {
    Start: 'LEO',
    Intake: 'LEO',
    PlanDraft: 'LEO',
    PlanReview: 'LEO',
    Audit: 'LUNA',
    Revision: 'LEO',
    FinalPlan: 'LUNA',
    Scheduling: 'LUNA',
    FinalSummary: 'LEO',
  }
  const desc: Record<string, string> = {
    Start: 'Initialize context, welcome user',
    Intake: 'Collect routines, goals, constraints',
    PlanDraft: 'Generate initial plan from intake',
    PlanReview: 'Self-check before handoff',
    Audit: 'Safety + guideline audit, evidence tags',
    Revision: 'Update plan using audit feedback',
    FinalPlan: 'Verify consistency, approve',
    Scheduling: 'Create schedule for sessions',
    FinalSummary: 'Explain plan and next steps',
  }
  return stages.map((id, i) => ({
    id: id as StepId,
    title: id,
    description: desc[id] || '',
    responsibleAgent: agentByStep[id],
    status: i < activeIdx ? 'success' : i === activeIdx ? 'running' : 'pending',
  }))
}
function FlowBar({ stages, activeIndex }: { stages: string[]; activeIndex: number }) {
  return (
    <div className="flex items-center gap-2 overflow-auto">
      {stages.map((s, i) => (
        <div key={s} className="flex items-center gap-2">
          <div className={`flex items-center gap-2`}>
            <div className={`w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-semibold ${i <= activeIndex ? 'bg-violet-600 text-white' : 'bg-slate-200 dark:bg-white/10 text-slate-700 dark:text-white/70'}`}>{i + 1}</div>
            <div className={`text-xs ${i === activeIndex ? 'text-violet-700 dark:text-violet-300 font-medium' : 'text-slate-600 dark:text-slate-300'}`}>{s}</div>
          </div>
          {i < stages.length - 1 && (<div className={`w-10 h-[2px] ${i < activeIndex ? 'bg-violet-600' : 'bg-slate-200 dark:bg-white/10'}`} />)}
        </div>
      ))}
    </div>
  )
}
