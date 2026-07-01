from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ImportBatch(Base):
    __tablename__ = "import_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_detected: Mapped[str | None] = mapped_column(String(50), nullable=True)
    provider_selected: Mapped[str | None] = mapped_column(String(50), nullable=True)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    record_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    errors_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    resources: Mapped[list["CloudResource"]] = relationship(back_populates="import_batch")


class CloudResource(Base):
    __tablename__ = "cloud_resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    import_batch_id: Mapped[int] = mapped_column(ForeignKey("import_batches.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(20), index=True)
    account_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resource_id: Mapped[str] = mapped_column(String(1024), index=True)
    resource_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resource_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    service: Mapped[str | None] = mapped_column(String(255), nullable=True)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    resource_group: Mapped[str | None] = mapped_column(String(255), nullable=True)
    usage_start_date: Mapped[str | None] = mapped_column(String(80), nullable=True)
    usage_end_date: Mapped[str | None] = mapped_column(String(80), nullable=True)
    monthly_cost: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    tags_json: Mapped[str] = mapped_column(Text, default="{}")
    state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    attached_to: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    disk_state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    managed_by: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    power_state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    cpu_p95: Mapped[float | None] = mapped_column(Float, nullable=True)
    network_in_mb: Mapped[float | None] = mapped_column(Float, nullable=True)
    network_out_mb: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_file: Mapped[str] = mapped_column(String(255), nullable=False)
    source_row: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_record_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    import_batch: Mapped[ImportBatch] = relationship(back_populates="resources")
    recommendations: Mapped[list["Recommendation"]] = relationship(back_populates="resource")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resource_id_fk: Mapped[int] = mapped_column(ForeignKey("cloud_resources.id"), nullable=False)
    finding_type: Mapped[str] = mapped_column(String(80), index=True)
    estimated_monthly_savings: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_annual_savings: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[str] = mapped_column(String(20), default="LOW")
    risk_level: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    recommended_action: Mapped[str] = mapped_column(String(80), default="MANUAL_REVIEW")
    evidence_json: Mapped[str] = mapped_column(Text, default="{}")
    status: Mapped[str] = mapped_column(String(40), default="DRAFT", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resource: Mapped[CloudResource] = relationship(back_populates="recommendations")
    remediation_pack: Mapped["RemediationPack"] = relationship(back_populates="recommendation", uselist=False)


class RemediationPack(Base):
    __tablename__ = "remediation_packs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    recommendation_id: Mapped[int] = mapped_column(ForeignKey("recommendations.id"), nullable=False, unique=True)
    explanation: Mapped[str] = mapped_column(Text)
    pre_check_command: Mapped[str | None] = mapped_column(Text, nullable=True)
    backup_command: Mapped[str | None] = mapped_column(Text, nullable=True)
    dry_run_command: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_command: Mapped[str | None] = mapped_column(Text, nullable=True)
    sdk_logic: Mapped[str] = mapped_column(Text)
    risk_warning: Mapped[str] = mapped_column(Text)
    rollback_note: Mapped[str] = mapped_column(Text)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    execution_mode: Mapped[str] = mapped_column(String(40), default="GENERATE_ONLY")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    recommendation: Mapped[Recommendation] = relationship(back_populates="remediation_pack")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entity_type: Mapped[str] = mapped_column(String(80), index=True)
    entity_id: Mapped[str] = mapped_column(String(120), index=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    actor: Mapped[str] = mapped_column(String(120), default="local-demo-user")
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
