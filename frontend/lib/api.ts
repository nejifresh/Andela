export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export type CloudResource = {
  id: number;
  provider: string;
  account_id: string | null;
  resource_id: string;
  resource_name: string | null;
  resource_type: string | null;
  region: string | null;
  resource_group: string | null;
  monthly_cost: number;
  currency: string;
  tags_json: string;
  state: string | null;
  attached_to: string | null;
  disk_state: string | null;
  managed_by: string | null;
  power_state: string | null;
  cpu_p95: number | null;
  network_in_mb: number | null;
  network_out_mb: number | null;
  source_file: string;
  source_row: number;
};

export type Recommendation = {
  id: number;
  resource_id_fk: number;
  finding_type: string;
  estimated_monthly_savings: number;
  estimated_annual_savings: number;
  confidence: string;
  risk_level: string;
  recommended_action: string;
  evidence_json: string;
  status: string;
  resource: CloudResource | null;
};

export type RemediationPack = {
  id: number;
  recommendation_id: number;
  explanation: string;
  pre_check_command: string | null;
  backup_command: string | null;
  dry_run_command: string | null;
  final_command: string | null;
  sdk_logic: string;
  risk_warning: string;
  rollback_note: string;
  requires_approval: boolean;
  execution_mode: string;
};

export type Summary = {
  resources_scanned: number;
  recommendation_count: number;
  estimated_monthly_savings: number;
  estimated_annual_savings: number;
  savings_by_provider: Record<string, number>;
  savings_by_finding_type: Record<string, number>;
  status_counts: Record<string, number>;
  confidence_counts: Record<string, number>;
  risk_counts: Record<string, number>;
  protected_or_review_count: number;
  needs_metrics_count: number;
};

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function apiPost<T>(path: string, body?: BodyInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { method: "POST", body });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}
