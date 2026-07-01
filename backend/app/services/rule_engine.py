import json
from dataclasses import dataclass

from app.db.models import CloudResource, Recommendation


PROTECTED_TAGS = {
    "keep": {"true", "yes", "1"},
    "protected": {"true", "yes", "1"},
    "do-not-delete": {"true", "yes", "1"},
    "environment": {"prod", "production"},
    "owner": {"critical"},
    "business-critical": {"true", "yes", "1"},
}


@dataclass
class FindingDraft:
    finding_type: str
    confidence: str
    risk_level: str
    recommended_action: str
    evidence: dict
    savings: float


def evaluate_resource(resource: CloudResource) -> FindingDraft | None:
    protected, protected_reason = is_protected(resource)
    if resource.monthly_cost <= 0 and not protected:
        return None

    if protected and _is_potential_waste(resource):
        return _draft(
            resource,
            "PROTECTED_RESOURCE",
            "MEDIUM",
            "HIGH",
            "MANUAL_REVIEW",
            savings=0.0,
            extra={"protected_reason": protected_reason},
        )

    provider = resource.provider.lower()
    resource_type = (resource.resource_type or "").lower()

    if provider == "aws" and _is_aws_volume(resource_type):
        return _aws_unattached_volume(resource)
    if provider == "azure" and _is_azure_disk(resource_type):
        return _azure_unattached_disk(resource)
    if provider == "aws" and _is_aws_instance(resource_type):
        return _idle_compute(resource, provider="aws")
    if provider == "azure" and _is_azure_vm(resource_type):
        return _idle_compute(resource, provider="azure")
    return None


def to_recommendation(resource: CloudResource, draft: FindingDraft) -> Recommendation:
    return Recommendation(
        resource_id_fk=resource.id,
        finding_type=draft.finding_type,
        estimated_monthly_savings=draft.savings,
        estimated_annual_savings=draft.savings * 12,
        confidence=draft.confidence,
        risk_level=draft.risk_level,
        recommended_action=draft.recommended_action,
        evidence_json=json.dumps(draft.evidence, sort_keys=True, default=str),
        status="DRAFT",
    )


def is_protected(resource: CloudResource) -> tuple[bool, str | None]:
    tags = json.loads(resource.tags_json or "{}")
    for key, protected_values in PROTECTED_TAGS.items():
        value = str(tags.get(key, "")).lower()
        if value in protected_values:
            return True, f"{key}={value}"
    return False, None


def _aws_unattached_volume(resource: CloudResource) -> FindingDraft | None:
    state = (resource.state or "").lower()
    unattached = state in {"available", "unattached"} or not resource.attached_to
    if not unattached or resource.monthly_cost <= 0:
        return None
    confidence = "HIGH" if state in {"available", "unattached"} and not resource.attached_to else "MEDIUM"
    return _draft(resource, "UNATTACHED_DISK", confidence, "MEDIUM", "DELETE_DISK", savings=resource.monthly_cost)


def _azure_unattached_disk(resource: CloudResource) -> FindingDraft | None:
    disk_state = (resource.disk_state or resource.state or "").lower()
    unattached = disk_state == "unattached" or not resource.managed_by
    if not unattached or resource.monthly_cost <= 0:
        return None
    confidence = "HIGH" if disk_state == "unattached" and not resource.managed_by else "MEDIUM"
    return _draft(resource, "UNATTACHED_DISK", confidence, "MEDIUM", "DELETE_DISK", savings=resource.monthly_cost)


def _idle_compute(resource: CloudResource, provider: str) -> FindingDraft | None:
    if resource.monthly_cost <= 0:
        return None
    known_state = resource.state or resource.power_state
    if not known_state:
        return None
    has_metrics = resource.cpu_p95 is not None and resource.network_in_mb is not None and resource.network_out_mb is not None
    if not has_metrics:
        action = "RIGHTSIZING_REVIEW"
        return _draft(resource, "NEEDS_METRICS", "LOW", "MEDIUM", action, savings=0.0, extra={"reason": "Utilization metrics are missing, so the system will not claim true idleness."})
    network_total = (resource.network_in_mb or 0) + (resource.network_out_mb or 0)
    if resource.cpu_p95 < 5 and network_total < 100:
        action = "STOP_VM" if provider == "aws" else "DEALLOCATE_VM"
        return _draft(resource, "IDLE_VM", "MEDIUM", "MEDIUM", action, savings=resource.monthly_cost)
    return None


def _draft(resource: CloudResource, finding_type: str, confidence: str, risk_level: str, action: str, savings: float, extra: dict | None = None) -> FindingDraft:
    evidence = {
        "source_file": resource.source_file,
        "source_row": resource.source_row,
        "provider": resource.provider,
        "resource_id": resource.resource_id,
        "resource_type": resource.resource_type,
        "region": resource.region,
        "resource_group": resource.resource_group,
        "state": resource.state,
        "attached_to": resource.attached_to,
        "disk_state": resource.disk_state,
        "managed_by": resource.managed_by,
        "power_state": resource.power_state,
        "cpu_p95": resource.cpu_p95,
        "network_in_mb": resource.network_in_mb,
        "network_out_mb": resource.network_out_mb,
        "monthly_cost": resource.monthly_cost,
        "tags": json.loads(resource.tags_json or "{}"),
    }
    if extra:
        evidence.update(extra)
    return FindingDraft(finding_type, confidence, risk_level, action, evidence, savings)


def _is_potential_waste(resource: CloudResource) -> bool:
    resource_type = (resource.resource_type or "").lower()
    return (
        _is_aws_volume(resource_type)
        or _is_azure_disk(resource_type)
        or _is_aws_instance(resource_type)
        or _is_azure_vm(resource_type)
    )


def _is_aws_volume(resource_type: str) -> bool:
    return resource_type in {"ebs_volume", "volume", "aws::ec2::volume"} or "ebs" in resource_type


def _is_azure_disk(resource_type: str) -> bool:
    return "microsoft.compute/disks" in resource_type or resource_type == "disk" or "manageddisk" in resource_type


def _is_aws_instance(resource_type: str) -> bool:
    return resource_type in {"ec2_instance", "instance", "aws::ec2::instance"} or "ec2" in resource_type


def _is_azure_vm(resource_type: str) -> bool:
    return "microsoft.compute/virtualmachines" in resource_type or resource_type in {"vm", "virtual_machine", "virtualmachine"}
