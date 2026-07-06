import enum


class RoleEnum(str, enum.Enum):
    program_manager = "program_manager"
    project_manager = "project_manager"
    resident_engineer = "resident_engineer"
    inspector = "inspector"
    designer = "designer"
    contractor = "contractor"
    dot_executive = "dot_executive"


class DocTypeEnum(str, enum.Enum):
    spec = "spec"
    fhwa_manual = "fhwa_manual"
    inspection_report = "inspection_report"
    rfi = "rfi"
    submittal = "submittal"
    plan_sheet = "plan_sheet"
    daily_report = "daily_report"
    other = "other"


class DocStatusEnum(str, enum.Enum):
    processing = "processing"
    indexed = "indexed"
    failed = "failed"


class PriorityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class SeverityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class RFIStatusEnum(str, enum.Enum):
    open = "open"
    answered = "answered"
    closed = "closed"


class SubmittalStatusEnum(str, enum.Enum):
    pending = "pending"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"
    resubmit_required = "resubmit_required"


class RiskStatusEnum(str, enum.Enum):
    open = "open"
    mitigated = "mitigated"
    closed = "closed"


class NCRStatusEnum(str, enum.Enum):
    open = "open"
    corrective_action = "corrective_action"
    closed = "closed"


class SafetyCategoryEnum(str, enum.Enum):
    fall_protection = "fall_protection"
    equipment = "equipment"
    traffic_control = "traffic_control"
    ppe = "ppe"
    electrical = "electrical"
    excavation = "excavation"
    other = "other"


class SafetyStatusEnum(str, enum.Enum):
    open = "open"
    corrective_action = "corrective_action"
    closed = "closed"


class ScheduleStatusEnum(str, enum.Enum):
    on_track = "on_track"
    at_risk = "at_risk"
    delayed = "delayed"
    complete = "complete"


class InspectionReportStatusEnum(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"


class DesignReviewCategoryEnum(str, enum.Enum):
    missing_item = "missing_item"
    conflict = "conflict"
    risk = "risk"
    constructability = "constructability"
    safety = "safety"
    compliance = "compliance"


class DesignReviewStatusEnum(str, enum.Enum):
    processing = "processing"
    completed = "completed"
    failed = "failed"


class ReportTypeEnum(str, enum.Enum):
    weekly_status = "weekly_status"
    risk_summary = "risk_summary"


class BridgeConditionEnum(str, enum.Enum):
    good = "good"
    fair = "fair"
    poor = "poor"
    unknown = "unknown"
