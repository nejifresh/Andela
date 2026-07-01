"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Check, Play, X } from "lucide-react";
import { apiGet, apiPost, Recommendation, RemediationPack } from "@/lib/api";
import { Badge } from "@/components/Badge";
import { CommandBlock } from "@/components/CommandBlock";
import { MetricCard } from "@/components/MetricCard";

export default function RecommendationDetail({ params }: { params: Promise<{ id: string }> }) {
  const [id, setId] = useState<string>("");
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [pack, setPack] = useState<RemediationPack | null>(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    params.then((resolved) => setId(resolved.id));
  }, [params]);

  async function refresh(currentId = id) {
    if (!currentId) return;
    const [rec, remediation] = await Promise.all([
      apiGet<Recommendation>(`/api/recommendations/${currentId}`),
      apiGet<RemediationPack>(`/api/recommendations/${currentId}/remediation-pack`)
    ]);
    setRecommendation(rec);
    setPack(remediation);
  }

  useEffect(() => {
    if (id) refresh(id).catch((error) => setMessage(error instanceof Error ? error.message : "Could not load recommendation."));
  }, [id]);

  async function transition(action: "approve" | "reject" | "simulate") {
    if (!id) return;
    try {
      await apiPost<Recommendation>(`/api/recommendations/${id}/${action}`);
      setMessage(`${action} completed.`);
      await refresh(id);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Workflow action failed.");
    }
  }

  const evidence = useMemo(() => {
    try {
      return JSON.parse(recommendation?.evidence_json || "{}") as Record<string, unknown>;
    } catch {
      return {};
    }
  }, [recommendation]);

  if (!recommendation || !pack) {
    return <div className="rounded-lg border border-line bg-white p-6 text-steel">Loading recommendation...</div>;
  }

  return (
    <div className="space-y-6">
      <Link href="/" className="inline-flex items-center gap-2 text-sm font-medium text-steel hover:text-ink">
        <ArrowLeft size={16} /> Back to dashboard
      </Link>

      <section className="rounded-lg border border-line bg-white p-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-ink">{recommendation.finding_type.replaceAll("_", " ")}</h1>
            <p className="mt-2 max-w-3xl text-sm text-steel">{pack.explanation}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              <Badge value={recommendation.confidence} />
              <Badge value={recommendation.risk_level} />
              <Badge value={recommendation.status} />
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <button onClick={() => transition("approve")} className="flex items-center gap-2 rounded-md bg-safe px-3 py-2 text-sm font-medium text-white">
              <Check size={16} /> Approve
            </button>
            <button onClick={() => transition("simulate")} className="flex items-center gap-2 rounded-md bg-ink px-3 py-2 text-sm font-medium text-white">
              <Play size={16} /> Simulate
            </button>
            <button onClick={() => transition("reject")} className="flex items-center gap-2 rounded-md border border-line bg-white px-3 py-2 text-sm font-medium text-danger">
              <X size={16} /> Reject
            </button>
          </div>
        </div>
        {message ? <div className="mt-4 rounded-md border border-line bg-panel px-3 py-2 text-sm text-steel">{message}</div> : null}
      </section>

      <section className="grid gap-4 md:grid-cols-4">
        <MetricCard label="Monthly savings" value={`$${recommendation.estimated_monthly_savings.toFixed(2)}`} />
        <MetricCard label="Annual savings" value={`$${recommendation.estimated_annual_savings.toFixed(2)}`} />
        <MetricCard label="Action" value={recommendation.recommended_action.replaceAll("_", " ")} />
        <MetricCard label="Mode" value={pack.execution_mode.replaceAll("_", " ")} />
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-lg border border-line bg-white p-4">
          <h2 className="text-sm font-semibold text-ink">Evidence</h2>
          <dl className="mt-4 grid gap-3 text-sm">
            {Object.entries(evidence).map(([key, value]) => (
              <div key={key} className="grid grid-cols-[150px_1fr] gap-3 border-b border-slate-100 pb-2 last:border-0">
                <dt className="text-steel">{key}</dt>
                <dd className="break-words text-ink">{typeof value === "object" ? JSON.stringify(value) : String(value)}</dd>
              </div>
            ))}
          </dl>
        </div>
        <div className="rounded-lg border border-line bg-white p-4">
          <h2 className="text-sm font-semibold text-ink">Safety notes</h2>
          <p className="mt-4 text-sm text-steel">{pack.risk_warning}</p>
          <h3 className="mt-5 text-sm font-semibold text-ink">Rollback</h3>
          <p className="mt-2 text-sm text-steel">{pack.rollback_note}</p>
          <h3 className="mt-5 text-sm font-semibold text-ink">SDK/API logic</h3>
          <p className="mt-2 text-sm text-steel">{pack.sdk_logic}</p>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <CommandBlock title="Pre-check command" command={pack.pre_check_command} />
        <CommandBlock title="Backup or snapshot command" command={pack.backup_command} />
        <CommandBlock title="Dry-run command" command={pack.dry_run_command} />
        <CommandBlock title="Final command requiring approval" command={pack.final_command} />
      </section>
    </div>
  );
}
