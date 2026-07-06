import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.rate_limit import LLM_RATE_LIMIT, limiter
from app.db.session import get_db
from app.models.enums import ReportTypeEnum
from app.models.project import Project
from app.models.report import GeneratedReport
from app.models.user import User
from app.schemas.report import GenerateReportRequest, GeneratedReportOut
from app.services import report_service

router = APIRouter(prefix="/api/v1/projects/{project_id}/reports", tags=["reports"])


@router.get("", response_model=list[GeneratedReportOut])
def list_reports(project_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return (
        db.query(GeneratedReport)
        .filter(GeneratedReport.project_id == project_id)
        .order_by(GeneratedReport.created_at.desc())
        .all()
    )


@router.post("", response_model=GeneratedReportOut)
@limiter.limit(LLM_RATE_LIMIT)
def generate_report(
    request: Request,
    project_id: uuid.UUID,
    payload: GenerateReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    generated_by = payload.generated_by or current_user.full_name

    if payload.report_type == ReportTypeEnum.weekly_status:
        file_path = report_service.generate_weekly_status_report(
            db, project, payload.period_start, payload.period_end, generated_by
        )
        title = "Weekly Project Status Report"
    else:
        file_path = report_service.generate_risk_summary_report(db, project, generated_by)
        title = "Project Risk Summary Report"

    record = GeneratedReport(
        project_id=project_id,
        report_type=payload.report_type,
        title=title,
        period_start=payload.period_start,
        period_end=payload.period_end,
        file_path=file_path,
        generated_by=generated_by,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{report_id}/pdf")
def download_report(
    project_id: uuid.UUID, report_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    record = db.get(GeneratedReport, report_id)
    if not record or record.project_id != project_id:
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(record.file_path, media_type="application/pdf", filename=f"{record.title}.pdf")
