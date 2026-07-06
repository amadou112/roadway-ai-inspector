import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.enums import DesignReviewCategoryEnum, DesignReviewStatusEnum, SeverityEnum


class DesignReviewFindingOut(BaseModel):
    id: uuid.UUID
    category: DesignReviewCategoryEnum
    severity: SeverityEnum
    description: str
    sheet_reference: str | None
    recommendation: str | None

    model_config = {"from_attributes": True}


class DesignReviewSubmissionCreate(BaseModel):
    document_id: uuid.UUID
    reviewed_by: str | None = None


class DesignReviewSubmissionOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    document_id: uuid.UUID
    reviewed_by: str | None
    review_date: date | None
    status: DesignReviewStatusEnum
    summary: str | None
    created_at: datetime
    findings: list[DesignReviewFindingOut] = []

    model_config = {"from_attributes": True}
