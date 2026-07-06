import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel

from app.models.enums import InspectionReportStatusEnum, SeverityEnum


class DailyInspectionReportCreate(BaseModel):
    report_date: date
    inspector_name: str | None = None
    weather_temp_f: int | None = None
    weather_conditions: str | None = None
    contractor_activities: list[str] = []
    equipment_onsite: list[str] = []
    materials_delivered: list[dict[str, Any]] = []
    quantities_installed: list[dict[str, Any]] = []
    deficiencies: list[dict[str, Any]] = []
    photos: list[str] = []


class DailyInspectionReportOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    report_date: date
    inspector_name: str | None
    weather_temp_f: int | None
    weather_conditions: str | None
    contractor_activities: list
    equipment_onsite: list
    materials_delivered: list
    quantities_installed: list
    deficiencies: list
    photos: list
    narrative: str | None
    status: InspectionReportStatusEnum
    created_at: datetime

    model_config = {"from_attributes": True}


class InspectionFindingOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    inspection_report_id: uuid.UUID | None
    description: str
    location: str | None
    category: str | None
    severity: SeverityEnum
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
