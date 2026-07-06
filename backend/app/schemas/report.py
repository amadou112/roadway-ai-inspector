import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.enums import ReportTypeEnum


class GenerateReportRequest(BaseModel):
    report_type: ReportTypeEnum
    period_start: date | None = None
    period_end: date | None = None
    generated_by: str | None = None


class GeneratedReportOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    report_type: ReportTypeEnum
    title: str
    period_start: date | None
    period_end: date | None
    generated_by: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
