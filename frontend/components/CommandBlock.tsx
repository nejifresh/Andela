import { Terminal } from "lucide-react";

export function CommandBlock({ title, command }: { title: string; command: string | null }) {
  return (
    <section className="rounded-lg border border-line bg-white p-4">
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-ink">
        <Terminal size={16} /> {title}
      </div>
      <pre className="command rounded-md border border-slate-200 bg-slate-950 p-3 text-sm text-slate-100">
        {command || "Not applicable for this recommendation."}
      </pre>
    </section>
  );
}
