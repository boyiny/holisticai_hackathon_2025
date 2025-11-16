export type RunListItem = {
  id: string
  timestamp: string
  user: string
  plan_score: number | null
  status: 'success' | 'warning' | 'failed'
}

export type OverviewMetrics = {
  avg_latency_s: number | null
  avg_tokens: number | null
  plan_consistency_score: number | null
  scientific_validity_coverage_pct: number | null
  runs_count: number
}

export type RunDetail = {
  id: string
  summary: any
  telemetry: { latency_s: number }[]
  validations: { claim: any; validity: string; confidence: number }[]
  conversation: string
  bookings: any[]
}

