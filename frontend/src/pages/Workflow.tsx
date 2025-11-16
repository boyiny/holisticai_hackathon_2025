import { ProgressiveBlurSlider } from '@/components/ui/progressive-blur-slider';

export default function Workflow() {
  return (
    <div className="card p-6">
      <div className="mb-4 font-display font-bold text-xl">Orchestration</div>

      <ProgressiveBlurSlider />

      <div className="mt-4 text-sm text-slate-500">
        Start → Intake → PlanDraft → PlanReview → Audit → Revision → FinalPlan → Scheduling → FinalSummary.
        The steps scroll continuously with a soft fade at the edges to highlight progress through the workflow.
      </div>
    </div>
  );
}
