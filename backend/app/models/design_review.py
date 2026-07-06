import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import DesignReviewCategoryEnum, DesignReviewStatusEnum, SeverityEnum
from app.models.mixins import TimestampMixin, UUIDPKMixin


class DesignReviewSubmission(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "design_review_submissions"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    reviewed_by: Mapped[str] = mapped_column(String(255), nullable=True)
    review_date: Mapped[date] = mapped_column(Date, nullable=True)
    status: Mapped[DesignReviewStatusEnum] = mapped_column(
        Enum(DesignReviewStatusEnum, name="design_review_status_enum"), default=DesignReviewStatusEnum.processing
    )
    summary: Mapped[str] = mapped_column(Text, nullable=True)

    findings: Mapped[list["DesignReviewFinding"]] = relationship(
        back_populates="submission", cascade="all, delete-orphan"
    )


class DesignReviewFinding(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "design_review_findings"

    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("design_review_submissions.id"), nullable=False, index=True
    )
    category: Mapped[DesignReviewCategoryEnum] = mapped_column(
        Enum(DesignReviewCategoryEnum, name="design_review_category_enum"), nullable=False
    )
    severity: Mapped[SeverityEnum] = mapped_column(Enum(SeverityEnum, name="severity_enum"), default=SeverityEnum.medium)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sheet_reference: Mapped[str] = mapped_column(String(128), nullable=True)
    recommendation: Mapped[str] = mapped_column(Text, nullable=True)

    submission: Mapped["DesignReviewSubmission"] = relationship(back_populates="findings")
