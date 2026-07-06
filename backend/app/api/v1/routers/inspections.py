import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.core.rate_limit import LLM_RATE_LIMIT, limiter
from app.db.session import get_db
from app.models.inspection import DailyInspectionReport
from app.models.project import Project
from app.models.user import User
from app.schemas.inspection import DailyInspectionReportCreate, DailyInspectionReportOut
from app.services import inspection_service, pdf_service

router = APIRouter(prefix="/api/v1/projects/{project_id}/inspection-reports", tags=["inspections"])
settings = get_settings()


@router.get("", response_model=list[DailyInspectionReportOut])
def list_reports(project_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return (
        db.query(DailyInspectionReport)
        .filter(DailyInspectionReport.project_id == project_id)
        .order_by(DailyInspectionReport.report_date.desc())
        .all()
    )


@router.post("", response_model=DailyInspectionReportOut)
@limiter.limit(LLM_RATE_LIMIT)
def create_report(
    request: Request,
    project_id: uuid.UUID,
    payload: DailyInspectionReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = DailyInspectionReport(
        project_id=project_id,
        inspector_id=current_user.id,
        **payload.model_dump(),
    )
    if not report.inspector_name:
        report.inspector_name = current_user.full_name

    report.narrative = inspection_service.generate_narrative(report)

    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/{report_id}", response_model=DailyInspectionReportOut)
def get_report(
    project_id: uuid.UUID, report_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    report = db.get(DailyInspectionReport, report_id)
    if not report or report.project_id != project_id:
        raise HTTPException(status_code=404, detail="Not found")
    return report


@router.get("/{report_id}/pdf")
def download_report_pdf(
    project_id: uuid.UUID, report_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    report = db.get(DailyInspectionReport, report_id)
    if not report or report.project_id != project_id:
        raise HTTPException(status_code=404, detail="Not found")
    project = db.get(Project, project_id)

    reports_dir = os.path.join(settings.storage_dir, str(project_id), "inspection_pdfs")
    os.makedirs(reports_dir, exist_ok=True)
    file_path = os.path.join(reports_dir, f"{report.id}.pdf")

    quantities_rows = [["Item", "Quantity", "Unit"]] + [
        [q.get("item", "-"), str(q.get("quantity", "-")), q.get("unit", "-")] for q in report.quantities_installed
    ] or [["Item", "Quantity", "Unit"], ["None recorded", "-", "-"]]

    deficiency_rows = [["Description", "Severity", "Location"]] + [
        [d.get("description", "-"), d.get("severity", "-"), d.get("location", "-")] for d in report.deficiencies
    ] or [["Description", "Severity", "Location"], ["None recorded", "-", "-"]]

    pdf_service.build_pdf(
        file_path=file_path,
        title="Daily Inspection Report",
        subtitle=f"{project.name if project else ''} — {report.report_date.isoformat()} — Inspector: {report.inspector_name}",
        sections=[("Narrative Report", report.narrative or "")],
        tables=[("Quantities Installed", quantities_rows), ("Deficiencies", deficiency_rows)],
    )
    return FileResponse(file_path, media_type="application/pdf", filename=f"daily_inspection_report_{report.report_date}.pdf")
