import { InfiniteSlider } from '@/components/ui/infinite-slider';
import { ProgressiveBlur } from '@/components/ui/progressive-blur';

const WORKFLOW_STEPS = [
  'Start',
  'Intake',
  'PlanDraft',
  'PlanReview',
  'Audit',
  'Revision',
  'FinalPlan',
  'Scheduling',
  'FinalSummary',
];

export function ProgressiveBlurSlider() {
  return (
    <div className="relative h-[220px] w-full overflow-hidden">
      <div className="relative h-full">
        <InfiniteSlider className="flex h-full w-full items-center">
          {WORKFLOW_STEPS.map((step) => (
            <div
              key={step}
              className="w-32 text-center text-3xl font-[450] text-slate-900"
            >
              {step}
            </div>
          ))}
        </InfiniteSlider>
      </div>

      <ProgressiveBlur
        className="pointer-events-none absolute top-0 left-0 z-10 h-full w-[200px]"
        direction="left"
        blurIntensity={1}
      />

      <ProgressiveBlur
        className="pointer-events-none absolute top-0 right-0 z-10 h-full w-[200px]"
        direction="right"
        blurIntensity={1}
      />
    </div>
  );
}


