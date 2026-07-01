"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { BarChart, Bar, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { FileUp, Play, RefreshCw } from "lucide-react";
import { apiGet, apiPost, Recommendation, Summary } from "@/lib/api";
import { Badge } from "@/components/Badge";
import { MetricCard } from "@/components/MetricCard";

export default function DashboardPage() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function refresh() {
    const [summaryData, recs] = await Promise.all([
      apiGet<Summary>("/api/summary"),
      apiGet<Recommendation[]>("/api/recommendations")
    ]);
    setSummary(summaryData);
    setRecommendations(recs);
  }

  useEffect(() => {
    refresh().catch(() => setMessage("Start the FastAPI backend on http://localhost:8000 to load data."));
  }, []);

  async function upload() {
    if (!file) return;
    setLoading(true);
    setMessage("");
    const formData = new FormData();
    formData.append("file", file);
    try {
      const result = await apiPost<{ record_count: number; error_count: number }>("/api/imports/upload", formData);
      setMessage(`Imported ${result.record_count} records with ${result.error_count} validation issue(s).`);
      setFile(null);
      await refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Upload failed.");
    } finally {
      setLoading(false);
    }
  }

  async function runRecommendations() {
    setLoading(true);
    setMessage("");
    try {
      const recs = await apiPost<Recommendation[]>("/api/recommendations/run");
      setMessage(`Generated ${recs.length} recommendation(s).`);
      await refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Recommendation run failed.");
    } finally {
      setLoading(false);
    }
  }

  const providerChart = useMemo(
    () => Object.entries(summary?.savings_by_provider || {}).map(([name, value]) => ({ name: name.toUpperCase(), value })),
    [summary]
  );

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-line bg-white p-5">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-ink">Evidence-backed cloud waste review</h1>
            <p className="mt-1 text-sm text-steel">Upload local AWS/Azure exports, run deterministic rules, then approve or simulate generated commands.</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <label className="flex cursor-pointer items-center gap-2 rounded-md border border-line bg-panel px-3 py-2 text-sm text-ink">
              <FileUp size={16} />
              <span>{file ? file.name : "Choose export"}</span>
              <input className="hidden" type="file" accept=".csv,.json" onChange={(event) => setFile(event.target.files?.[0] || null)} />
            </label>
            <button disabled={!file || loading} onClick={upload} className="rounded-md bg-ink px-3 py-2 text-sm font-medium text-white disabled:opacity-50">
              Upload
            </button>
            <button disabled={loading} onClick={runRecommendations} className="flex items-center gap-2 rounded-md bg-safe px-3 py-2 text-sm font-medium text-white disabled:opacity-50">
              <Play size={16} /> Run Recommendations
            </button>
            <button disabled={loading} onClick={refresh} className="rounded-md border border-line bg-white p-2 text-steel disabled:opacity-50" aria-label="Refresh">
              <RefreshCw size={16} />
            </button>
          </div>
        </div>
        {message ? <div className="mt-4 rounded-md border border-line bg-panel px-3 py-2 text-sm text-steel">{message}</div> : null}
      </section>

      <section className="grid gap-4 md:grid-cols-4">
        <MetricCard label="Resources scanned" value={String(summary?.resources_scanned || 0)} />
        <MetricCard label="Findings" value={String(summary?.recommendation_count || 0)} hint={`${summary?.needs_metrics_count || 0} need metrics`} />
        <MetricCard label="Monthly savings" value={`$${(summary?.estimated_monthly_savings || 0).toFixed(2)}`} />
        <MetricCard label="Annual savings" value={`$${(summary?.estimated_annual_savings || 0).toFixed(2)}`} hint={`${summary?.protected_or_review_count || 0} review guarded`} />
      </section>

      <section className="grid gap-4 lg:grid-cols-[1fr_2fr]">
        <div className="rounded-lg border border-line bg-white p-4">
          <h2 className="text-sm font-semibold text-ink">Savings by provider</h2>
          <div className="mt-4 h-60">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={providerChart}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#047857" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="overflow-hidden rounded-lg border border-line bg-white">
          <div className="border-b border-line px-4 py-3">
            <h2 className="text-sm font-semibold text-ink">Recommendations</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-line text-sm">
              <thead className="bg-panel text-left text-xs uppercase tracking-wide text-steel">
                <tr>
                  <th className="px-4 py-3">Resource</th>
                  <th className="px-4 py-3">Finding</th>
                  <th className="px-4 py-3">Savings</th>
                  <th className="px-4 py-3">Confidence</th>
                  <th className="px-4 py-3">Risk</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {recommendations.map((rec) => (
                  <tr key={rec.id} className="align-top">
                    <td className="px-4 py-3">
                      <div className="font-medium text-ink">{rec.resource?.resource_id}</div>
                      <div className="text-xs text-steel">{rec.resource?.provider.toUpperCase()} · {rec.resource?.region || rec.resource?.resource_group}</div>
                    </td>
                    <td className="px-4 py-3 text-steel">{rec.finding_type.replaceAll("_", " ")}</td>
                    <td className="px-4 py-3 font-medium text-ink">${rec.estimated_monthly_savings.toFixed(2)}</td>
                    <td className="px-4 py-3"><Badge value={rec.confidence} /></td>
                    <td className="px-4 py-3"><Badge value={rec.risk_level} /></td>
                    <td className="px-4 py-3"><Badge value={rec.status} /></td>
                    <td className="px-4 py-3 text-right">
                      <Link className="rounded-md border border-line px-3 py-2 text-xs font-medium text-ink hover:bg-panel" href={`/recommendations/${rec.id}`}>
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
                {recommendations.length === 0 ? (
                  <tr>
                    <td className="px-4 py-8 text-center text-steel" colSpan={7}>No recommendations yet. Upload sample data and run recommendations.</td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
}
