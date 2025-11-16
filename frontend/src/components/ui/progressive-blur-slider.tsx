export function ProgressiveBlurSlider() {
  const steps = ['Start','Intake','PlanDraft','PlanReview','Audit','Revision','FinalPlan','Scheduling','FinalSummary']
  return (
    <div className="relative overflow-hidden">
      <div className="pointer-events-none absolute inset-y-0 left-0 w-12 bg-gradient-to-r from-white dark:from-black to-transparent" />
      <div className="pointer-events-none absolute inset-y-0 right-0 w-12 bg-gradient-to-l from-white dark:from-black to-transparent" />
      <div className="flex gap-3 overflow-x-auto no-scrollbar py-1 pr-6">
        {steps.map((s, i) => (
          <div key={s} className="shrink-0 px-3 py-2 rounded-full border border-slate-200 dark:border-white/10 bg-white dark:bg-black text-sm">
            {s}
          </div>
        ))}
      </div>
    </div>
  )
}

