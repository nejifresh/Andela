from pathlib import Path

from app.services.normalizer import normalize_record
from app.services.parser import parse_export

SAMPLE_DIR = Path(__file__).resolve().parents[1] / "sample_data"


def test_parse_aws_csv_and_source_row():
    parsed = parse_export("aws_resources.csv", (SAMPLE_DIR / "aws_resources.csv").read_bytes())
    assert parsed.file_type == "csv"
    assert parsed.provider_detected == "aws"
    assert len(parsed.records) == 5
    normalized, errors = normalize_record(parsed.records[0], "aws_resources.csv")
    assert errors == []
    assert normalized["provider"] == "aws"
    assert normalized["resource_id"] == "vol-0aaa111"
    assert normalized["source_row"] == 2


def test_parse_aws_json():
    parsed = parse_export("aws_resources.json", (SAMPLE_DIR / "aws_resources.json").read_bytes())
    assert parsed.file_type == "json"
    assert parsed.provider_detected == "aws"
    assert len(parsed.records) == 2


def test_parse_azure_csv():
    parsed = parse_export("azure_resources.csv", (SAMPLE_DIR / "azure_resources.csv").read_bytes())
    assert parsed.provider_detected == "azure"
    normalized, errors = normalize_record(parsed.records[0], "azure_resources.csv")
    assert errors == []
    assert normalized["provider"] == "azure"
    assert normalized["resource_group"] == "rg-dev"


def test_parse_azure_json():
    parsed = parse_export("azure_resources.json", (SAMPLE_DIR / "azure_resources.json").read_bytes())
    assert parsed.file_type == "json"
    assert parsed.provider_detected == "azure"
    assert len(parsed.records) == 2
