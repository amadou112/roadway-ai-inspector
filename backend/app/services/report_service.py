import os
import uuid
from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.enums import NCRStatusEnum, RFIStatusEnum, RiskStatusEnum, SafetyStatusEnum
from app.models.pm import RFI, CostItem, NonConformanceReport, Risk, SafetyIssue, ScheduleItem, Submittal
from app.models.project import Project
from app.services import pdf_service
from app.services.llm_provider import chat_completion

settings = get_settings()

WEEKLY_SUMMARY_PROMPT = """You are a DOT program management office assistant writing the executive \
narrative for a weekly project status report. Given the KPI snapshot below, write a concise \
3-5 sentence executive summary highlighting overall health, top risks/issues to watch, and any \
notable schedule or cost concerns. Professional, direct, suitable for a DOT executive audience."""

RISK_SUMMARY_PROMPT = """You are a DOT program risk manager. Given the list of open project risks \
below (title, category, likelihood, impact, score, mitigation plan), write a concise 3-5 sentence \
narrative summarizing the overall risk posture and the top priorities for the coming weeks."""


def _project_kpis(db: Session, project_id: uuid.UUID) -> dict:
    open_rfis = db.query(RFI).filter(RFI.project_id == project_id, RFI.status == RFIStatusEnum.open).count()
    open_submittals = db.query(Submittal).filter(Submittal.project_id == project_id).count()
    open_risks = db.query(Risk).filter(Risk.project_id == project_id, Risk.status == RiskStatusEnum.open).count()
    open_ncrs = (
        db.query(NonConformanceReport)
        .filter(NonConformanceReport.project_id == project_id, NonConformanceReport.status != NCRStatusEnum.closed)
        .count()
    )
    open_safety = (
        db.query(SafetyIssue)
        .filter(SafetyIssue.project_id == project_id, SafetyIssue.status != SafetyStatusEnum.closed)
        .count()
    )
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

    return {
        "open_rfis": open_rfis,
        "open_submittals": open_submittals,
        "open_risks": open_risks,
        "open_ncrs": open_ncrs,
        "open_safety_issues": open_safety,
        "schedule_counts": {str(k.value if hasattr(k, "value") else k): v for k, v in schedule_counts.items()},
        "budget_total": float(cost_totals[0]),
        "actual_total": float(cost_totals[1]),
        "committed_total": float(cost_totals[2]),
    }


def generate_weekly_status_report(
    db: Session, project: Project, period_start: date | None, period_end: date | None, generated_by: str | None
) -> str:
    kpis = _project_kpis(db, project.id)
    summary_prompt = (
        f"Project: {project.name} ({project.route}, {project.county} County, {project.state})\n"
        f"KPI snapshot: {kpis}"
    )
    narrative = chat_completion(WEEKLY_SUMMARY_PROMPT, summary_prompt)

    kpi_rows = [["Metric", "Value"]] + [
        ["Open RFIs", str(kpis["open_rfis"])],
        ["Open Submittals", str(kpis["open_submittals"])],
        ["Open Risks", str(kpis["open_risks"])],
        ["Open NCRs", str(kpis["open_ncrs"])],
        ["Open Safety Issues", str(kpis["open_safety_issues"])],
        ["Budget Total", f"${kpis['budget_total']:,.2f}"],
        ["Actual Spend", f"${kpis['actual_total']:,.2f}"],
        ["Committed", f"${kpis['committed_total']:,.2f}"],
    ]
    schedule_rows = [["Status", "Count"]] + [[k, str(v)] for k, v in kpis["schedule_counts"].items()] or [
        ["Status", "Count"],
        ["No schedule items", "0"],
    ]

    reports_dir = os.path.join(settings.storage_dir, str(project.id), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    file_name = f"weekly_status_{date.today().isoformat()}_{uuid.uuid4().hex[:8]}.pdf"
    file_path = os.path.join(reports_dir, file_name)

    pdf_service.build_pdf(
        file_path=file_path,
        title="Weekly Project Status Report",
        subtitle=f"{project.name} — Generated {date.today().isoformat()}"
        + (f" by {generated_by}" if generated_by else ""),
        sections=[("Executive Summary", narrative)],
        tables=[("Key Performance Indicators", kpi_rows), ("Schedule Status", schedule_rows)],
    )
    return file_path


def generate_risk_summary_report(
    db: Session, project: Project, generated_by: str | None
) -> str:
    risks = db.query(Risk).filter(Risk.project_id == project.id, Risk.status == RiskStatusEnum.open).all()
    risk_rows = [["Title", "Category", "Likelihood", "Impact", "Score", "Owner"]] + [
        [r.title, r.category or "-", str(r.likelihood), str(r.impact), str(r.risk_score), r.owner or "-"]
        for r in risks
    ]
    if len(risk_rows) == 1:
        risk_rows.append(["No open risks", "-", "-", "-", "-", "-"])

    risk_text = "\n".join(
        f"- {r.title} ({r.category}): likelihood={r.likelihood}, impact={r.impact}, "
        f"score={r.risk_score}, mitigation={r.mitigation_plan or 'none documented'}"
        for r in risks
    ) or "No open risks recorded."

    narrative = chat_completion(RISK_SUMMARY_PROMPT, risk_text)

    reports_dir = os.path.join(settings.storage_dir, str(project.id), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    file_name = f"risk_summary_{date.today().isoformat()}_{uuid.uuid4().hex[:8]}.pdf"
    file_path = os.path.join(reports_dir, file_name)

    pdf_service.build_pdf(
        file_path=file_path,
        title="Project Risk Summary Report",
        subtitle=f"{project.name} — Generated {date.today().isoformat()}"
        + (f" by {generated_by}" if generated_by else ""),
        sections=[("Risk Posture Summary", narrative)],
        tables=[("Open Risks", risk_rows)],
    )
    return file_path
