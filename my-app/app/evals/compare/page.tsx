import { listEvalReports, loadEvalReport } from "@/lib/evalData";
import { EvalReport } from "@/lib/evalTypes";

import EvalCompareDashboard from "@/components/ui/eval-dashboard";

type Props = {
  searchParams: Promise<{
    left?: string;
    right?: string;
  }>;
};

function pickDefaultIds(ids: string[], leftParam?: string, rightParam?: string) {
  const [first = "", second = first] = ids;
  const left = leftParam && ids.includes(leftParam) ? leftParam : first;
  const right = rightParam && ids.includes(rightParam) ? rightParam : second;
  return { left, right };
}

export default async function EvalComparePage({ searchParams }: Props) {
  const resolvedSearchParams = await searchParams;

  const evals = await listEvalReports();
  if (!evals.length) {
    return (
      <div className="mx-auto max-w-5xl px-6 py-16">
        <h1 className="text-3xl font-semibold">Eval Comparison</h1>
        <p className="mt-4 text-lg text-muted-foreground">
          No eval reports were found under <code>data/evals</code>. Generate reports first, then refresh this page.
        </p>
      </div>
    );
  }

  const ids = evals.map((item) => item.id);
  const { left, right } = pickDefaultIds(
    ids,
    resolvedSearchParams?.left,
    resolvedSearchParams?.right
  );

  const [leftReport, rightReport] = await Promise.all([
    left ? loadEvalReport(left) : (null as EvalReport | null),
    right ? loadEvalReport(right) : (null as EvalReport | null),
  ]);

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <h1 className="text-3xl font-semibold">Eval Comparison</h1>
      <p className="mt-2 text-muted-foreground">
        Compare two evaluation runs side-by-side. Metrics are derived from the JSON reports generated under <code>data/evals</code>.
      </p>
      <EvalCompareDashboard
        evals={evals}
        initialLeftId={left}
        initialRightId={right}
        initialLeftReport={leftReport}
        initialRightReport={rightReport}
      />
    </div>
  );
}

