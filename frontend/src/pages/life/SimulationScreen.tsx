import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLife } from '../../context/LifeContext'
import { WorkflowTimeline, type WorkflowStepState, type StepId } from '../../components/WorkflowTimeline'
import { useConversation } from '@elevenlabs/react'

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
  const [mode, setMode] = useState<'sim' | 'live' | 'duo' | 'duoText'>('sim')
  const [agentIdInput, setAgentIdInput] = useState<string>(import.meta.env.VITE_ELEVEN_AGENT_ID || '')
  const startedAtRef = useRef<number>(Date.now())
  const [generatedSnapshot, setGeneratedSnapshot] = useState<SnapshotSection | null>(null)

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
          <div className="flex items-center justify-between mb-2">
            <div>
              <div className="font-display font-bold">{mode === 'live' ? 'Live Interview (ElevenLabs)' : mode === 'duo' ? 'Duo Agents: LEO ↔ LUNA' : 'Simulated Interview'}</div>
              <div className="text-xs text-slate-500">
                {mode === 'live' ? 'real-time voice via ElevenLabs' : mode === 'duo' ? 'two agents conversing via ElevenLabs' : 'audio by 11Labs (simulated)'}
              </div>
              <div className="text-xs text-slate-500 mt-1">Persona: <span className="font-medium">{persona.name}</span> — Focus: <span className="font-medium">{focus.title}</span></div>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <select className="input text-xs" value={mode} onChange={(e) => { setMode(e.target.value as any); setGeneratedSnapshot(null) }}>
                <option value="sim">Simulated</option>
                <option value="live">Live (You ↔ Agent)</option>
                <option value="duo">Duo (Agents SDK)</option>
                <option value="duoText">Duo (Text + TTS)</option>
              </select>
            </div>
          </div>

          {mode === 'live' ? (
            <LiveElevenPanel agentIdInput={agentIdInput} setAgentIdInput={setAgentIdInput} personaName={persona.name} />
          ) : mode === 'duo' ? (
            <DuoElevenPanel personaName={persona.name} focusTitle={focus.title} onMessagesChange={(msgs) => setGeneratedSnapshot(computeSnapshotFromMessages(msgs, persona.name, focus.title))} />
          ) : mode === 'duoText' ? (
            <DuoTextTTSPanel personaName={persona.name} focusTitle={focus.title} onMessagesReady={(msgs) => setGeneratedSnapshot(computeSnapshotFromMessages(msgs, persona.name, focus.title))} />
          ) : (
            <>
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
            </>
          )}
        </div>

        <div className="lg:col-span-3 card p-4">
          <div className="font-display font-bold text-lg mb-2">Generated Longevity Snapshot</div>
          <div className="space-y-4 text-sm">
            {((mode === 'duo' || mode === 'duoText') && generatedSnapshot) ? (
              <SnapshotView snap={generatedSnapshot} />
            ) : (
              <SnapshotView snap={currentSnapshot} />
            )}
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

