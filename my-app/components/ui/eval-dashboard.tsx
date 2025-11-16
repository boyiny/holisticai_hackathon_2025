"use client";

import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { EvalListItem, EvalReport, EvalSummary } from "@/lib/evalTypes";

type Props = {
  evals: EvalListItem[];
  initialLeftId: string;
  initialRightId: string;
  initialLeftReport: EvalReport | null;
  initialRightReport: EvalReport | null;
};

type MetricDef = {
  key: keyof EvalSummary;
  label: string;
};

const METRICS: MetricDef[] = [
  { key: "avg_collaboration", label: "Collaboration" },
  { key: "avg_alignment_a", label: "Alignment A" },
  { key: "avg_alignment_b", label: "Alignment B" },
  { key: "avg_reasoning_depth", label: "Reasoning Depth" },
  { key: "avg_consistency", label: "Consistency" },
];

const SCORECARD_ROWS: MetricDef[] = [
  ...METRICS,
  { key: "num_pairs", label: "Scenario Pairs" },
];

const leftColor = "#f43f5e";
const rightColor = "#2563eb";

export default function EvalCompareDashboard({
  evals,
  initialLeftId,
  initialRightId,
  initialLeftReport,
  initialRightReport,
}: Props) {
  const [leftId, setLeftId] = useState(initialLeftId);
  const [rightId, setRightId] = useState(initialRightId);
  const [leftReport, setLeftReport] = useState<EvalReport | null>(initialLeftReport);
  const [rightReport, setRightReport] = useState<EvalReport | null>(initialRightReport);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const summariesReady = leftReport?.summary && rightReport?.summary;

  async function fetchReport(id: string) {
    const res = await fetch(`/api/evals/${id}`);
    if (!res.ok) {
      throw new Error(`Failed to load ${id}`);
    }
    return (await res.json()) as EvalReport;
  }

  async function handleSelect(side: "left" | "right", id: string) {
    if (side === "left" && id === leftId && leftReport) return;
    if (side === "right" && id === rightId && rightReport) return;
    setLoading(true);
    setError(null);
    try {
      const report = await fetchReport(id);
      if (side === "left") {
        setLeftId(id);
        setLeftReport(report);
      } else {
        setRightId(id);
        setRightReport(report);
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  const radarData = useMemo(() => {
    if (!summariesReady) return [];
    return METRICS.map((metric) => ({
      metric: metric.label,
      left: leftReport?.summary?.[metric.key] ?? 0,
      right: rightReport?.summary?.[metric.key] ?? 0,
    }));
  }, [summariesReady, leftReport, rightReport]);

  const barData = radarData;

  const scorecardRows = useMemo(() => {
    return SCORECARD_ROWS.map((metric) => {
      const leftValue = leftReport?.summary?.[metric.key] ?? 0;
      const rightValue = rightReport?.summary?.[metric.key] ?? 0;
      return {
        label: metric.label,
        leftValue,
        rightValue,
        diff: rightValue - leftValue,
      };
    });
  }, [leftReport, rightReport]);

  return (
    <div className="mt-8 space-y-8">
      <div className="flex flex-wrap gap-4 rounded-xl border border-border/60 bg-muted/20 p-4">
        <Selector label="Evaluation A" value={leftId} evals={evals} onChange={(id) => handleSelect("left", id)} />
        <Selector label="Evaluation B" value={rightId} evals={evals} onChange={(id) => handleSelect("right", id)} />
        {loading && <span className="text-sm text-muted-foreground">Loading…</span>}
      </div>
      <MetaStrip leftSummary={leftReport?.summary ?? null} rightSummary={rightReport?.summary ?? null} />
      {error && (
        <div className="rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-destructive">
          {error}
        </div>
      )}
      {summariesReady ? (
        <>
          <div className="grid gap-6 lg:grid-cols-2">
            <ChartCard title="Summary Metrics (Radar)">
              <ResponsiveContainer width="100%" height={320}>
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="metric" />
                  <Radar name="Eval A" dataKey="left" stroke={leftColor} fill={leftColor} fillOpacity={0.25} />
                  <Radar name="Eval B" dataKey="right" stroke={rightColor} fill={rightColor} fillOpacity={0.25} />
                  <Legend />
                </RadarChart>
              </ResponsiveContainer>
            </ChartCard>
            <ChartCard title="Summary Metrics (Bar)">
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="metric" />
                  <YAxis domain={[0, 10]} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="left" name="Eval A" fill={leftColor} radius={[4, 4, 0, 0]} />
                  <Bar dataKey="right" name="Eval B" fill={rightColor} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>
          <Scorecard rows={scorecardRows} />
          <PairNotes leftReport={leftReport} rightReport={rightReport} />
        </>
      ) : (
        <div className="rounded-lg border border-dashed border-muted-foreground/40 p-8 text-center text-muted-foreground">
          Select two evals with comparable data to view charts.
        </div>
      )}
    </div>
  );
}

type SelectorProps = {
  label: string;
  value: string;
  evals: EvalListItem[];
  onChange: (id: string) => void;
};

function Selector({ label, value, evals, onChange }: SelectorProps) {
  return (
    <label className="flex flex-col text-sm font-medium text-foreground">
      {label}
      <select
        className="mt-1 rounded-md border border-border bg-background px-3 py-2 text-base"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {evals.map((item) => (
          <option key={item.id} value={item.id}>
            {item.project} · {item.id.replace("conversation_eval_", "")}
          </option>
        ))}
      </select>
    </label>
  );
}

type ChartCardProps = {
  title: string;
  children: React.ReactNode;
};

function ChartCard({ title, children }: ChartCardProps) {
  return (
    <div className="rounded-xl border border-border/60 bg-background shadow-sm">
      <div className="border-b border-border/50 px-4 py-4">
        <h2 className="text-lg font-semibold">{title}</h2>
      </div>
      <div className="px-4 py-4">{children}</div>
    </div>
  );
}

type ScorecardRow = {
  label: string;
  leftValue: number;
  rightValue: number;
  diff: number;
};

function Scorecard({ rows }: { rows: ScorecardRow[] }) {
  return (
    <div className="rounded-xl border border-border/60 bg-background shadow-sm">
      <div className="border-b border-border/50 px-6 py-4">
        <h2 className="text-lg font-semibold">Scorecard</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-border/60">
          <thead className="bg-muted/40 text-left text-sm text-muted-foreground">
            <tr>
              <th className="px-6 py-3 font-medium">Metric</th>
              <th className="px-6 py-3 font-medium">Eval A</th>
              <th className="px-6 py-3 font-medium">Eval B</th>
              <th className="px-6 py-3 font-medium">Diff (B − A)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/60 text-sm">
            {rows.map((row) => (
              <tr key={row.label}>
                <td className="px-6 py-3 font-medium">{row.label}</td>
                <td className="px-6 py-3">{formatValue(row.leftValue)}</td>
                <td className="px-6 py-3">{formatValue(row.rightValue)}</td>
                <td className="px-6 py-3">
                  <DiffBadge value={row.diff} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function DiffBadge({ value }: { value: number }) {
  const sign = value === 0 ? "" : value > 0 ? "+" : "";
  const tone = value > 0 ? "text-emerald-600 bg-emerald-50" : value < 0 ? "text-rose-600 bg-rose-50" : "text-muted-foreground bg-muted/30";
  return <span className={`rounded-full px-2 py-1 text-xs font-semibold ${tone}`}>{`${sign}${value.toFixed(2)}`}</span>;
}

function formatValue(value: number) {
  if (Number.isInteger(value)) return value.toLocaleString();
  return value.toFixed(2);
}

function PairNotes({ leftReport, rightReport }: { leftReport: EvalReport | null; rightReport: EvalReport | null }) {
  const panels = [
    { label: "Eval A Highlights", report: leftReport },
    { label: "Eval B Highlights", report: rightReport },
  ];

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {panels.map(({ label, report }) => (
        <div key={label} className="rounded-xl border border-border/60 bg-background shadow-sm">
          <div className="border-b border-border/50 px-6 py-4">
            <h3 className="text-lg font-semibold">{label}</h3>
            {report?.summary?.project && <p className="text-sm text-muted-foreground">{report.summary.project}</p>}
          </div>
          <div className="space-y-4 px-6 py-4 text-sm">
            {report?.pairs?.length ? (
              report.pairs.map((pair, index) => (
                <div key={`${pair.scenario_id}-${index}`} className="rounded-lg border border-border/50 bg-muted/10 p-3">
                  <p className="text-xs uppercase text-muted-foreground">Scenario: {pair.scenario_id}</p>
                  <p className="mt-1 font-medium">Recommendation: {pair.recommendation.replace("conversation_", "conv ")}</p>
                  <p className="mt-2 text-muted-foreground">{pair.notes}</p>
                </div>
              ))
            ) : (
              <p className="text-muted-foreground">No pair details available.</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function MetaStrip({ leftSummary, rightSummary }: { leftSummary: EvalSummary | null; rightSummary: EvalSummary | null }) {
  const items = [
    { label: "Eval A", summary: leftSummary, color: leftColor },
    { label: "Eval B", summary: rightSummary, color: rightColor },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {items.map(({ label, summary, color }) => (
        <div key={label} className="flex flex-col rounded-xl border border-border/60 bg-background/80 p-4 shadow-sm">
          <div className="flex items-center gap-2 text-sm font-semibold" style={{ color }}>
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
            {label}
          </div>
          {summary ? (
            <>
              <p className="text-lg font-semibold">{summary.project}</p>
              <div className="mt-2 text-sm text-muted-foreground">
                <p>Judge: {summary.judge_model}</p>
                <p>Pairs: {summary.num_pairs}</p>
              </div>
            </>
          ) : (
            <p className="text-sm text-muted-foreground">Select an evaluation</p>
          )}
        </div>
      ))}
    </div>
  );
}

