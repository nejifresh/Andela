export function MetricCard({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-lg border border-line bg-white p-4">
      <div className="text-xs font-medium uppercase tracking-wide text-steel">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-ink">{value}</div>
      {hint ? <div className="mt-1 text-sm text-steel">{hint}</div> : null}
    </div>
  );
}
