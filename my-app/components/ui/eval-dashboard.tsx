"use client";

import { useMemo, useState } from "react";
import {
  Area,
  AreaChart,
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

import { ChaosReport, ChaosSummary } from "@/lib/chaosTypes";
import { EvalListItem, EvalReport, EvalSummary } from "@/lib/evalTypes";

type Props = {
  evals: EvalListItem[];
  initialLeftId: string;
  initialRightId: string;
  initialLeftReport: EvalReport | null;
  initialRightReport: EvalReport | null;
  chaosReports: ChaosReport[];
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
const chaosPrimary = "#7c3aed";

type TabKey = "evals" | "chaos";

export default function EvalDashboard({
  evals,
  initialLeftId,
  initialRightId,
  initialLeftReport,
  initialRightReport,
  chaosReports,
}: Props) {
  const [tab, setTab] = useState<TabKey>("evals");

  return (
    <div className="mt-8 space-y-8">
      <div className="flex gap-4 rounded-xl border border-border/60 bg-muted/10 p-2 text-sm font-semibold">
        <button
          className={`flex-1 rounded-lg px-4 py-2 ${tab === "evals" ? "bg-background text-foreground shadow-sm" : "text-muted-foreground"}`}
          onClick={() => setTab("evals")}
        >
          Eval Comparison
        </button>
        <button
          className={`flex-1 rounded-lg px-4 py-2 ${tab === "chaos" ? "bg-background text-foreground shadow-sm" : "text-muted-foreground"}`}
          onClick={() => setTab("chaos")}
        >
          Chaos Tests
        </button>
      </div>
      {tab === "evals" ? (
        <EvalComparePanel
          evals={evals}
          initialLeftId={initialLeftId}
          initialRightId={initialRightId}
          initialLeftReport={initialLeftReport}
          initialRightReport={initialRightReport}
        />
      ) : (
        <ChaosDashboard reports={chaosReports} />
      )}
    </div>
  );
}

type ComparePanelProps = {
  evals: EvalListItem[];
  initialLeftId: string;
  initialRightId: string;
  initialLeftReport: EvalReport | null;
  initialRightReport: EvalReport | null;
};

function EvalComparePanel({
  evals,
  initialLeftId,
  initialRightId,
  initialLeftReport,
  initialRightReport,
}: ComparePanelProps) {
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

type ChaosDashboardProps = {
  reports: ChaosReport[];
};

function ChaosDashboard({ reports }: ChaosDashboardProps) {
  if (!reports.length) {
    return (
      <div className="rounded-lg border border-dashed border-muted-foreground/40 p-8 text-center text-muted-foreground">
        No chaos test reports found under <code>data/tests</code>.
      </div>
    );
  }

  const chartData = reports.map((report) => ({
    scenario: humanizeScenario(report.summary.scenario),
    successRate: +(report.summary.success_rate * 100).toFixed(1),
    errorRate: +(((report.summary.error_count || 0) / Math.max(1, report.summary.num_runs)) * 100).toFixed(1),
    avgLatency: report.summary.avg_latency_ms,
    p95Latency: report.summary.p95_latency_ms,
  }));

  return (
    <div className="space-y-8">
      <div className="grid gap-6 lg:grid-cols-3">
        {reports.map((report) => (
          <ChaosCard key={report.summary.scenario} report={report} />
        ))}
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <ChartCard title="Latency per Scenario (ms)">
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="scenario" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="avgLatency" name="Avg Latency" fill={chaosPrimary} />
              <Bar dataKey="p95Latency" name="p95 Latency" fill="#94a3b8" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Success vs Error Rate">
          <ResponsiveContainer width="100%" height={320}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="scenario" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="successRate" name="Success %" stroke={chaosPrimary} fill={`${chaosPrimary}33`} />
              <Area type="monotone" dataKey="errorRate" name="Error %" stroke="#f97316" fill="#f9731633" />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      <ChaosRunsTable reports={reports} />
    </div>
  );
}

function ChaosCard({ report }: { report: ChaosReport }) {
  const { summary, chaos_config } = report;
  return (
    <div className="rounded-2xl border border-border/60 bg-gradient-to-br from-background to-muted/30 p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Scenario</p>
          <h3 className="text-xl font-bold">{humanizeScenario(summary.scenario)}</h3>
        </div>
        <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
          {(summary.success_rate * 100).toFixed(1)}% success
        </span>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div>
          <p className="text-muted-foreground">Avg Latency</p>
          <p className="text-lg font-semibold">{summary.avg_latency_ms.toLocaleString()} ms</p>
        </div>
        <div>
          <p className="text-muted-foreground">p95 Latency</p>
          <p className="text-lg font-semibold">{summary.p95_latency_ms.toLocaleString()} ms</p>
        </div>
        <div>
          <p className="text-muted-foreground">Errors</p>
          <p className="text-lg font-semibold">{summary.error_count}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Concurrency</p>
          <p className="text-lg font-semibold">{summary.concurrency}</p>
        </div>
      </div>
      <div className="mt-4 rounded-lg border border-border/60 bg-background/70 p-3 text-xs text-muted-foreground">
        <p className="font-semibold text-foreground">Chaos Config</p>
        <div className="mt-1 grid grid-cols-2 gap-1">
          <span>Jitter: {chaos_config.jitter_min_ms}–{chaos_config.jitter_max_ms} ms</span>
          <span>Network fail: {(chaos_config.network_fail_prob * 100).toFixed(0)}%</span>
          <span>Tool fail: {(chaos_config.tool_fail_prob * 100).toFixed(0)}%</span>
          <span>LLM bad output: {(chaos_config.llm_bad_output_prob * 100).toFixed(0)}%</span>
        </div>
      </div>
    </div>
  );
}

function ChaosRunsTable({ reports }: { reports: ChaosReport[] }) {
  const rows = reports.flatMap((report) =>
    (report.runs || []).map((run, index) => ({
      scenario: humanizeScenario(report.summary.scenario),
      run_id: run.run_id,
      success: run.success,
      latency: run.latency_ms,
      errors: run.errors?.length ?? 0,
      key: `${report.summary.scenario}-${run.run_id}-${index}`,
    })),
  );

  if (!rows.length) {
    return null;
  }

  return (
    <div className="rounded-xl border border-border/60 bg-background shadow-sm">
      <div className="border-b border-border/50 px-6 py-4">
        <h2 className="text-lg font-semibold">Recent Chaos Runs</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-border/60 text-sm">
          <thead className="bg-muted/40 text-left text-muted-foreground">
            <tr>
              <th className="px-6 py-3 font-medium">Scenario</th>
              <th className="px-6 py-3 font-medium">Run ID</th>
              <th className="px-6 py-3 font-medium">Latency (ms)</th>
              <th className="px-6 py-3 font-medium">Status</th>
              <th className="px-6 py-3 font-medium">Errors</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/60">
            {rows.map((row) => (
              <tr key={row.key}>
                <td className="px-6 py-3 font-medium">{row.scenario}</td>
                <td className="px-6 py-3 text-muted-foreground">{row.run_id}</td>
                <td className="px-6 py-3">{row.latency?.toLocaleString() ?? "—"}</td>
                <td className="px-6 py-3">
                  <span className={`rounded-full px-2 py-1 text-xs font-semibold ${row.success ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"}`}>
                    {row.success ? "Success" : "Failed"}
                  </span>
                </td>
                <td className="px-6 py-3">{row.errors}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function humanizeScenario(name: string) {
  return name
    .replace(/_/g, " ")
    .split(" ")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

