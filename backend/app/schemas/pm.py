import uuid
from datetime import date, datetime

from pydantic import BaseModel

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


# --- RFI ---
class RFIBase(BaseModel):
    number: str
    subject: str
    question: str
    status: RFIStatusEnum = RFIStatusEnum.open
    priority: PriorityEnum = PriorityEnum.medium
    submitted_by: str | None = None
    assigned_to: str | None = None
    submitted_date: date | None = None
    due_date: date | None = None
    response: str | None = None
    cost_impact: float = 0
    schedule_impact_days: int = 0


class RFICreate(RFIBase):
    pass


class RFIUpdate(BaseModel):
    status: RFIStatusEnum | None = None
    response: str | None = None
    assigned_to: str | None = None
    cost_impact: float | None = None
    schedule_impact_days: int | None = None


class RFIOut(RFIBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Submittal ---
class SubmittalBase(BaseModel):
    number: str
    spec_section: str | None = None
    title: str
    status: SubmittalStatusEnum = SubmittalStatusEnum.pending
    submitted_date: date | None = None
    reviewed_date: date | None = None
    reviewer: str | None = None
    revision: int = 0
    notes: str | None = None


class SubmittalCreate(SubmittalBase):
    pass


class SubmittalUpdate(BaseModel):
    status: SubmittalStatusEnum | None = None
    reviewer: str | None = None
    reviewed_date: date | None = None
    notes: str | None = None


class SubmittalOut(SubmittalBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Risk ---
class RiskBase(BaseModel):
    title: str
    category: str | None = None
    description: str | None = None
    likelihood: int = 3
    impact: int = 3
    status: RiskStatusEnum = RiskStatusEnum.open
    owner: str | None = None
    mitigation_plan: str | None = None


class RiskCreate(RiskBase):
    pass


class RiskUpdate(BaseModel):
    status: RiskStatusEnum | None = None
    likelihood: int | None = None
    impact: int | None = None
    mitigation_plan: str | None = None


class RiskOut(RiskBase):
    id: uuid.UUID
    project_id: uuid.UUID
    risk_score: int
    created_at: datetime

    model_config = {"from_attributes": True}


# --- NCR ---
class NCRBase(BaseModel):
    ncr_number: str
    description: str
    location: str | None = None
    spec_reference: str | None = None
    severity: SeverityEnum = SeverityEnum.medium
    status: NCRStatusEnum = NCRStatusEnum.open
    identified_by: str | None = None
    identified_date: date | None = None
    corrective_action: str | None = None
    closed_date: date | None = None


class NCRCreate(NCRBase):
    pass


class NCRUpdate(BaseModel):
    status: NCRStatusEnum | None = None
    corrective_action: str | None = None
    closed_date: date | None = None


class NCROut(NCRBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Safety Issue ---
class SafetyIssueBase(BaseModel):
    description: str
    location: str | None = None
    severity: SeverityEnum = SeverityEnum.medium
    category: SafetyCategoryEnum = SafetyCategoryEnum.other
    status: SafetyStatusEnum = SafetyStatusEnum.open
    reported_by: str | None = None
    reported_date: date | None = None
    corrective_action: str | None = None


class SafetyIssueCreate(SafetyIssueBase):
    pass


class SafetyIssueUpdate(BaseModel):
    status: SafetyStatusEnum | None = None
    corrective_action: str | None = None


class SafetyIssueOut(SafetyIssueBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Schedule Item ---
class ScheduleItemBase(BaseModel):
    task_name: str
    planned_start: date | None = None
    planned_finish: date | None = None
    actual_start: date | None = None
    actual_finish: date | None = None
    percent_complete: int = 0
    status: ScheduleStatusEnum = ScheduleStatusEnum.on_track
    predecessor: str | None = None


class ScheduleItemCreate(ScheduleItemBase):
    pass


class ScheduleItemUpdate(BaseModel):
    percent_complete: int | None = None
    status: ScheduleStatusEnum | None = None
    actual_start: date | None = None
    actual_finish: date | None = None


class ScheduleItemOut(ScheduleItemBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Cost Item ---
class CostItemBase(BaseModel):
    category: str
    budget_amount: float = 0
    committed_amount: float = 0
    actual_amount: float = 0
    change_order_number: str | None = None


class CostItemCreate(CostItemBase):
    pass


class CostItemUpdate(BaseModel):
    committed_amount: float | None = None
    actual_amount: float | None = None


class CostItemOut(CostItemBase):
    id: uuid.UUID
    project_id: uuid.UUID
    variance: float
    created_at: datetime

    model_config = {"from_attributes": True}
