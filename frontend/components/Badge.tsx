const styles: Record<string, string> = {
  HIGH: "border-danger/20 bg-red-50 text-danger",
  MEDIUM: "border-warn/20 bg-amber-50 text-warn",
  LOW: "border-safe/20 bg-emerald-50 text-safe",
  DRAFT: "border-slate-200 bg-slate-50 text-slate-700",
  APPROVED: "border-safe/20 bg-emerald-50 text-safe",
  REJECTED: "border-danger/20 bg-red-50 text-danger",
  SIMULATED_EXECUTION: "border-blue-200 bg-blue-50 text-blue-700"
};

export function Badge({ value }: { value: string }) {
  return (
    <span className={`inline-flex items-center rounded-md border px-2 py-1 text-xs font-medium ${styles[value] || "border-slate-200 bg-white text-slate-700"}`}>
      {value.replaceAll("_", " ")}
    </span>
  );
}
