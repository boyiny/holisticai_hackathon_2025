import { useEffect, useMemo, useRef } from 'react'

export type AgentRole = 'LEO' | 'LUNA'

export type StepId =
  | 'Start'
  | 'Intake'
  | 'PlanDraft'
  | 'PlanReview'
  | 'Audit'
  | 'Revision'
  | 'FinalPlan'
  | 'Scheduling'
  | 'FinalSummary'

export type StepStatus = 'pending' | 'running' | 'success' | 'error'

export interface WorkflowStepState {
  id: StepId
  title: string
  description: string
  responsibleAgent: AgentRole
  status: StepStatus
  startedAt?: string
  finishedAt?: string
  errorMessage?: string
}

export interface WorkflowTimelineProps {
  steps: WorkflowStepState[]
  currentStepId: StepId
  onStepClick?: (stepId: StepId) => void
}

export function WorkflowTimeline({ steps, currentStepId, onStepClick }: WorkflowTimelineProps) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const activeIndex = useMemo(() => steps.findIndex(s => s.id === currentStepId), [steps, currentStepId])

  useEffect(() => {
    // Smooth scroll active into view
    const el = containerRef.current?.querySelector(`[data-step='${currentStepId}']`) as HTMLElement | null
    if (el && containerRef.current) {
      const parent = containerRef.current
      const left = el.offsetLeft - parent.clientWidth / 3
      parent.scrollTo({ left, behavior: 'smooth' })
    }
  }, [currentStepId])

  return (
    <div className="relative">
      {/* left fade */}
      <div className="pointer-events-none absolute inset-y-0 left-0 w-10 bg-gradient-to-r from-white dark:from-slate-900 to-transparent z-10" />
      {/* right fade */}
      <div className="pointer-events-none absolute inset-y-0 right-0 w-10 bg-gradient-to-l from-white dark:from-slate-900 to-transparent z-10" />

      <div ref={containerRef} className="overflow-x-auto no-scrollbar">
        <div className="flex items-stretch gap-3 pr-6">
          {steps.map((s, i) => (
            <StepCard
              key={s.id}
              step={s}
              index={i}
              isActive={i === activeIndex}
              isDone={i < activeIndex}
              onClick={() => onStepClick?.(s.id)}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

function StepCard({ step, index, isActive, isDone, onClick }: { step: WorkflowStepState; index: number; isActive: boolean; isDone: boolean; onClick?: () => void }) {
  const statusChip = (
    <span
      className={
        'text-[10px] px-2 py-0.5 rounded-full ' +
        (step.status === 'pending'
          ? 'bg-slate-100 dark:bg-white/10 text-slate-600 dark:text-white/70'
          : step.status === 'running'
          ? 'bg-blue-100 text-blue-700 animate-pulse'
          : step.status === 'success'
          ? 'bg-green-100 text-green-700'
          : 'bg-red-100 text-red-700')
      }
    >
      {step.status}
    </span>
  )

  const badge = (
    <span
      className={
        'text-[10px] px-2 py-0.5 rounded-full font-medium ' +
        (step.responsibleAgent === 'LEO' ? 'bg-teal-100 text-teal-700' : 'bg-violet-100 text-violet-700')
      }
    >
      {step.responsibleAgent}
    </span>
  )

  return (
    <button
      data-step={step.id}
      onClick={onClick}
      className={
        'min-w-[220px] text-left rounded-xl border p-3 transition ' +
        (isActive ? 'border-violet-400 shadow-sm' : isDone ? 'border-slate-200 dark:border-white/10 opacity-90' : 'border-slate-200 dark:border-white/10 opacity-80')
      }
    >
      <div className="flex items-center justify-between mb-2">
        <div className="text-xs text-slate-500">{index + 1}</div>
        {badge}
      </div>
      <div className={"font-semibold text-sm " + (isActive ? 'text-violet-700 dark:text-violet-300' : '')}>{step.title}</div>
      <div className="text-xs text-slate-600 dark:text-slate-300 mt-1 line-clamp-3">{step.description}</div>
      <div className="mt-2">{statusChip}</div>
    </button>
  )
}

