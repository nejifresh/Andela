import json
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import AuditEvent


def record_audit_event(db: Session, entity_type: str, entity_id: str | int, action: str, metadata: dict[str, Any] | None = None, actor: str = "local-demo-user") -> AuditEvent:
    event = AuditEvent(
        entity_type=entity_type,
        entity_id=str(entity_id),
        action=action,
        actor=actor,
        metadata_json=json.dumps(metadata or {}, sort_keys=True, default=str),
    )
    db.add(event)
    return event
