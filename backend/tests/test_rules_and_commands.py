from app.db.models import CloudResource
from app.services.command_generator import build_remediation_pack
from app.services.rule_engine import evaluate_resource, to_recommendation


def resource(**overrides):
    values = {
        "id": 1,
        "import_batch_id": 1,
        "provider": "aws",
        "account_id": "acct",
        "resource_id": "vol-test",
        "resource_type": "ebs_volume",
        "service": "EC2",
        "region": "us-east-1",
        "monthly_cost": 10.0,
        "currency": "USD",
        "tags_json": "{}",
        "state": "available",
        "attached_to": None,
        "source_file": "fixture.csv",
        "source_row": 2,
        "raw_record_json": "{}",
    }
    values.update(overrides)
    return CloudResource(**values)


def test_aws_unattached_ebs_rule_and_commands():
    cloud_resource = resource()
    draft = evaluate_resource(cloud_resource)
    assert draft is not None
    assert draft.finding_type == "UNATTACHED_DISK"
    assert draft.confidence == "HIGH"
    rec = to_recommendation(cloud_resource, draft)
    rec.id = 1
    pack = build_remediation_pack(rec, cloud_resource)
    assert "describe-volumes" in pack.pre_check_command
    assert "delete-volume" in pack.final_command
    assert pack.requires_approval is True


def test_azure_unattached_disk_rule_and_commands():
    cloud_resource = resource(
        provider="azure",
        resource_id="/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/disks/disk1",
        resource_name="disk1",
        resource_type="Microsoft.Compute/disks",
        region="eastus",
        resource_group="rg",
        state=None,
        disk_state="Unattached",
        managed_by=None,
    )
    draft = evaluate_resource(cloud_resource)
    assert draft is not None
    assert draft.confidence == "HIGH"
    rec = to_recommendation(cloud_resource, draft)
    rec.id = 1
    pack = build_remediation_pack(rec, cloud_resource)
    assert "az disk show" in pack.pre_check_command
    assert "az disk delete" in pack.final_command


def test_idle_vm_with_metrics():
    cloud_resource = resource(
        resource_id="i-idle",
        resource_type="ec2_instance",
        state="running",
        cpu_p95=2.0,
        network_in_mb=20,
        network_out_mb=15,
    )
    draft = evaluate_resource(cloud_resource)
    assert draft is not None
    assert draft.finding_type == "IDLE_VM"
    assert draft.recommended_action == "STOP_VM"


def test_missing_metrics_does_not_overclaim_idleness():
    cloud_resource = resource(resource_id="i-needs", resource_type="ec2_instance", state="running", cpu_p95=None, network_in_mb=None, network_out_mb=None)
    draft = evaluate_resource(cloud_resource)
    assert draft is not None
    assert draft.finding_type == "NEEDS_METRICS"
    assert draft.confidence == "LOW"
    assert draft.savings == 0.0


def test_protected_resource_escalates_to_manual_review():
    cloud_resource = resource(tags_json='{"keep": "true"}')
    draft = evaluate_resource(cloud_resource)
    assert draft is not None
    assert draft.finding_type == "PROTECTED_RESOURCE"
    assert draft.recommended_action == "MANUAL_REVIEW"
    assert draft.savings == 0.0


def test_zero_cost_resource_suppressed():
    cloud_resource = resource(monthly_cost=0)
    assert evaluate_resource(cloud_resource) is None
