from pathlib import Path

SAMPLE_DIR = Path(__file__).resolve().parents[1] / "sample_data"


def upload(client, filename):
    with (SAMPLE_DIR / filename).open("rb") as handle:
        return client.post("/api/imports/upload", files={"file": (filename, handle, "text/csv" if filename.endswith(".csv") else "application/json")})


def test_upload_run_workflow_and_export(client):
    assert client.get("/health").json()["status"] == "ok"
    response = upload(client, "aws_resources.csv")
    assert response.status_code == 200
    assert response.json()["record_count"] == 5
    response = upload(client, "azure_resources.csv")
    assert response.status_code == 200
    assert response.json()["record_count"] == 5

    resources = client.get("/api/resources")
    assert resources.status_code == 200
    assert len(resources.json()) == 10

    run = client.post("/api/recommendations/run")
    assert run.status_code == 200
    recommendations = run.json()
    assert len(recommendations) >= 6
    assert any(rec["finding_type"] == "PROTECTED_RESOURCE" for rec in recommendations)
    assert any(rec["finding_type"] == "NEEDS_METRICS" for rec in recommendations)

    first_actionable = next(rec for rec in recommendations if rec["recommended_action"] != "MANUAL_REVIEW")
    detail = client.get(f"/api/recommendations/{first_actionable['id']}")
    assert detail.status_code == 200
    pack = client.get(f"/api/recommendations/{first_actionable['id']}/remediation-pack")
    assert pack.status_code == 200
    assert pack.json()["requires_approval"] is True

    approved = client.post(f"/api/recommendations/{first_actionable['id']}/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "APPROVED"
    simulated = client.post(f"/api/recommendations/{first_actionable['id']}/simulate")
    assert simulated.status_code == 200
    assert simulated.json()["status"] == "SIMULATED_EXECUTION"

    summary = client.get("/api/summary")
    assert summary.status_code == 200
    assert summary.json()["estimated_monthly_savings"] > 0

    exported = client.get("/api/export/recommendations.csv")
    assert exported.status_code == 200
    assert "resource_id" in exported.text
