import streamlit as st

from streamlit_common import apply_page_style, get_db_session, init_app, render_entity_manager, sidebar_controls

apply_page_style()
init_app()

from app.models.pm import RFI, CostItem, NonConformanceReport, Risk, SafetyIssue, ScheduleItem, Submittal  # noqa: E402

st.title("Project Management")

with get_db_session() as db:
    current_user, project = sidebar_controls(db)
    if project is None:
        st.stop()
    pid = project.id

    tabs = st.tabs(["RFIs", "Submittals", "Risks", "NCRs", "Safety", "Schedule", "Cost"])

    with tabs[0]:
        render_entity_manager(
            db, pid, RFI, "RFIs",
            display_columns=["number", "subject", "status", "priority", "assigned_to", "due_date", "cost_impact"],
            form_fields=[
                ("number", "RFI Number", "text"),
                ("subject", "Subject", "text"),
                ("question", "Question", "textarea"),
                ("priority", "Priority", ["low", "medium", "high", "critical"]),
                ("assigned_to", "Assigned To", "text"),
            ],
            status_field="status", status_options=["open", "answered", "closed"], row_label_field="number",
        )

    with tabs[1]:
        render_entity_manager(
            db, pid, Submittal, "Submittals",
            display_columns=["number", "title", "spec_section", "status", "reviewer", "revision"],
            form_fields=[
                ("number", "Submittal Number", "text"),
                ("spec_section", "Spec Section", "text"),
                ("title", "Title", "text"),
                ("reviewer", "Reviewer", "text"),
            ],
            status_field="status",
            status_options=["pending", "under_review", "approved", "rejected", "resubmit_required"],
            row_label_field="number",
        )

    with tabs[2]:
        render_entity_manager(
            db, pid, Risk, "Risks",
            display_columns=["title", "category", "likelihood", "impact", "status", "owner"],
            form_fields=[
                ("title", "Risk Title", "text"),
                ("category", "Category", "text"),
                ("description", "Description", "textarea"),
                ("likelihood", "Likelihood (1-5)", "number"),
                ("impact", "Impact (1-5)", "number"),
                ("owner", "Owner", "text"),
                ("mitigation_plan", "Mitigation Plan", "textarea"),
            ],
            status_field="status", status_options=["open", "mitigated", "closed"], row_label_field="title",
        )

    with tabs[3]:
        render_entity_manager(
            db, pid, NonConformanceReport, "NCRs",
            display_columns=["ncr_number", "description", "severity", "status", "location", "identified_date"],
            form_fields=[
                ("ncr_number", "NCR Number", "text"),
                ("description", "Description", "textarea"),
                ("location", "Location", "text"),
                ("spec_reference", "Spec Reference", "text"),
                ("severity", "Severity", ["low", "medium", "high", "critical"]),
                ("identified_by", "Identified By", "text"),
            ],
            status_field="status", status_options=["open", "corrective_action", "closed"], row_label_field="ncr_number",
        )

    with tabs[4]:
        render_entity_manager(
            db, pid, SafetyIssue, "Safety Issues",
            display_columns=["description", "category", "severity", "status", "location", "reported_date"],
            form_fields=[
                ("description", "Description", "textarea"),
                ("location", "Location", "text"),
                ("severity", "Severity", ["low", "medium", "high", "critical"]),
                (
                    "category", "Category",
                    ["fall_protection", "equipment", "traffic_control", "ppe", "electrical", "excavation", "other"],
                ),
                ("reported_by", "Reported By", "text"),
            ],
            status_field="status", status_options=["open", "corrective_action", "closed"], row_label_field="description",
        )

    with tabs[5]:
        render_entity_manager(
            db, pid, ScheduleItem, "Schedule",
            display_columns=["task_name", "planned_start", "planned_finish", "percent_complete", "status"],
            form_fields=[
                ("task_name", "Task Name", "text"),
                ("planned_start", "Planned Start", "date"),
                ("planned_finish", "Planned Finish", "date"),
                ("percent_complete", "Percent Complete", "number"),
            ],
            status_field="status", status_options=["on_track", "at_risk", "delayed", "complete"], row_label_field="task_name",
        )

    with tabs[6]:
        render_entity_manager(
            db, pid, CostItem, "Cost Items",
            display_columns=["category", "budget_amount", "committed_amount", "actual_amount"],
            form_fields=[
                ("category", "Category", "text"),
                ("budget_amount", "Budget Amount (USD)", "number"),
                ("committed_amount", "Committed Amount (USD)", "number"),
                ("actual_amount", "Actual Amount (USD)", "number"),
            ],
        )
