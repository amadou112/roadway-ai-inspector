import uuid
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.enums import (
    NCRStatusEnum,
    RFIStatusEnum,
    RiskStatusEnum,
    SafetyStatusEnum,
    ScheduleStatusEnum,
)
from app.models.inspection import InspectionFinding
from app.models.pm import RFI, CostItem, NonConformanceReport, Risk, SafetyIssue, ScheduleItem, Submittal
from app.models.user import User
from app.schemas.dashboard import CountByLabel, DashboardOverview, RiskHeatmapCell

router = APIRouter(prefix="/api/v1/projects/{project_id}/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverview)
def overview(project_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    open_rfis = db.query(RFI).filter(RFI.project_id == project_id, RFI.status == RFIStatusEnum.open)
    overdue_rfis = open_rfis.filter(RFI.due_date < date.today()).count()

    schedule_counts = dict(
        db.query(ScheduleItem.status, func.count(ScheduleItem.id))
        .filter(ScheduleItem.project_id == project_id)
        .group_by(ScheduleItem.status)
        .all()
    )
    cost_totals = db.query(
        func.coalesce(func.sum(CostItem.budget_amount), 0),
        func.coalesce(func.sum(CostItem.actual_amount), 0),
        func.coalesce(func.sum(CostItem.committed_amount), 0),
    ).filter(CostItem.project_id == project_id).first()

    return DashboardOverview(
        open_rfis=open_rfis.count(),
        overdue_rfis=overdue_rfis,
        open_submittals=db.query(Submittal).filter(Submittal.project_id == project_id).count(),
        open_risks=db.query(Risk).filter(Risk.project_id == project_id, Risk.status == RiskStatusEnum.open).count(),
        high_impact_risks=db.query(Risk)
        .filter(Risk.project_id == project_id, Risk.status == RiskStatusEnum.open, Risk.impact >= 4)
        .count(),
        open_ncrs=db.query(NonConformanceReport)
        .filter(NonConformanceReport.project_id == project_id, NonConformanceReport.status != NCRStatusEnum.closed)
        .count(),
        open_safety_issues=db.query(SafetyIssue)
        .filter(SafetyIssue.project_id == project_id, SafetyIssue.status != SafetyStatusEnum.closed)
        .count(),
        open_inspection_findings=db.query(InspectionFinding)
        .filter(InspectionFinding.project_id == project_id, InspectionFinding.status == "open")
        .count(),
        schedule_on_track=schedule_counts.get(ScheduleStatusEnum.on_track, 0),
        schedule_at_risk=schedule_counts.get(ScheduleStatusEnum.at_risk, 0),
        schedule_delayed=schedule_counts.get(ScheduleStatusEnum.delayed, 0),
        budget_total=float(cost_totals[0]),
        actual_total=float(cost_totals[1]),
        committed_total=float(cost_totals[2]),
        variance_total=float(cost_totals[0]) - float(cost_totals[1]),
    )


@router.get("/risk-heatmap", response_model=list[RiskHeatmapCell])
def risk_heatmap(project_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = (
        db.query(Risk.likelihood, Risk.impact, func.count(Risk.id))
        .filter(Risk.project_id == project_id, Risk.status == RiskStatusEnum.open)
        .group_by(Risk.likelihood, Risk.impact)
        .all()
    )
    return [RiskHeatmapCell(likelihood=l, impact=i, count=c) for l, i, c in rows]


@router.get("/safety-by-category", response_model=list[CountByLabel])
def safety_by_category(project_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = (
        db.query(SafetyIssue.category, func.count(SafetyIssue.id))
        .filter(SafetyIssue.project_id == project_id)
        .group_by(SafetyIssue.category)
        .all()
    )
    return [CountByLabel(label=cat.value, count=count) for cat, count in rows]


@router.get("/ncr-trend", response_model=list[CountByLabel])
def ncr_trend(project_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    month_expr = func.to_char(NonConformanceReport.identified_date, "YYYY-MM")
    rows = (
        db.query(month_expr, func.count(NonConformanceReport.id))
        .filter(NonConformanceReport.project_id == project_id, NonConformanceReport.identified_date.isnot(None))
        .group_by(month_expr)
        .order_by(month_expr)
        .all()
    )
    return [CountByLabel(label=label, count=count) for label, count in rows]
