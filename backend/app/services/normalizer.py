import json
from typing import Any


REQUIRED_FIELDS = ("provider", "resource_id")


def normalize_record(record: dict[str, Any], filename: str, provider_override: str | None = None) -> tuple[dict[str, Any] | None, list[str]]:
    provider = _lower(provider_override or record.get("provider") or _infer_provider(record))
    errors: list[str] = []
    if provider not in {"aws", "azure"}:
        errors.append("Provider could not be determined. Include provider=aws/azure or pass a provider override.")

    resource_id = _first(record, "resource_id", "ResourceId", "id", "instance_id", "volume_id")
    if not resource_id:
        errors.append("Missing resource_id.")
    if errors:
        return None, errors

    account_id = _first(record, "account_id", "subscription_id", "subscriptionId", "AccountId")
    region = _first(record, "region", "location", "Location", "availability_zone")
    state = _first(record, "state", "volume_state", "instance_state", "State")
    tags = _parse_tags(_first(record, "tags", "Tags") or {})
    normalized = {
        "provider": provider,
        "account_id": str(account_id) if account_id is not None else None,
        "resource_id": str(resource_id),
        "resource_name": _first(record, "resource_name", "name", "Name"),
        "resource_type": _first(record, "resource_type", "ResourceType", "type", "meter_category"),
        "service": _first(record, "service", "meter_category", "Service"),
        "region": str(region) if region is not None else None,
        "resource_group": _first(record, "resource_group", "resourceGroup"),
        "usage_start_date": _first(record, "usage_start_date", "date", "usageDate", "Date"),
        "usage_end_date": _first(record, "usage_end_date", "date", "usageDate", "Date"),
        "monthly_cost": _float(_first(record, "monthly_cost", "cost", "Cost", "pretax_cost"), 0.0),
        "currency": str(_first(record, "currency", "Currency") or "USD"),
        "tags_json": json.dumps(tags, sort_keys=True),
        "state": str(state) if state is not None else None,
        "attached_to": _none_if_empty(_first(record, "attached_to", "attachment", "attachedTo")),
        "disk_state": _first(record, "disk_state", "diskState"),
        "managed_by": _none_if_empty(_first(record, "managed_by", "managedBy")),
        "power_state": _first(record, "power_state", "powerState"),
        "cpu_p95": _float_or_none(_first(record, "cpu_p95", "cpuP95")),
        "network_in_mb": _float_or_none(_first(record, "network_in_mb", "networkInMb")),
        "network_out_mb": _float_or_none(_first(record, "network_out_mb", "networkOutMb")),
        "source_file": filename,
        "source_row": int(record.get("_source_row", 0)),
        "raw_record_json": json.dumps({k: v for k, v in record.items() if k != "_source_row"}, sort_keys=True, default=str),
    }
    return normalized, []


def _infer_provider(record: dict[str, Any]) -> str | None:
    keys = {str(k).lower() for k in record}
    values = " ".join(str(v).lower() for v in record.values() if v is not None)
    if "subscription_id" in keys or "microsoft.compute" in values:
        return "azure"
    if "account_id" in keys or "aws::" in values or "ec2" in values:
        return "aws"
    return None


def _first(record: dict[str, Any], *keys: str) -> Any:
    lower_map = {str(k).lower(): v for k, v in record.items()}
    for key in keys:
        if key in record and record[key] not in ("", None):
            return record[key]
        value = lower_map.get(key.lower())
        if value not in ("", None):
            return value
    return None


def _parse_tags(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {str(k).lower(): str(v).lower() for k, v in value.items()}
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return {str(k).lower(): str(v).lower() for k, v in parsed.items()}
        except json.JSONDecodeError:
            pass
        tags: dict[str, str] = {}
        for part in value.replace(",", ";").split(";"):
            if "=" in part:
                key, tag_value = part.split("=", 1)
                tags[key.strip().lower()] = tag_value.strip().lower()
        return tags
    return {}


def _lower(value: Any) -> str | None:
    return str(value).strip().lower() if value not in (None, "") else None


def _none_if_empty(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    return None if text.lower() in {"null", "none", "n/a"} else text


def _float(value: Any, default: float) -> float:
    parsed = _float_or_none(value)
    return default if parsed is None else parsed


def _float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace("$", "").replace(",", ""))
    except ValueError:
        return None
