from datetime import date

import plotly.express as px
import streamlit as st
from sqlalchemy import func

from streamlit_common import CATEGORICAL, STATUS_COLORS, apply_page_style, get_db_session, init_app, sidebar_controls

apply_page_style()
init_app()

from app.models.enums import (  # noqa: E402
    NCRStatusEnum,
    RFIStatusEnum,
    RiskStatusEnum,
    SafetyStatusEnum,
    ScheduleStatusEnum,
)
from app.models.inspection import InspectionFinding  # noqa: E402
from app.models.pm import RFI, CostItem, NonConformanceReport, Risk, SafetyIssue, ScheduleItem, Submittal  # noqa: E402

with get_db_session() as db:
    current_user, project = sidebar_controls(db)

    if project is None:
        st.title("Roadway AI Inspector & Design Assistant")
        st.info("No projects found yet — the demo seed should create one automatically. Refresh in a moment.")
        st.stop()

    st.title("Program Dashboard")
    st.caption(f"{project.name} — {project.route or ''} · {project.county or ''} County, {project.state}")

    pid = project.id

    open_rfis_q = db.query(RFI).filter(RFI.project_id == pid, RFI.status == RFIStatusEnum.open)
    overdue_rfis = open_rfis_q.filter(RFI.due_date < date.today()).count()
    open_risks_q = db.query(Risk).filter(Risk.project_id == pid, Risk.status == RiskStatusEnum.open)
    high_impact_risks = open_risks_q.filter(Risk.impact >= 4).count()
    open_ncrs = (
        db.query(NonConformanceReport)
        .filter(NonConformanceReport.project_id == pid, NonConformanceReport.status != NCRStatusEnum.closed)
        .count()
    )
    open_safety = (
        db.query(SafetyIssue)
        .filter(SafetyIssue.project_id == pid, SafetyIssue.status != SafetyStatusEnum.closed)
        .count()
    )
    schedule_counts = dict(
        db.query(ScheduleItem.status, func.count(ScheduleItem.id))
        .filter(ScheduleItem.project_id == pid)
        .group_by(ScheduleItem.status)
        .all()
    )
    cost_totals = (
        db.query(
            func.coalesce(func.sum(CostItem.budget_amount), 0),
            func.coalesce(func.sum(CostItem.actual_amount), 0),
        )
        .filter(CostItem.project_id == pid)
        .first()
    )
    budget_total, actual_total = float(cost_totals[0]), float(cost_totals[1])

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Open RFIs", open_rfis_q.count(), f"{overdue_rfis} overdue" if overdue_rfis else None, delta_color="inverse")
    col2.metric("Open Submittals", db.query(Submittal).filter(Submittal.project_id == pid).count())
    col3.metric("Open Risks", open_risks_q.count(), f"{high_impact_risks} high-impact" if high_impact_risks else None, delta_color="inverse")
    col4.metric("Open NCRs", open_ncrs)
    col5.metric("Open Safety Issues", open_safety)

    col6, col7, col8 = st.columns(3)
    col6.metric("Budget", f"${budget_total:,.0f}")
    col7.metric("Actual Spend", f"${actual_total:,.0f}")
    col8.metric("Variance", f"${budget_total - actual_total:,.0f}")

    st.divider()
    left, right = st.columns(2)

    with left:
        st.subheader("Schedule Status")
        sched_df = {
            "Status": ["On Track", "At Risk", "Delayed"],
            "Count": [
                schedule_counts.get(ScheduleStatusEnum.on_track, 0),
                schedule_counts.get(ScheduleStatusEnum.at_risk, 0),
                schedule_counts.get(ScheduleStatusEnum.delayed, 0),
            ],
        }
        fig = px.bar(
            sched_df, x="Status", y="Count",
            color="Status",
            color_discrete_map={"On Track": STATUS_COLORS["good"], "At Risk": STATUS_COLORS["warning"], "Delayed": STATUS_COLORS["critical"]},
        )
        fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Safety Issues by Category")
        safety_rows = (
            db.query(SafetyIssue.category, func.count(SafetyIssue.id))
            .filter(SafetyIssue.project_id == pid)
            .group_by(SafetyIssue.category)
            .all()
        )
        if safety_rows:
            fig2 = px.bar(
                x=[c.value.replace("_", " ") for c, _ in safety_rows],
                y=[n for _, n in safety_rows],
                color=[c.value for c, _ in safety_rows],
                color_discrete_sequence=CATEGORICAL,
                labels={"x": "", "y": "Count"},
            )
            fig2.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.caption("No safety issues recorded.")

    with right:
        st.subheader("Risk Heat Map (Likelihood × Impact)")
        risk_rows = (
            db.query(Risk.likelihood, Risk.impact, func.count(Risk.id))
            .filter(Risk.project_id == pid, Risk.status == RiskStatusEnum.open)
            .group_by(Risk.likelihood, Risk.impact)
            .all()
        )
        if risk_rows:
            grid = [[0] * 5 for _ in range(5)]
            for likelihood, impact, count in risk_rows:
                grid[likelihood - 1][impact - 1] = count
            fig3 = px.imshow(
                grid, x=[1, 2, 3, 4, 5], y=[1, 2, 3, 4, 5], color_continuous_scale="Blues",
                labels=dict(x="Impact", y="Likelihood", color="Risks"), text_auto=True,
            )
            fig3.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.caption("No open risks recorded.")

        st.subheader("NCR Trend")
        month_expr = func.to_char(NonConformanceReport.identified_date, "YYYY-MM")
        ncr_rows = (
            db.query(month_expr, func.count(NonConformanceReport.id))
            .filter(NonConformanceReport.project_id == pid, NonConformanceReport.identified_date.isnot(None))
            .group_by(month_expr)
            .order_by(month_expr)
            .all()
        )
        if ncr_rows:
            fig4 = px.line(x=[r[0] for r in ncr_rows], y=[r[1] for r in ncr_rows], markers=True, labels={"x": "Month", "y": "NCRs"})
            fig4.update_traces(line_color=STATUS_COLORS["neutral"])
            fig4.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.caption("No NCR history yet.")
