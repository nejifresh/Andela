from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ImportBatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    provider_detected: str | None
    provider_selected: str | None
    file_type: str
    record_count: int
    error_count: int
    errors_json: str
    created_at: datetime


class CloudResourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    import_batch_id: int
    provider: str
    account_id: str | None
    resource_id: str
    resource_name: str | None
    resource_type: str | None
    service: str | None
    region: str | None
    resource_group: str | None
    usage_start_date: str | None
    usage_end_date: str | None
    monthly_cost: float
    currency: str
    tags_json: str
    state: str | None
    attached_to: str | None
    disk_state: str | None
    managed_by: str | None
    power_state: str | None
    cpu_p95: float | None
    network_in_mb: float | None
    network_out_mb: float | None
    source_file: str
    source_row: int
    raw_record_json: str
    created_at: datetime


class RecommendationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resource_id_fk: int
    finding_type: str
    estimated_monthly_savings: float
    estimated_annual_savings: float
    confidence: str
    risk_level: str
    recommended_action: str
    evidence_json: str
    status: str
    created_at: datetime
    updated_at: datetime
    resource: CloudResourceRead | None = None


class RemediationPackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recommendation_id: int
    explanation: str
    pre_check_command: str | None
    backup_command: str | None
    dry_run_command: str | None
    final_command: str | None
    sdk_logic: str
    risk_warning: str
    rollback_note: str
    requires_approval: bool
    execution_mode: str
    created_at: datetime


class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_type: str
    entity_id: str
    action: str
    actor: str
    metadata_json: str
    created_at: datetime


class SummaryRead(BaseModel):
    resources_scanned: int
    recommendation_count: int
    estimated_monthly_savings: float
    estimated_annual_savings: float
    savings_by_provider: dict[str, float] = Field(default_factory=dict)
    savings_by_finding_type: dict[str, float] = Field(default_factory=dict)
    status_counts: dict[str, int] = Field(default_factory=dict)
    confidence_counts: dict[str, int] = Field(default_factory=dict)
    risk_counts: dict[str, int] = Field(default_factory=dict)
    protected_or_review_count: int = 0
    needs_metrics_count: int = 0
    recent_audit_events: list[dict[str, Any]] = Field(default_factory=list)
