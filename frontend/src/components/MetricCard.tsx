type Props = { title: string; value: string | number | null; subtitle?: string }
export default function MetricCard({ title, value, subtitle }: Props) {
  return (
    <div className="card p-4">
      <div className="text-sm text-slate-500">{title}</div>
      <div className="text-2xl font-semibold mt-1">{value ?? '—'}</div>
      {subtitle && <div className="text-xs text-slate-500 mt-1">{subtitle}</div>}
    </div>
  )
}

