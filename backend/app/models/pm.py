import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import (
    NCRStatusEnum,
    PriorityEnum,
    RFIStatusEnum,
    RiskStatusEnum,
    SafetyCategoryEnum,
    SafetyStatusEnum,
    ScheduleStatusEnum,
    SeverityEnum,
    SubmittalStatusEnum,
)
from app.models.mixins import TimestampMixin, UUIDPKMixin


class RFI(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "rfis"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    number: Mapped[str] = mapped_column(String(32), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[RFIStatusEnum] = mapped_column(Enum(RFIStatusEnum, name="rfi_status_enum"), default=RFIStatusEnum.open)
    priority: Mapped[PriorityEnum] = mapped_column(Enum(PriorityEnum, name="priority_enum"), default=PriorityEnum.medium)
    submitted_by: Mapped[str] = mapped_column(String(255), nullable=True)
    assigned_to: Mapped[str] = mapped_column(String(255), nullable=True)
    submitted_date: Mapped[date] = mapped_column(Date, nullable=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=True)
    response: Mapped[str] = mapped_column(Text, nullable=True)
    cost_impact: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    schedule_impact_days: Mapped[int] = mapped_column(Integer, default=0)


class Submittal(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "submittals"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    number: Mapped[str] = mapped_column(String(32), nullable=False)
    spec_section: Mapped[str] = mapped_column(String(64), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[SubmittalStatusEnum] = mapped_column(
        Enum(SubmittalStatusEnum, name="submittal_status_enum"), default=SubmittalStatusEnum.pending
    )
    submitted_date: Mapped[date] = mapped_column(Date, nullable=True)
    reviewed_date: Mapped[date] = mapped_column(Date, nullable=True)
    reviewer: Mapped[str] = mapped_column(String(255), nullable=True)
    revision: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(Text, nullable=True)


class Risk(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "risks"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    likelihood: Mapped[int] = mapped_column(Integer, default=3)
    impact: Mapped[int] = mapped_column(Integer, default=3)
    status: Mapped[RiskStatusEnum] = mapped_column(Enum(RiskStatusEnum, name="risk_status_enum"), default=RiskStatusEnum.open)
    owner: Mapped[str] = mapped_column(String(255), nullable=True)
    mitigation_plan: Mapped[str] = mapped_column(Text, nullable=True)

    @property
    def risk_score(self) -> int:
        return self.likelihood * self.impact


class NonConformanceReport(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "non_conformance_reports"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    ncr_number: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    spec_reference: Mapped[str] = mapped_column(String(128), nullable=True)
    severity: Mapped[SeverityEnum] = mapped_column(Enum(SeverityEnum, name="severity_enum"), default=SeverityEnum.medium)
    status: Mapped[NCRStatusEnum] = mapped_column(Enum(NCRStatusEnum, name="ncr_status_enum"), default=NCRStatusEnum.open)
    identified_by: Mapped[str] = mapped_column(String(255), nullable=True)
    identified_date: Mapped[date] = mapped_column(Date, nullable=True)
    corrective_action: Mapped[str] = mapped_column(Text, nullable=True)
    closed_date: Mapped[date] = mapped_column(Date, nullable=True)


class SafetyIssue(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "safety_issues"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    severity: Mapped[SeverityEnum] = mapped_column(Enum(SeverityEnum, name="severity_enum"), default=SeverityEnum.medium)
    category: Mapped[SafetyCategoryEnum] = mapped_column(
        Enum(SafetyCategoryEnum, name="safety_category_enum"), default=SafetyCategoryEnum.other
    )
    status: Mapped[SafetyStatusEnum] = mapped_column(Enum(SafetyStatusEnum, name="safety_status_enum"), default=SafetyStatusEnum.open)
    reported_by: Mapped[str] = mapped_column(String(255), nullable=True)
    reported_date: Mapped[date] = mapped_column(Date, nullable=True)
    corrective_action: Mapped[str] = mapped_column(Text, nullable=True)


class ScheduleItem(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "schedule_items"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    planned_start: Mapped[date] = mapped_column(Date, nullable=True)
    planned_finish: Mapped[date] = mapped_column(Date, nullable=True)
    actual_start: Mapped[date] = mapped_column(Date, nullable=True)
    actual_finish: Mapped[date] = mapped_column(Date, nullable=True)
    percent_complete: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[ScheduleStatusEnum] = mapped_column(
        Enum(ScheduleStatusEnum, name="schedule_status_enum"), default=ScheduleStatusEnum.on_track
    )
    predecessor: Mapped[str] = mapped_column(String(255), nullable=True)


class CostItem(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "cost_items"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(128), nullable=False)
    budget_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    committed_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    actual_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    change_order_number: Mapped[str] = mapped_column(String(64), nullable=True)

    @property
    def variance(self) -> float:
        return float(self.budget_amount) - float(self.actual_amount)