function buildLocalDuoMock(turns: number, personaName: string, focusTitle: string) {
  const L = Math.max(2, Math.min(12, turns))
  const seed = [
    { speaker: 'LEO' as const, text: `I’m LEO. I’ll gather ${personaName}’s goals and routines around ${focusTitle}.` },
    { speaker: 'LUNA' as const, text: `I’m LUNA. I’ll check safety, evidence, and schedule realistic next steps.` },
  ]
  const pool = [
    { speaker: 'LEO' as const, text: `Initial intake suggests limited weekday movement and late bedtime. I propose simple movement snacks and earlier wind-down.` },
    { speaker: 'LUNA' as const, text: `Evidence supports small, frequent bouts of movement. Let’s keep intensity low initially and set two 20–25 min sessions per week.` },
    { speaker: 'LEO' as const, text: `Nutrition timing seems late. We can try moving dinner earlier and set a caffeine cutoff.` },
    { speaker: 'LUNA' as const, text: `That’s aligned with sleep hygiene research; let’s document a 1–2 hour earlier dinner target and a 2 pm caffeine cutoff.` },
    { speaker: 'LEO' as const, text: `We’ll keep phrasing as lifestyle coaching, not medical advice, and suggest review with a clinician.` },
    { speaker: 'LUNA' as const, text: `Agreed. I’ll include disclaimers and plan a quick weekly check-in to adapt the routine.` },
  ]
  const out = [...seed]
  let i = 0
  while (out.length < L) {
    out.push(pool[i % pool.length])
    i++
  }
  return out.slice(0, L)
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

function SnapshotView({ snap }: { snap: SnapshotSection }) {
  return (
    <>
      <Section title="Primary goals">
        <ul className="list-disc pl-5 space-y-1">
          {snap.primaryGoals.map((g, i) => <li key={i}>{g}</li>)}
        </ul>
      </Section>
      <Section title="Current lifestyle overview">
        <p>{snap.lifestyleOverview}</p>
      </Section>
      <Section title="Existing strengths">
        {snap.strengths.length ? (
          <ul className="list-disc pl-5 space-y-1">{snap.strengths.map((s, i) => <li key={i}>{s}</li>)}</ul>
        ) : <div className="text-slate-500">To be identified.</div>}
      </Section>
      <Section title="Potential lifestyle concerns (not medical advice)">
        <ul className="list-disc pl-5 space-y-1">
          {snap.potentialConcerns.map((c, i) => <li key={i}>{c}</li>)}
        </ul>
        <div className="text-[11px] text-slate-500 mt-2">These are lifestyle patterns to explore; they are not medical diagnoses.</div>
      </Section>
      <Section title="Suggested habit focus areas">
        <ul className="list-disc pl-5 space-y-1">
          {snap.focusAreas.map((a, i) => <li key={i}>{a}</li>)}
        </ul>
      </Section>
      <Section title="Questions for human coach or clinician">
        <ul className="list-disc pl-5 space-y-1">
          {snap.questionsForCoach.map((q, i) => <li key={i}>{q}</li>)}
        </ul>
      </Section>
    </>
  )
}

function computeSnapshotFromMessages(msgs: { speaker: 'LEO' | 'LUNA'; text: string }[], personaName: string, focusTitle: string): SnapshotSection {
  const text = msgs.map(m => `${m.speaker}: ${m.text}`).join('\n')
  const lower = text.toLowerCase()
  const concerns: string[] = []
  if (lower.includes('late') || lower.includes('midnight')) concerns.push('Late bedtime may reduce perceived sleep quality')
  if (lower.includes('caffeine') || lower.includes('coffee')) concerns.push('High afternoon caffeine can delay wind-down')
  if (lower.includes('walk') || lower.includes('exercise') || lower.includes('sedentary') || lower.includes('sitting')) concerns.push('Low weekly movement volume or prolonged sitting')
  if (!concerns.length) concerns.push('Areas to clarify in follow-up')
  const strengths: string[] = []
  if (lower.includes('motiv') || lower.includes('ready') || lower.includes('willing')) strengths.push('Motivated to improve')
  if (!strengths.length) strengths.push('Open to small habit changes')
  const focusAreas = Array.from(new Set([focusTitle, ...(lower.includes('sleep') ? ['Sleep timing'] : []), ...(lower.includes('movement') || lower.includes('walk') ? ['Strength & Movement'] : []), ...(lower.includes('nutrition') || lower.includes('dinner') ? ['Meal timing'] : [])])).filter(Boolean)
  const goals = [`Make progress on ${focusTitle} over the next 3–6 months`, 'Reduce lifestyle risk via sleep and movement basics']
  const overview = msgs.slice(0, 4).map(m => `${m.speaker}: ${m.text}`).join(' ')
  const questionsForCoach = ['Confirm safe progression for movement', 'Adjust evening routine and meal timing to fit constraints']
  return { primaryGoals: goals, lifestyleOverview: overview || `${personaName} provided initial context.`, strengths, potentialConcerns: concerns, focusAreas, questionsForCoach }
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

type LiveElevenPanelProps = {
  agentIdInput: string
  setAgentIdInput: (v: string) => void
  personaName: string
}

function LiveElevenPanel({ agentIdInput, setAgentIdInput, personaName }: LiveElevenPanelProps) {
  const [logs, setLogs] = useState<string[]>([])
  const [messages, setMessages] = useState<{ speaker: 'agent' | 'user'; text: string }[]>([])
  const [connecting, setConnecting] = useState(false)
  const [micMuted, setMicMuted] = useState(false)
  const [volume, setVolume] = useState(0.9)

  const conversation = useConversation({
    micMuted,
    volume,
    onStatusChange: (s) => setLogs((l) => [`status: ${s}`, ...l].slice(0, 50)),
    onModeChange: (m) => setLogs((l) => [`mode: ${m}`, ...l].slice(0, 50)),
    onError: (e) => setLogs((l) => [`error: ${String(e)}`,...l].slice(0, 50)),
    onMessage: (m: any) => {
      try {
        // Try to extract a readable text and role
        const role: 'agent' | 'user' | undefined = (m?.role === 'assistant' || m?.role === 'agent') ? 'agent' : (m?.role === 'user' ? 'user' : undefined)
        const text: string | undefined = m?.text ?? m?.message ?? m?.content ?? (typeof m === 'string' ? m : undefined)
        if (role && text && text.trim()) {
          setMessages((prev) => [...prev, { speaker: role, text }])
        }
        setLogs((l) => [`msg: ${JSON.stringify(m).slice(0, 200)}`,...l].slice(0, 50))
      } catch (err) {
        setLogs((l) => [`msg-parse-error: ${String(err)}`,...l].slice(0, 50))
      }
    },
  })

  const { status, isSpeaking, sendUserMessage, sendUserActivity } = conversation

  const start = async () => {
    if (!agentIdInput) {
      alert('Enter a public ElevenLabs Agent ID or set VITE_ELEVEN_AGENT_ID in your env.')
      return
    }
    try {
      setConnecting(true)
      // Request mic access explicitly so the browser shows a clear prompt first
      await navigator.mediaDevices.getUserMedia({ audio: true })
      await conversation.startSession({
        agentId: agentIdInput,
        connectionType: 'webrtc',
      })
    } catch (e) {
      console.error(e)
      alert('Failed to start live voice session. Check Agent ID and permissions.')
    } finally {
      setConnecting(false)
    }
  }

  const stop = async () => {
    try { await conversation.endSession() } catch {}
  }

  const [input, setInput] = useState('')

  return (
    <div className="flex-1 flex flex-col">
      <div className="flex flex-wrap items-center gap-2 mb-2">
        <input
          className="input text-xs flex-1 min-w-[160px]"
          placeholder="Public Agent ID (from ElevenLabs)"
          value={agentIdInput}
          onChange={(e) => setAgentIdInput(e.target.value)}
        />
        {status !== 'connected' ? (
          <button className="btn" onClick={start} disabled={connecting}>{connecting ? 'Connecting…' : 'Start'}</button>
        ) : (
          <button className="btn-ghost border border-slate-200 dark:border-white/10" onClick={stop}>End</button>
        )}
        <label className="text-xs flex items-center gap-1 ml-auto">
          <input type="checkbox" checked={micMuted} onChange={(e) => setMicMuted(e.target.checked)} /> Mic muted
        </label>
      </div>

      <div className="text-[11px] text-slate-500 mb-2 flex items-center gap-3">
        <StatusPill label={status === 'connected' ? 'Connected' : 'Disconnected'} tone={status === 'connected' ? 'good' : 'warn'} />
        <StatusPill label={isSpeaking ? 'Agent: Speaking' : 'Agent: Listening'} tone={isSpeaking ? 'accent' : 'idle'} pulse={isSpeaking} />
        <div className="ml-auto flex items-center gap-2">
          <span>Vol</span>
          <input type="range" min={0} max={1} step={0.05} value={volume} onChange={(e) => setVolume(parseFloat(e.target.value))} />
        </div>
      </div>

      <div className="flex-1 overflow-auto space-y-2 pr-1">
        {messages.length === 0 && (
          <div className="text-xs text-slate-500">Speak to the agent after connecting, or type below. Your voice will be transcribed and the agent will reply with voice. Turn-taking is visible above.</div>
        )}
        {messages.map((m, idx) => (
          <div key={idx} className={`max-w-[88%] rounded-2xl px-3 py-2 text-sm ${m.speaker === 'agent' ? 'bg-violet-600 text-white self-start rounded-bl-sm' : 'bg-slate-100 dark:bg-white/10 text-slate-900 dark:text-white self-end rounded-br-sm ml-auto'}`}>
            <div className="text-[11px] opacity-80 mb-0.5">{m.speaker === 'agent' ? 'Intake Agent' : personaName}</div>
            <div>{m.text}</div>
          </div>
        ))}
      </div>

      <form
        className="mt-2 flex items-center gap-2"
        onSubmit={(e) => {
          e.preventDefault()
          if (!input.trim()) return
          sendUserMessage(input.trim())
          setMessages((prev) => [...prev, { speaker: 'user', text: input.trim() }])
          setInput('')
        }}
      >
        <input
          className="input flex-1"
          placeholder="Type to message the agent…"
          value={input}
          onChange={(e) => {
            setInput(e.target.value)
            sendUserActivity()
          }}
        />
        <button className="btn" type="submit">Send</button>
      </form>

      <details className="mt-3">
        <summary className="text-xs text-slate-500 cursor-pointer">Debug</summary>
        <div className="text-[11px] text-slate-600 dark:text-slate-300 mt-2 space-y-1 max-h-32 overflow-auto">
          {logs.map((l, i) => <div key={i}>{l}</div>)}
        </div>
      </details>
    </div>
  )
}

function StatusPill({ label, tone, pulse }: { label: string; tone: 'good' | 'warn' | 'accent' | 'idle'; pulse?: boolean }) {
  const toneClass = tone === 'good'
    ? 'bg-emerald-100 text-emerald-700'
    : tone === 'warn'
      ? 'bg-amber-100 text-amber-700'
      : tone === 'accent'
        ? 'bg-violet-100 text-violet-700'
        : 'bg-slate-100 text-slate-700'
  return (
    <div className={`text-[10px] px-2 py-1 rounded-full ${toneClass} ${pulse ? 'animate-pulse' : ''}`}>{label}</div>
  )
}

function DuoElevenPanel({ personaName, focusTitle, onMessagesChange }: { personaName: string; focusTitle: string; onMessagesChange?: (msgs: { speaker: 'LEO' | 'LUNA'; text: string }[]) => void }) {
  const apiBase = (import.meta as any).env?.VITE_API_BASE || ''
  const defaultLeo = (import.meta as any).env?.VITE_ELEVEN_LEO_AGENT_ID || 'agent_8901ka69ad6eegnvkv2b4c33yj6b'
  const defaultLuna = (import.meta as any).env?.VITE_ELEVEN_LUNA_AGENT_ID || 'agent_6401ka69c4k5eg08atbsgfd0kgka'
  const [leoId, setLeoId] = useState<string>(defaultLeo)
  const [lunaId, setLunaId] = useState<string>(defaultLuna)
  const [connecting, setConnecting] = useState(false)
  const [logs, setLogs] = useState<string[]>([])
  const [messages, setMessages] = useState<{ speaker: 'LEO' | 'LUNA'; text: string }[]>([])
  const [leoVol, setLeoVol] = useState(0.9)
  const [lunaVol, setLunaVol] = useState(0.9)
  const [deviceRole, setDeviceRole] = useState<'LEO' | 'LUNA' | 'BOTH'>('BOTH')

  const [textBridge, setTextBridge] = useState(true)

  const sharedOverrides = textBridge
    ? { conversation: { textOnly: true }, agent: { firstMessage: `Hi, I am part of a duo conversation. User: ${personaName}; Focus: ${focusTitle}. Keep replies concise.` } }
    : undefined

  const leo = useConversation({
    volume: leoVol,
    micMuted: true,
    overrides: sharedOverrides,
    onStatusChange: (s) => setLogs((l) => [`LEO status: ${s}`, ...l].slice(0, 50)),
    onModeChange: (m) => setLogs((l) => [`LEO mode: ${m}`, ...l].slice(0, 50)),
    onError: (e) => setLogs((l) => [`LEO error: ${String(e)}`,...l].slice(0, 50)),
    onMessage: (m: any) => {
      try {
        const role = (m?.role === 'assistant' || m?.role === 'agent') ? 'assistant' : m?.role
        const text: string | undefined = m?.text ?? m?.message ?? m?.content ?? (typeof m === 'string' ? m : undefined)
        const isFinal = m?.isFinal || m?.final || m?.type === 'assistant_message' || m?.type === 'response_completed'
        if (role === 'assistant' && text && text.trim() && (isFinal || text.length > 12)) {
          setMessages((prev) => { const next = [...prev, { speaker: 'LEO', text }]; onMessagesChange?.(next); return next })
          // Forward LEO -> LUNA as user message
          if (deviceRole === 'BOTH') {
            luna.sendUserMessage(text)
          }
        }
      } catch (err) {
        setLogs((l) => [`LEO msg-parse-error: ${String(err)}`,...l].slice(0, 50))
      }
    },
  })

  const luna = useConversation({
    volume: lunaVol,
    micMuted: true,
    overrides: sharedOverrides,
    onStatusChange: (s) => setLogs((l) => [`LUNA status: ${s}`, ...l].slice(0, 50)),
    onModeChange: (m) => setLogs((l) => [`LUNA mode: ${m}`, ...l].slice(0, 50)),
    onError: (e) => setLogs((l) => [`LUNA error: ${String(e)}`,...l].slice(0, 50)),
    onMessage: (m: any) => {
      try {
        const role = (m?.role === 'assistant' || m?.role === 'agent') ? 'assistant' : m?.role
        const text: string | undefined = m?.text ?? m?.message ?? m?.content ?? (typeof m === 'string' ? m : undefined)
        const isFinal = m?.isFinal || m?.final || m?.type === 'assistant_message' || m?.type === 'response_completed'
        if (role === 'assistant' && text && text.trim() && (isFinal || text.length > 12)) {
          setMessages((prev) => { const next = [...prev, { speaker: 'LUNA', text }]; onMessagesChange?.(next); return next })
          // Forward LUNA -> LEO as user message
          if (deviceRole === 'BOTH') {
            leo.sendUserMessage(text)
          }
        }
      } catch (err) {
        setLogs((l) => [`LUNA msg-parse-error: ${String(err)}`,...l].slice(0, 50))
      }
    },
  })

  const start = async () => {
    if (!leoId || !lunaId) {
      alert('Enter both LEO and LUNA Agent IDs.')
      return
    }
    try {
      setConnecting(true)
      if (deviceRole === 'LEO' || deviceRole === 'BOTH') {
        if (textBridge) {
          const leoUrl = await fetch(`${apiBase}/api/eleven/signed-url?agent_id=${encodeURIComponent(leoId)}`).then(r => r.ok ? r.json() : Promise.reject(new Error(`signed-url LEO ${r.status}`)))
          await leo.startSession({ signedUrl: leoUrl, connectionType: 'websocket' })
        } else {
          await navigator.mediaDevices.getUserMedia({ audio: true })
          await leo.startSession({ agentId: leoId, connectionType: 'webrtc' })
        }
      }
      if (deviceRole === 'LUNA' || deviceRole === 'BOTH') {
        if (textBridge) {
          const lunaUrl = await fetch(`${apiBase}/api/eleven/signed-url?agent_id=${encodeURIComponent(lunaId)}`).then(r => r.ok ? r.json() : Promise.reject(new Error(`signed-url LUNA ${r.status}`)))
          await luna.startSession({ signedUrl: lunaUrl, connectionType: 'websocket' })
        } else {
          await navigator.mediaDevices.getUserMedia({ audio: true })
          await luna.startSession({ agentId: lunaId, connectionType: 'webrtc' })
        }
      }
      // Share user context with both agents
      const ctx = `User: ${personaName}. Focus: ${focusTitle}. Please keep replies short, coordinate with your counterpart, and avoid medical advice.`
      if (deviceRole === 'LEO' || deviceRole === 'BOTH') { try { leo.sendContextualUpdate(ctx) } catch {} }
      if (deviceRole === 'LUNA' || deviceRole === 'BOTH') { try { luna.sendContextualUpdate(ctx) } catch {} }
      // Seed the conversation to kick off LEO -> LUNA
      if (deviceRole === 'BOTH') {
        luna.sendUserMessage(`LEO: Please start the intake conversation for ${personaName} focusing on ${focusTitle}. Keep it concise.`)
      }
    } catch (e) {
      console.error(e)
      alert('Failed to start duo session. Verify IDs and permissions.')
    } finally {
      setConnecting(false)
    }
  }

  const stop = async () => {
    try { await leo.endSession() } catch {}
    try { await luna.endSession() } catch {}
  }

  return (
    <div className="flex-1 flex flex-col">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-2">
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-semibold">LEO</span>
          <input className="input text-xs flex-1" placeholder="LEO Agent ID" value={leoId} onChange={(e) => setLeoId(e.target.value)} />
          <div className="flex items-center gap-1 text-[11px] ml-auto"><span>Vol</span><input type="range" min={0} max={1} step={0.05} value={leoVol} onChange={(e) => setLeoVol(parseFloat(e.target.value))} /></div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-semibold">LUNA</span>
          <input className="input text-xs flex-1" placeholder="LUNA Agent ID" value={lunaId} onChange={(e) => setLunaId(e.target.value)} />
          <div className="flex items-center gap-1 text-[11px] ml-auto"><span>Vol</span><input type="range" min={0} max={1} step={0.05} value={lunaVol} onChange={(e) => setLunaVol(parseFloat(e.target.value))} /></div>
        </div>
      </div>

      <div className="flex items-center gap-2 mb-2">
        <button className="btn" onClick={start} disabled={connecting}> {connecting ? 'Connecting…' : 'Start Duo'} </button>
        <button className="btn-ghost border border-slate-200 dark:border-white/10" onClick={stop}>End</button>
        <label className="text-[11px] flex items-center gap-2 ml-2">
          <input type="checkbox" checked={textBridge} onChange={(e) => setTextBridge(e.target.checked)} /> Text bridge (no mic)
        </label>
        <label className="text-[11px] flex items-center gap-2 ml-2">
          This device runs:
          <select className="input text-xs" value={deviceRole} onChange={(e) => setDeviceRole(e.target.value as any)}>
            <option value="LEO">LEO only</option>
            <option value="LUNA">LUNA only</option>
            <option value="BOTH">Both</option>
          </select>
        </label>
        <div className="ml-auto flex items-center gap-2 text-[11px]">
          {(deviceRole === 'LEO' || deviceRole === 'BOTH') && (
            <StatusPill label={`LEO ${leo.isSpeaking ? 'Speaking' : 'Listening'}`} tone={leo.isSpeaking ? 'accent' : 'idle'} pulse={leo.isSpeaking} />
          )}
          {(deviceRole === 'LUNA' || deviceRole === 'BOTH') && (
            <StatusPill label={`LUNA ${luna.isSpeaking ? 'Speaking' : 'Listening'}`} tone={luna.isSpeaking ? 'accent' : 'idle'} pulse={luna.isSpeaking} />
          )}
        </div>
      </div>

      <div className="flex-1 overflow-auto space-y-2 pr-1">
        {messages.length === 0 && (
          <div className="text-xs text-slate-500">Start the duo to hear LEO and LUNA talk to each other. Messages appear here with turn-taking.</div>
        )}
        {messages.map((m, idx) => (
          <div key={idx} className={`max-w-[88%] rounded-2xl px-3 py-2 text-sm ${m.speaker === 'LEO' ? 'bg-teal-600 text-white self-start rounded-bl-sm' : 'bg-violet-600 text-white self-end rounded-br-sm ml-auto'}`}>
            <div className="text-[11px] opacity-80 mb-0.5">{m.speaker}</div>
            <div>{m.text}</div>
          </div>
        ))}
      </div>

      <details className="mt-3">
        <summary className="text-xs text-slate-500 cursor-pointer">Debug</summary>
        <div className="text-[11px] text-slate-600 dark:text-slate-300 mt-2 space-y-1 max-h-32 overflow-auto">
          {logs.map((l, i) => <div key={i}>{l}</div>)}
        </div>
      </details>
    </div>
  )
}

function DuoTextTTSPanel({ personaName, focusTitle, onMessagesReady }: { personaName: string; focusTitle: string; onMessagesReady?: (msgs: { speaker: 'LEO' | 'LUNA'; text: string }[]) => void }) {
  const apiBase = (import.meta as any).env?.VITE_API_BASE || ''
  const [turnLimit, setTurnLimit] = useState(8)
  const defaultLeoVoice = (import.meta as any).env?.VITE_ELEVEN_LEO_VOICE_ID || ''
  const defaultLunaVoice = (import.meta as any).env?.VITE_ELEVEN_LUNA_VOICE_ID || ''
  const [leoVoice, setLeoVoice] = useState<string>(defaultLeoVoice)
  const [lunaVoice, setLunaVoice] = useState<string>(defaultLunaVoice)
  const [messages, setMessages] = useState<{ speaker: 'LEO' | 'LUNA'; text: string }[]>([])
  const [running, setRunning] = useState(false)
  const abortRef = useRef<{ aborted: boolean; audio?: HTMLAudioElement }>({ aborted: false })
  const [logs, setLogs] = useState<string[]>([])

  const runDuo = async () => {
    setRunning(true)
    setMessages([])
    abortRef.current.aborted = false
    try {
      let msgs: { speaker: 'LEO' | 'LUNA'; text: string }[] = []
      try {
        const res = await fetch(`${apiBase}/api/duo/run`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ turn_limit: turnLimit }) })
        if (!res.ok) throw new Error(`duo/run ${res.status}`)
        const data = await res.json()
        msgs = (data?.messages || [])
          .filter((m: any) => m?.speaker && m?.text)
          .map((m: any) => ({ speaker: (m.speaker === 'LEO' ? 'LEO' : 'LUNA') as 'LEO' | 'LUNA', text: String(m.text) }))
      } catch (err) {
        setLogs((l) => [`fallback: local text loop (${String(err)})`, ...l].slice(0, 50))
        msgs = buildLocalDuoMock(turnLimit, personaName, focusTitle)
      }
      setMessages(msgs)
      onMessagesReady?.(msgs)
      // Enforce two distinct voices for playback
      if (!leoVoice || !lunaVoice) {
        setLogs((l) => ["tts-skip: set both LEO and LUNA voice IDs", ...l].slice(0, 50))
        return
      }
      if (leoVoice === lunaVoice) {
        setLogs((l) => ["tts-skip: voice IDs must be different", ...l].slice(0, 50))
        return
      }
      for (const m of msgs) {
        if (abortRef.current.aborted) break
        const vid = m.speaker === 'LEO' ? leoVoice : lunaVoice
        if (!vid) continue
        try {
          const audioUrl = await synth(m.text, vid)
          if (abortRef.current.aborted) break
          await playAudio(audioUrl)
        } catch (e) {
          setLogs((l) => [`tts-error: ${String(e)}`, ...l].slice(0, 50))
        }
      }
    } catch (e) {
      setLogs((l) => [`run-error: ${String(e)}`, ...l].slice(0, 50))
    } finally {
      setRunning(false)
    }
  }

  const stop = () => {
    abortRef.current.aborted = true
    if (abortRef.current.audio) {
      try { abortRef.current.audio.pause() } catch {}
    }
  }

  async function synth(text: string, voiceId: string): Promise<string> {
    const res = await fetch(`${apiBase}/api/tts`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ text, voice_id: voiceId }) })
    if (!res.ok) throw new Error(`TTS failed (${res.status})`)
    const blob = await res.blob()
    return URL.createObjectURL(blob)
  }

  function playAudio(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const audio = new Audio(url)
      abortRef.current.audio = audio
      audio.onended = () => resolve()
      audio.onerror = () => reject(new Error('audio error'))
      audio.play().catch(reject)
    })
  }

  return (
    <div className="flex-1 flex flex-col">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mb-2">
        <label className="text-xs flex items-center gap-2">
          <span>Turns</span>
          <input type="number" min={2} max={12} className="input text-xs w-20" value={turnLimit} onChange={(e) => setTurnLimit(parseInt(e.target.value || '8'))} />
        </label>
        <input className="input text-xs" placeholder="LEO Voice ID (required for TTS)" value={leoVoice} onChange={(e) => setLeoVoice(e.target.value)} />
        <input className="input text-xs" placeholder="LUNA Voice ID (required for TTS)" value={lunaVoice} onChange={(e) => setLunaVoice(e.target.value)} />
      </div>

      <div className="flex items-center gap-2 mb-2">
        <button className="btn" onClick={runDuo} disabled={running}>{running ? 'Running…' : 'Run Duo'}</button>
        <button className="btn-ghost border border-slate-200 dark:border-white/10" onClick={stop}>Stop</button>
      </div>

      <div className="flex-1 overflow-auto space-y-2 pr-1">
        {messages.length === 0 && (
          <div className="text-xs text-slate-500">Click Run Duo to generate a LEO ↔ LUNA text conversation. If you provide voice IDs, it will play each turn via TTS.</div>
        )}
        {messages.map((m, idx) => (
          <div key={idx} className={`max-w-[88%] rounded-2xl px-3 py-2 text-sm ${m.speaker === 'LEO' ? 'bg-teal-600 text-white self-start rounded-bl-sm' : 'bg-violet-600 text-white self-end rounded-br-sm ml-auto'}`}>
            <div className="text-[11px] opacity-80 mb-0.5">{m.speaker}</div>
            <div>{m.text}</div>
          </div>
        ))}
      </div>

      <details className="mt-3">
        <summary className="text-xs text-slate-500 cursor-pointer">Debug</summary>
        <div className="text-[11px] text-slate-600 dark:text-slate-300 mt-2 space-y-1 max-h-32 overflow-auto">
          {logs.map((l, i) => <div key={i}>{l}</div>)}
        </div>
      </details>
    </div>
  )
}
