import json
from pathlib import Path

from app.db.models import CloudResource
from app.services.command_generator import build_remediation_pack
from app.services.normalizer import normalize_record
from app.services.parser import parse_export
from app.services.rule_engine import evaluate_resource, to_recommendation


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = ROOT / "sample_data"


def main() -> None:
    resources = []
    next_id = 1
    for filename in ["aws_resources.csv", "azure_resources.csv"]:
        parsed = parse_export(filename, (SAMPLE_DIR / filename).read_bytes())
        for record in parsed.records:
            normalized, errors = normalize_record(record, filename, parsed.provider_detected)
            if errors or normalized is None:
                continue
            resource = CloudResource(id=next_id, import_batch_id=1, **normalized)
            resources.append(resource)
            next_id += 1

    findings = []
    command_pass = True
    for resource in resources:
        draft = evaluate_resource(resource)
        if not draft:
            continue
        rec = to_recommendation(resource, draft)
        rec.id = len(findings) + 1
        pack = build_remediation_pack(rec, resource)
        if rec.recommended_action != "MANUAL_REVIEW" and not pack.final_command:
            command_pass = False
        findings.append((resource.resource_id, rec.finding_type, rec.estimated_monthly_savings))

    expected = {
        ("vol-0aaa111", "UNATTACHED_DISK"),
        ("vol-0ccc333", "PROTECTED_RESOURCE"),
        ("i-0idle111", "IDLE_VM"),
        ("i-0metrics222", "NEEDS_METRICS"),
        ("/subscriptions/sub-111/resourceGroups/rg-dev/providers/Microsoft.Compute/disks/disk-orphan-01", "UNATTACHED_DISK"),
        ("/subscriptions/sub-111/resourceGroups/rg-prod/providers/Microsoft.Compute/disks/disk-protected-01", "PROTECTED_RESOURCE"),
        ("/subscriptions/sub-111/resourceGroups/rg-sandbox/providers/Microsoft.Compute/virtualMachines/vm-idle-01", "IDLE_VM"),
        ("/subscriptions/sub-111/resourceGroups/rg-lab/providers/Microsoft.Compute/virtualMachines/vm-needs-metrics-01", "NEEDS_METRICS"),
    }
    actual = {(resource_id, finding_type) for resource_id, finding_type, _ in findings}
    result = {
        "expected_findings": len(expected),
        "actual_findings": len(actual),
        "missing_findings": sorted([list(item) for item in expected - actual]),
        "extra_findings": sorted([list(item) for item in actual - expected]),
        "command_generation_pass": command_pass,
        "savings_total": round(sum(savings for _, _, savings in findings), 2),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
