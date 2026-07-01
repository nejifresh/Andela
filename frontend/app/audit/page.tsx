"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";

type AuditEvent = {
  id: number;
  entity_type: string;
  entity_id: string;
  action: string;
  actor: string;
  metadata_json: string;
  created_at: string;
};

export default function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    apiGet<AuditEvent[]>("/api/audit-events")
      .then(setEvents)
      .catch((error) => setMessage(error instanceof Error ? error.message : "Could not load audit events."));
  }, []);

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-line bg-white p-5">
        <h1 className="text-2xl font-semibold text-ink">Audit log</h1>
        <p className="mt-1 text-sm text-steel">Imports, rule runs, approvals, rejections, simulations, and exports are recorded here.</p>
        {message ? <div className="mt-4 rounded-md border border-line bg-panel px-3 py-2 text-sm text-steel">{message}</div> : null}
      </section>

      <section className="overflow-hidden rounded-lg border border-line bg-white">
        <table className="min-w-full divide-y divide-line text-sm">
          <thead className="bg-panel text-left text-xs uppercase tracking-wide text-steel">
            <tr>
              <th className="px-4 py-3">Time</th>
              <th className="px-4 py-3">Action</th>
              <th className="px-4 py-3">Entity</th>
              <th className="px-4 py-3">Actor</th>
              <th className="px-4 py-3">Metadata</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {events.map((event) => (
              <tr key={event.id} className="align-top">
                <td className="whitespace-nowrap px-4 py-3 text-steel">{new Date(event.created_at).toLocaleString()}</td>
                <td className="px-4 py-3 font-medium text-ink">{event.action.replaceAll("_", " ")}</td>
                <td className="px-4 py-3 text-steel">{event.entity_type} #{event.entity_id}</td>
                <td className="px-4 py-3 text-steel">{event.actor}</td>
                <td className="px-4 py-3 text-xs text-steel">{event.metadata_json}</td>
              </tr>
            ))}
            {events.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-steel">No audit events yet.</td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </section>
    </div>
  );
}
