import json
from collections import defaultdict
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import AuditEvent, CloudResource, Recommendation


def get_summary(db: Session) -> dict[str, Any]:
    resources = db.query(CloudResource).all()
    recommendations = db.query(Recommendation).all()
    provider_savings: dict[str, float] = defaultdict(float)
    finding_savings: dict[str, float] = defaultdict(float)
    status_counts: dict[str, int] = defaultdict(int)
    confidence_counts: dict[str, int] = defaultdict(int)
    risk_counts: dict[str, int] = defaultdict(int)
    for rec in recommendations:
        provider_savings[rec.resource.provider] += rec.estimated_monthly_savings
        finding_savings[rec.finding_type] += rec.estimated_monthly_savings
        status_counts[rec.status] += 1
        confidence_counts[rec.confidence] += 1
        risk_counts[rec.risk_level] += 1
    recent_events = db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(8).all()
    return {
        "resources_scanned": len(resources),
        "recommendation_count": len(recommendations),
        "estimated_monthly_savings": round(sum(rec.estimated_monthly_savings for rec in recommendations), 2),
        "estimated_annual_savings": round(sum(rec.estimated_annual_savings for rec in recommendations), 2),
        "savings_by_provider": {k: round(v, 2) for k, v in provider_savings.items()},
        "savings_by_finding_type": {k: round(v, 2) for k, v in finding_savings.items()},
        "status_counts": dict(status_counts),
        "confidence_counts": dict(confidence_counts),
        "risk_counts": dict(risk_counts),
        "protected_or_review_count": sum(1 for rec in recommendations if rec.finding_type == "PROTECTED_RESOURCE" or rec.recommended_action == "MANUAL_REVIEW"),
        "needs_metrics_count": sum(1 for rec in recommendations if rec.finding_type == "NEEDS_METRICS"),
        "recent_audit_events": [
            {
                "id": event.id,
                "entity_type": event.entity_type,
                "entity_id": event.entity_id,
                "action": event.action,
                "actor": event.actor,
                "metadata": json.loads(event.metadata_json or "{}"),
                "created_at": event.created_at.isoformat(),
            }
            for event in recent_events
        ],
    }
