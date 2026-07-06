import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import ReportTypeEnum
from app.models.mixins import TimestampMixin, UUIDPKMixin


class GeneratedReport(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "generated_reports"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    report_type: Mapped[ReportTypeEnum] = mapped_column(Enum(ReportTypeEnum, name="report_type_enum"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=True)
    period_end: Mapped[date] = mapped_column(Date, nullable=True)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    generated_by: Mapped[str] = mapped_column(String(255), nullable=True)
