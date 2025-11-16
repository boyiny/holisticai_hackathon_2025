<!-- 12d483fb-0c56-4fd9-9011-834f3d2ffc54 e721df43-bd7f-4c3b-91c6-716d94c94436 -->
## Eval Comparison Dashboard Plan (Next.js frontend)

### Goals

- **Goal 1**: Surface existing eval JSON reports (e.g. `data/evals/conversation_eval_20251116_124355.json`) in the Next.js app so they can be selected and compared.
- **Goal 2**: Build a visual dashboard that approximates the LangSmith "Compare Evaluations" UI: summary charts (radar + bar) and a scorecard-style table highlighting metric differences between two eval runs.

### Data & Types

- **Eval report shape**
- Base the frontend types on the existing JSON schema:
  - `EvalPair`: mirrors a single entry from `pairs[]` (scenario_id, run IDs, metrics, notes, judge_model, summary_model, created_at).
  - `EvalSummary`: mirrors `summary` (avg_collaboration, avg_alignment_a, avg_alignment_b, avg_reasoning_depth, avg_consistency, num_pairs, project, judge_model, summary_model).
  - `EvalReport`: `{ pairs: EvalPair[]; summary: EvalSummary; group_count: number; min_group_size: number; }`.
- Define TypeScript types in a shared file under the Next app, e.g. `my-app/lib/evalTypes.ts`.
- **File location & loading strategy**
- Copy or sync relevant eval JSONs from the repo root `data/evals/` into a directory the Next app can read at runtime, e.g. `my-app/evals/` or keep them at the root and resolve via `path.resolve(process.cwd(), "..", "data", "evals")` on the server.
- Implement a small server-side loader in `my-app/lib/evalData.ts` using Node `fs`:
  - `listEvalReports(): Promise<{ id: string; filename: string; createdAt?: string; project: string; }[]>` — scan the eval directory for `conversation_eval_*.json`, parse their `summary.project` and maybe `summary.createdAt` if we add it.
  - `loadEvalReport(idOrFilename: string): Promise<EvalReport>` — read and JSON-parse a single report.
- Keep this logic server-only (no direct `fs` inside client components).

### Routing & Page Structure

- **New route**
- Add a new page under the Next.js app, e.g. `my-app/app/evals/compare/page.tsx`.
- Make this a **server component** that:
  - Calls `listEvalReports()` to get available eval runs.
  - Optionally preloads one or two default reports (e.g. the two most recent) via `loadEvalReport`.
  - Passes the list and default report data into a client component `EvalCompareDashboard`.
- **URL model (optional enhancement)**
- Support query params like `/evals/compare?left=<idA>&right=<idB>`.
- Read these in the server component and choose which evals to preload; this will allow deep-linking specific comparisons later.

### UI Components

- **Layout shell**
- In `my-app/components/ui/eval-dashboard.tsx` (client component), build a layout similar to the attached screenshot:
  - Top bar with two selectors:
  - Left dropdown for Evaluation A.
  - Right dropdown for Evaluation B.
  - Each option label could be `project / timestamp` or `project / filename`.
  - Main content split vertically into:
  - Summary Metrics section (charts).
  - Scorecard section (table) below.
- **Selectors**
- Use controlled `select` elements or a small UI library component to choose which eval report is mapped to A and B.
- When the user changes selection:
  - Trigger a client-side fetch to a simple API route (see below) or use the preloaded reports if already present.
  - Update state for `leftEval` and `rightEval` and recompute derived chart data.

### Data Access from the Client

- **API routes**
- Create API handlers under `my-app/app/api/evals/route.ts` and `my-app/app/api/evals/[id]/route.ts` (App Router style):
  - `GET /api/evals` → returns the list from `listEvalReports()`.
  - `GET /api/evals/[id]` → returns a single `EvalReport` by id/filename.
- The client dashboard can:
  - Use `useEffect` + `fetch` to load evals on selection change, or
  - Use SWR/React Query for caching if you prefer (optional given hackathon scope).

### Charts & Visualizations

- **Charting library choice**
- Add a lightweight charting library (e.g. `recharts` or `react-chartjs-2`) to the Next app.
- Wrap the charts in a client-only component (charts must not run in a pure server component because they depend on the DOM).
- **Summary Metrics panel**
- **Radar chart**: emulate the “Summary Metrics” radar by plotting for each eval:
  - axes: `avg_collaboration`, `avg_alignment_a`, `avg_alignment_b`, `avg_reasoning_depth`, `avg_consistency`.
  - series A (left eval) vs series B (right eval) in different colors.
- **Bar chart**: side-by-side bars for the same metrics, plus `num_pairs` if desired:
  - x-axis: metric names.
  - y-axis: scores.
  - Each group: bar for eval A and bar for eval B.
- **Scorecard table**
- Below the charts, build a table similar to the screenshot:
  - Columns: Metric name, Eval A value, Eval B value, Diff (B − A) highlighted.
  - Rows for:
  - Collaboration
  - Alignment A / Alignment B (show as two rows or unify into “alignment” with labels per eval).
  - Reasoning depth
  - Consistency
  - Num pairs
  - Format diffs with green/red badges depending on whether “higher is better” for that metric.
- Include textual context drawn from the `pairs` array:
  - For example, show the judge `notes` for each pair in an expandable section or tooltip.

### Comparisons & Aggregations

- **Per-eval aggregation**
- Use each eval’s `summary` directly for charts and scorecard A/B values.
- Additionally, compute simple stats over `pairs` if useful (e.g. min/max consistency, count of times A vs B chosen as `recommendation`).
- **Difference computation**
- In the dashboard component, derive a `diff` object:
  - `diff.collaboration = summaryB.avg_collaboration - summaryA.avg_collaboration`, etc.
- Use this for the diff column and for optional annotations (e.g. “Eval B improves avg_consistency by +1.0 over Eval A”).

### Styling & UX

- **Styling**
- Reuse the existing Tailwind setup in `my-app` (`globals.css`, `layout.tsx`) for spacing, typography, and colors.
- Mimic the screenshot layout:
  - Cards with subtle borders and rounded corners for the chart area and scorecard.
  - Legend markers for A vs B colors.
- **Empty / error states**
- If an eval has no `pairs` (e.g., `pairs: []`), show an inline message: “No comparable scenarios found for this eval” and disable diff charts.
- Handle fetch errors gracefully with a small inline error banner.

### Validation & Demo

- **Local testing flow**
- Copy at least two eval JSONs (like `conversation_eval_20251116_113709.json` and `conversation_eval_20251116_124355.json`) into the configured evals directory, with IDs like `evalA`, `evalB` or using their filenames.
- Verify:
  - The compare page loads and lists both evals in the selectors.
  - Charts update when you switch selections.
  - Scorecard values match the underlying JSON (spot-check a few fields).
- Optionally, add a small “Debug” section showing the raw summaries for A and B to aid future troubleshooting.

### To-dos

- [ ] Define TypeScript types for eval reports and implement server-side loaders (listEvalReports, loadEvalReport) that read conversation eval JSON from disk.
- [ ] Add Next.js API routes for listing eval reports and fetching a single report by id, delegating to the loader functions.
- [ ] Create the /evals/compare page and EvalCompareDashboard client component with selectors, radar/bar charts, and a scorecard table comparing two eval summaries.
- [ ] Polish dashboard styling and UX to roughly match the LangSmith compare-evaluations view, including legends, diff badges, and empty-state handling.
- [ ] Wire in at least two real eval JSON reports, validate that metrics and diffs match the source data, and adjust any chart mappings or labels as needed.