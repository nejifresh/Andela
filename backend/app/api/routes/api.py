import csv
import io
import json
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, selectinload

from app.db.models import AuditEvent, CloudResource, ImportBatch, Recommendation, RemediationPack
from app.db.session import get_db
from app.schemas import AuditEventRead, CloudResourceRead, ImportBatchRead, RecommendationRead, RemediationPackRead, SummaryRead
from app.services.audit import record_audit_event
from app.services.command_generator import build_remediation_pack
from app.services.normalizer import normalize_record
from app.services.parser import parse_export
from app.services.rule_engine import evaluate_resource, to_recommendation
from app.services.summary import get_summary

router = APIRouter()


@router.get("/imports", response_model=list[ImportBatchRead])
def list_imports(db: Session = Depends(get_db)):
    return db.query(ImportBatch).order_by(ImportBatch.created_at.desc()).all()


@router.post("/imports/upload", response_model=ImportBatchRead)
async def upload_import(
    file: UploadFile = File(...),
    provider_override: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    content = await file.read()
    parsed = parse_export(file.filename or "upload", content)
    selected_provider = provider_override.lower() if provider_override else parsed.provider_detected
    import_batch = ImportBatch(
        filename=file.filename or "upload",
        provider_detected=parsed.provider_detected,
        provider_selected=selected_provider,
        file_type=parsed.file_type,
        record_count=0,
        error_count=len(parsed.errors),
        errors_json=json.dumps(parsed.errors, sort_keys=True, default=str),
    )
    db.add(import_batch)
    db.flush()

    errors = list(parsed.errors)
    saved_count = 0
    for record in parsed.records:
        normalized, record_errors = normalize_record(record, import_batch.filename, selected_provider)
        if record_errors or normalized is None:
            errors.append({"source_row": record.get("_source_row"), "errors": record_errors})
            continue
        resource = CloudResource(import_batch_id=import_batch.id, **normalized)
        db.add(resource)
        saved_count += 1

    import_batch.record_count = saved_count
    import_batch.error_count = len(errors)
    import_batch.errors_json = json.dumps(errors, sort_keys=True, default=str)
    record_audit_event(db, "import_batch", import_batch.id, "IMPORT_UPLOADED", {"filename": import_batch.filename, "records": saved_count, "errors": len(errors)})
    db.commit()
    db.refresh(import_batch)
    return import_batch


@router.get("/resources", response_model=list[CloudResourceRead])
def list_resources(db: Session = Depends(get_db)):
    return db.query(CloudResource).order_by(CloudResource.created_at.desc()).all()


@router.post("/recommendations/run", response_model=list[RecommendationRead])
def run_recommendations(db: Session = Depends(get_db)):
    db.query(RemediationPack).delete()
    db.query(Recommendation).delete()
    db.flush()

    created: list[Recommendation] = []
    resources = db.query(CloudResource).order_by(CloudResource.id.asc()).all()
    for resource in resources:
        draft = evaluate_resource(resource)
        if draft is None:
            continue
        recommendation = to_recommendation(resource, draft)
        db.add(recommendation)
        db.flush()
        pack = build_remediation_pack(recommendation, resource)
        db.add(pack)
        created.append(recommendation)
    record_audit_event(db, "recommendation_run", "latest", "RULE_ENGINE_RUN", {"resources_scanned": len(resources), "recommendations_created": len(created)})
    db.commit()
    return (
        db.query(Recommendation)
        .options(selectinload(Recommendation.resource))
        .order_by(Recommendation.estimated_monthly_savings.desc(), Recommendation.id.asc())
        .all()
    )


@router.get("/recommendations", response_model=list[RecommendationRead])
def list_recommendations(db: Session = Depends(get_db)):
    return (
        db.query(Recommendation)
        .options(selectinload(Recommendation.resource))
        .order_by(Recommendation.estimated_monthly_savings.desc(), Recommendation.id.asc())
        .all()
    )


@router.get("/recommendations/{recommendation_id}", response_model=RecommendationRead)
def get_recommendation(recommendation_id: int, db: Session = Depends(get_db)):
    recommendation = (
        db.query(Recommendation)
        .options(selectinload(Recommendation.resource))
        .filter(Recommendation.id == recommendation_id)
        .first()
    )
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found.")
    return recommendation


@router.get("/recommendations/{recommendation_id}/remediation-pack", response_model=RemediationPackRead)
def get_remediation_pack(recommendation_id: int, db: Session = Depends(get_db)):
    pack = db.query(RemediationPack).filter(RemediationPack.recommendation_id == recommendation_id).first()
    if not pack:
        raise HTTPException(status_code=404, detail="Remediation pack not found.")
    return pack


@router.post("/recommendations/{recommendation_id}/approve", response_model=RecommendationRead)
def approve_recommendation(recommendation_id: int, db: Session = Depends(get_db)):
    recommendation = _get_recommendation_or_404(db, recommendation_id)
    if recommendation.status == "REJECTED":
        raise HTTPException(status_code=409, detail="Rejected recommendations cannot be approved.")
    recommendation.status = "APPROVED"
    recommendation.updated_at = datetime.utcnow()
    record_audit_event(db, "recommendation", recommendation.id, "RECOMMENDATION_APPROVED", {"resource_id": recommendation.resource.resource_id})
    db.commit()
    db.refresh(recommendation)
    return recommendation


@router.post("/recommendations/{recommendation_id}/reject", response_model=RecommendationRead)
def reject_recommendation(recommendation_id: int, db: Session = Depends(get_db)):
    recommendation = _get_recommendation_or_404(db, recommendation_id)
    if recommendation.status == "SIMULATED_EXECUTION":
        raise HTTPException(status_code=409, detail="Simulated recommendations cannot be rejected afterward in the MVP workflow.")
    recommendation.status = "REJECTED"
    recommendation.updated_at = datetime.utcnow()
    record_audit_event(db, "recommendation", recommendation.id, "RECOMMENDATION_REJECTED", {"resource_id": recommendation.resource.resource_id})
    db.commit()
    db.refresh(recommendation)
    return recommendation


@router.post("/recommendations/{recommendation_id}/simulate", response_model=RecommendationRead)
def simulate_recommendation(recommendation_id: int, db: Session = Depends(get_db)):
    recommendation = _get_recommendation_or_404(db, recommendation_id)
    if recommendation.status != "APPROVED":
        raise HTTPException(status_code=409, detail="Recommendation must be APPROVED before simulation.")
    recommendation.status = "SIMULATED_EXECUTION"
    recommendation.updated_at = datetime.utcnow()
    if recommendation.remediation_pack:
        recommendation.remediation_pack.execution_mode = "SIMULATED"
    record_audit_event(
        db,
        "recommendation",
        recommendation.id,
        "SIMULATED_EXECUTION",
        {"resource_id": recommendation.resource.resource_id, "executed_real_command": False},
    )
    db.commit()
    db.refresh(recommendation)
    return recommendation


@router.get("/summary", response_model=SummaryRead)
def summary(db: Session = Depends(get_db)):
    return get_summary(db)


@router.get("/export/recommendations.csv")
def export_recommendations(db: Session = Depends(get_db)):
    recommendations = db.query(Recommendation).options(selectinload(Recommendation.resource)).order_by(Recommendation.id.asc()).all()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "id",
        "provider",
        "resource_id",
        "resource_type",
        "region",
        "finding_type",
        "estimated_monthly_savings",
        "estimated_annual_savings",
        "confidence",
        "risk_level",
        "recommended_action",
        "status",
    ])
    for rec in recommendations:
        writer.writerow([
            rec.id,
            rec.resource.provider,
            rec.resource.resource_id,
            rec.resource.resource_type,
            rec.resource.region,
            rec.finding_type,
            rec.estimated_monthly_savings,
            rec.estimated_annual_savings,
            rec.confidence,
            rec.risk_level,
            rec.recommended_action,
            rec.status,
        ])
    record_audit_event(db, "recommendations", "csv", "RECOMMENDATIONS_EXPORTED", {"count": len(recommendations)})
    db.commit()
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=recommendations.csv"},
    )


@router.get("/audit-events", response_model=list[AuditEventRead])
def list_audit_events(db: Session = Depends(get_db)):
    return db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(100).all()


def _get_recommendation_or_404(db: Session, recommendation_id: int) -> Recommendation:
    recommendation = (
        db.query(Recommendation)
        .options(selectinload(Recommendation.resource), selectinload(Recommendation.remediation_pack))
        .filter(Recommendation.id == recommendation_id)
        .first()
    )
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found.")
    return recommendation
