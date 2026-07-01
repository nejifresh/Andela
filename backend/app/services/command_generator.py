import json
import re

from app.db.models import CloudResource, Recommendation, RemediationPack


def build_remediation_pack(recommendation: Recommendation, resource: CloudResource) -> RemediationPack:
    provider = resource.provider.lower()
    finding = recommendation.finding_type
    if provider == "aws" and finding == "UNATTACHED_DISK":
        return _aws_ebs_pack(recommendation, resource)
    if provider == "aws" and finding in {"IDLE_VM", "NEEDS_METRICS"}:
        return _aws_ec2_pack(recommendation, resource)
    if provider == "azure" and finding == "UNATTACHED_DISK":
        return _azure_disk_pack(recommendation, resource)
    if provider == "azure" and finding in {"IDLE_VM", "NEEDS_METRICS"}:
        return _azure_vm_pack(recommendation, resource)
    return _manual_review_pack(recommendation, resource)


def _aws_ebs_pack(recommendation: Recommendation, resource: CloudResource) -> RemediationPack:
    region = resource.region or "<region>"
    volume_id = resource.resource_id
    return _pack(
        recommendation,
        explanation=f"EBS volume {volume_id} appears unattached and has ${resource.monthly_cost:.2f} in monthly spend.",
        pre=f"aws ec2 describe-volumes --volume-ids {volume_id} --region {region}",
        backup=f'aws ec2 create-snapshot --volume-id {volume_id} --region {region} --description "pre-delete snapshot created by Cost Optimizer"',
        dry=f"aws ec2 delete-volume --volume-id {volume_id} --region {region} --dry-run",
        final=f"aws ec2 delete-volume --volume-id {volume_id} --region {region}",
        sdk="Use boto3 EC2 describe_volumes to confirm State=available, create_snapshot, then delete_volume after approval.",
        risk="Deleting a volume can permanently remove data if a current snapshot is not available.",
        rollback="There is no direct undelete. Restore by creating a new EBS volume from the pre-delete snapshot.",
    )


def _aws_ec2_pack(recommendation: Recommendation, resource: CloudResource) -> RemediationPack:
    region = resource.region or "<region>"
    instance_id = resource.resource_id
    final = f"aws ec2 stop-instances --instance-ids {instance_id} --region {region}"
    if recommendation.recommended_action == "TERMINATE_VM":
        final = f"aws ec2 terminate-instances --instance-ids {instance_id} --region {region}"
    return _pack(
        recommendation,
        explanation=f"EC2 instance {instance_id} is a low-utilization candidate; default action is stop or rightsizing review, not deletion.",
        pre=f"aws ec2 describe-instances --instance-ids {instance_id} --region {region}",
        backup=None,
        dry=None,
        final=final,
        sdk="Use boto3 EC2 describe_instances and CloudWatch metrics, then stop_instances only after approval.",
        risk="Stopping or terminating compute can interrupt workloads. Validate owner, schedule, and recent metrics first.",
        rollback="Stopped instances can usually be started again. Terminated instances cannot be directly restored.",
    )


def _azure_disk_pack(recommendation: Recommendation, resource: CloudResource) -> RemediationPack:
    snapshot_name = f"{_safe_name(resource.resource_name or resource.resource_id.split('/')[-1])}-pre-delete-snapshot"
    group = resource.resource_group or "<resource_group>"
    return _pack(
        recommendation,
        explanation=f"Azure managed disk {resource.resource_id} appears unattached and has ${resource.monthly_cost:.2f} in monthly spend.",
        pre=f"az disk show --ids {resource.resource_id}",
        backup=f"az snapshot create --resource-group {group} --source {resource.resource_id} --name {snapshot_name}",
        dry=None,
        final=f"az disk delete --ids {resource.resource_id} --yes",
        sdk="Use Azure SDK for Python to get the disk, verify managed_by is empty, create a snapshot, then begin_delete after approval.",
        risk="Deleting a managed disk can permanently remove data if a current snapshot is not available.",
        rollback="There is no direct undelete. Recreate a managed disk from the pre-delete snapshot.",
    )


def _azure_vm_pack(recommendation: Recommendation, resource: CloudResource) -> RemediationPack:
    final = f"az vm deallocate --ids {resource.resource_id}"
    if recommendation.recommended_action == "DELETE_VM":
        final = f"az vm delete --ids {resource.resource_id} --yes"
    return _pack(
        recommendation,
        explanation=f"Azure VM {resource.resource_id} is a low-utilization candidate; default action is deallocate or rightsizing review.",
        pre=f"az vm get-instance-view --ids {resource.resource_id}",
        backup=None,
        dry=None,
        final=final,
        sdk="Use Azure ComputeManagementClient to get instance view and metrics, then deallocate after approval.",
        risk="Deallocating or deleting a VM can interrupt workloads. Validate owner, environment, and recent metrics first.",
        rollback="A deallocated VM can be started again. Deleted VM rollback depends on backups and attached disks.",
    )


def _manual_review_pack(recommendation: Recommendation, resource: CloudResource) -> RemediationPack:
    evidence = json.loads(recommendation.evidence_json or "{}")
    return _pack(
        recommendation,
        explanation=f"{resource.provider.upper()} resource {resource.resource_id} requires manual review before action.",
        pre=evidence.get("suggested_precheck"),
        backup=None,
        dry=None,
        final=None,
        sdk="Inspect source evidence and provider state manually before choosing a remediation.",
        risk="Automated command generation was intentionally withheld because the recommendation needs human review.",
        rollback="No rollback applies until a concrete remediation is selected.",
    )


def _pack(recommendation: Recommendation, explanation: str, pre: str | None, backup: str | None, dry: str | None, final: str | None, sdk: str, risk: str, rollback: str) -> RemediationPack:
    return RemediationPack(
        recommendation_id=recommendation.id,
        explanation=explanation,
        pre_check_command=pre,
        backup_command=backup,
        dry_run_command=dry,
        final_command=final,
        sdk_logic=sdk,
        risk_warning=risk,
        rollback_note=rollback,
        requires_approval=True,
        execution_mode="GENERATE_ONLY",
    )


def _safe_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9-]", "-", value).strip("-")[:60] or "resource"
