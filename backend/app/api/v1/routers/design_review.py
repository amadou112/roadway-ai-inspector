import os
import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.core.rate_limit import LLM_RATE_LIMIT, limiter
from app.db.session import get_db
from app.models.design_review import DesignReviewFinding, DesignReviewSubmission
from app.models.document import Document
from app.models.enums import DesignReviewStatusEnum
from app.models.project import Project
from app.models.user import User
from app.schemas.design_review import DesignReviewSubmissionCreate, DesignReviewSubmissionOut
from app.services import design_review_service, ingestion, pdf_service

router = APIRouter(prefix="/api/v1/projects/{project_id}/design-reviews", tags=["design-review"])
settings = get_settings()


@router.get("", response_model=list[DesignReviewSubmissionOut])
def list_reviews(project_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return (
        db.query(DesignReviewSubmission)
        .filter(DesignReviewSubmission.project_id == project_id)
        .order_by(DesignReviewSubmission.created_at.desc())
        .all()
    )


@router.post("", response_model=DesignReviewSubmissionOut)
@limiter.limit(LLM_RATE_LIMIT)
def create_review(
    request: Request,
    project_id: uuid.UUID,
    payload: DesignReviewSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = db.get(Document, payload.document_id)
    if not document or document.project_id != project_id:
        raise HTTPException(status_code=404, detail="Document not found for this project")

    submission = DesignReviewSubmission(
        project_id=project_id,
        document_id=payload.document_id,
        reviewed_by=payload.reviewed_by or current_user.full_name,
        review_date=date.today(),
        status=DesignReviewStatusEnum.processing,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    try:
        pages = ingestion.extract_pages(document.file_path)
        design_text = "\n".join(pages)
        findings = design_review_service.review_design_document(str(project_id), design_text)
        for f in findings:
            db.add(
                DesignReviewFinding(
                    submission_id=submission.id,
                    category=f.get("category", "compliance"),
                    severity=f.get("severity", "medium"),
                    description=f.get("description", ""),
                    sheet_reference=f.get("sheet_reference"),
                    recommendation=f.get("recommendation"),
                )
            )
        submission.status = DesignReviewStatusEnum.completed
        submission.summary = f"{len(findings)} findings identified across constructability, safety, and compliance review."
    except Exception as exc:  # noqa: BLE001
        submission.status = DesignReviewStatusEnum.failed
        submission.summary = f"Review failed: {exc}"

    db.commit()
    db.refresh(submission)
    return submission


@router.get("/{submission_id}", response_model=DesignReviewSubmissionOut)
def get_review(
    project_id: uuid.UUID, submission_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    submission = db.get(DesignReviewSubmission, submission_id)
    if not submission or submission.project_id != project_id:
        raise HTTPException(status_code=404, detail="Not found")
    return submission


@router.get("/{submission_id}/pdf")
def download_review_pdf(
    project_id: uuid.UUID, submission_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    submission = db.get(DesignReviewSubmission, submission_id)
    if not submission or submission.project_id != project_id:
        raise HTTPException(status_code=404, detail="Not found")
    project = db.get(Project, project_id)
    document = db.get(Document, submission.document_id)

    findings_rows = [["Category", "Severity", "Description", "Sheet", "Recommendation"]] + [
        [f.category.value, f.severity.value, f.description, f.sheet_reference or "-", f.recommendation or "-"]
        for f in submission.findings
    ]

    reports_dir = os.path.join(settings.storage_dir, str(project_id), "design_review_pdfs")
    os.makedirs(reports_dir, exist_ok=True)
    file_path = os.path.join(reports_dir, f"{submission.id}.pdf")

    pdf_service.build_pdf(
        file_path=file_path,
        title="Design Review Report",
        subtitle=f"{project.name if project else ''} — Document: {document.title if document else ''} — "
        f"Reviewed by {submission.reviewed_by}",
        sections=[("Summary", submission.summary or "")],
        tables=[("Findings", findings_rows)],
    )
    return FileResponse(file_path, media_type="application/pdf", filename=f"design_review_{submission.id}.pdf")
