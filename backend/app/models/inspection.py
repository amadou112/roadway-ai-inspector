import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import InspectionReportStatusEnum, SeverityEnum
from app.models.mixins import TimestampMixin, UUIDPKMixin


class DailyInspectionReport(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "daily_inspection_reports"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    inspector_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    inspector_name: Mapped[str] = mapped_column(String(255), nullable=True)

    weather_temp_f: Mapped[int] = mapped_column(Integer, nullable=True)
    weather_conditions: Mapped[str] = mapped_column(String(255), nullable=True)

    contractor_activities: Mapped[list] = mapped_column(JSONB, default=list)
    equipment_onsite: Mapped[list] = mapped_column(JSONB, default=list)
    materials_delivered: Mapped[list] = mapped_column(JSONB, default=list)
    quantities_installed: Mapped[list] = mapped_column(JSONB, default=list)
    deficiencies: Mapped[list] = mapped_column(JSONB, default=list)
    photos: Mapped[list] = mapped_column(JSONB, default=list)

    narrative: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[InspectionReportStatusEnum] = mapped_column(
        Enum(InspectionReportStatusEnum, name="inspection_report_status_enum"),
        default=InspectionReportStatusEnum.draft,
    )


class InspectionFinding(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "inspection_findings"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    inspection_report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("daily_inspection_reports.id"), nullable=True, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    category: Mapped[str] = mapped_column(String(128), nullable=True)
    severity: Mapped[SeverityEnum] = mapped_column(Enum(SeverityEnum, name="severity_enum"), default=SeverityEnum.medium)
    status: Mapped[str] = mapped_column(String(32), default="open")
