import csv
import io
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParsedFile:
    file_type: str
    provider_detected: str | None
    records: list[dict[str, Any]]
    errors: list[dict[str, Any]] = field(default_factory=list)


def parse_export(filename: str, content: bytes) -> ParsedFile:
    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix == "csv":
        return _parse_csv(content)
    if suffix == "json":
        return _parse_json(content)
    return ParsedFile(file_type=suffix or "unknown", provider_detected=None, records=[], errors=[{"message": "Only .csv and .json files are supported."}])


def _parse_csv(content: bytes) -> ParsedFile:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    records: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    if not reader.fieldnames:
        return ParsedFile(file_type="csv", provider_detected=None, records=[], errors=[{"message": "CSV file has no header row."}])
    for line_number, row in enumerate(reader, start=2):
        clean = {str(k).strip(): _clean_value(v) for k, v in row.items() if k is not None}
        if not any(value not in (None, "") for value in clean.values()):
            continue
        clean["_source_row"] = line_number
        records.append(clean)
    provider = detect_provider(records)
    if not records:
        errors.append({"message": "CSV file did not contain any data rows."})
    return ParsedFile(file_type="csv", provider_detected=provider, records=records, errors=errors)


def _parse_json(content: bytes) -> ParsedFile:
    try:
        payload = json.loads(content.decode("utf-8"))
    except json.JSONDecodeError as exc:
        return ParsedFile(file_type="json", provider_detected=None, records=[], errors=[{"message": f"Invalid JSON: {exc.msg}", "line": exc.lineno}])
    if isinstance(payload, dict):
        if isinstance(payload.get("records"), list):
            items = payload["records"]
        elif isinstance(payload.get("data"), list):
            items = payload["data"]
        else:
            items = [payload]
    elif isinstance(payload, list):
        items = payload
    else:
        return ParsedFile(file_type="json", provider_detected=None, records=[], errors=[{"message": "JSON must be an object, a list, or contain a records/data list."}])

    records: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append({"source_row": index, "message": "JSON record must be an object."})
            continue
        item = dict(item)
        item["_source_row"] = index
        records.append(item)
    return ParsedFile(file_type="json", provider_detected=detect_provider(records), records=records, errors=errors)


def detect_provider(records: list[dict[str, Any]]) -> str | None:
    saw_aws = False
    saw_azure = False
    for record in records:
        provider = str(record.get("provider") or "").lower()
        keys = {str(k).lower() for k in record}
        values = " ".join(str(v).lower() for v in record.values() if v is not None)
        saw_aws = saw_aws or provider == "aws" or "account_id" in keys or "aws::" in values or "ec2" in values
        saw_azure = saw_azure or provider == "azure" or "subscription_id" in keys or "microsoft.compute" in values or "resource_group" in keys
    if saw_aws and not saw_azure:
        return "aws"
    if saw_azure and not saw_aws:
        return "azure"
    return None


def _clean_value(value: Any) -> Any:
    if isinstance(value, str):
        stripped = value.strip()
        return None if stripped == "" else stripped
    return value
