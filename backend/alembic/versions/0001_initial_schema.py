"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def _enum(name: str, *values: str) -> postgresql.ENUM:
    return postgresql.ENUM(*values, name=name, create_type=True)


def upgrade() -> None:
    role_enum = _enum(
        "role_enum",
        "program_manager", "project_manager", "resident_engineer", "inspector",
        "designer", "contractor", "dot_executive",
    )
    doc_type_enum = _enum(
        "doc_type_enum",
        "spec", "fhwa_manual", "inspection_report", "rfi", "submittal",
        "plan_sheet", "daily_report", "other",
    )
    doc_status_enum = _enum("doc_status_enum", "processing", "indexed", "failed")
    priority_enum = _enum("priority_enum", "low", "medium", "high", "critical")
    severity_enum = _enum("severity_enum", "low", "medium", "high", "critical")
    rfi_status_enum = _enum("rfi_status_enum", "open", "answered", "closed")
    submittal_status_enum = _enum(
        "submittal_status_enum", "pending", "under_review", "approved", "rejected", "resubmit_required"
    )
    risk_status_enum = _enum("risk_status_enum", "open", "mitigated", "closed")
    ncr_status_enum = _enum("ncr_status_enum", "open", "corrective_action", "closed")
    safety_category_enum = _enum(
        "safety_category_enum", "fall_protection", "equipment", "traffic_control", "ppe",
        "electrical", "excavation", "other",
    )
    safety_status_enum = _enum("safety_status_enum", "open", "corrective_action", "closed")
    schedule_status_enum = _enum("schedule_status_enum", "on_track", "at_risk", "delayed", "complete")
    inspection_report_status_enum = _enum("inspection_report_status_enum", "draft", "submitted")
    design_review_category_enum = _enum(
        "design_review_category_enum", "missing_item", "conflict", "risk", "constructability", "safety", "compliance"
    )
    design_review_status_enum = _enum("design_review_status_enum", "processing", "completed", "failed")
    report_type_enum = _enum("report_type_enum", "weekly_status", "risk_summary")
    bridge_condition_enum = _enum("bridge_condition_enum", "good", "fair", "poor", "unknown")

    bind = op.get_bind()
    all_enums = [
        role_enum, doc_type_enum, doc_status_enum, priority_enum, severity_enum, rfi_status_enum,
        submittal_status_enum, risk_status_enum, ncr_status_enum, safety_category_enum, safety_status_enum,
        schedule_status_enum, inspection_report_status_enum, design_review_category_enum,
        design_review_status_enum, report_type_enum, bridge_condition_enum,
    ]
    for e in all_enums:
        e.create(bind, checkfirst=True)
        # Types are created explicitly above (once each, even though several are reused
        # across multiple tables below) — tell SQLAlchemy not to re-emit CREATE TYPE
        # when each create_table() call below dispatches its "before_create" event.
        e.create_type = False

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", role_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("dot_number", sa.String(64)),
        sa.Column("route", sa.String(64)),
        sa.Column("county", sa.String(128)),
        sa.Column("state", sa.String(2)),
        sa.Column("status", sa.String(32)),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("budget", sa.Numeric(14, 2)),
        sa.Column("spent", sa.Numeric(14, 2)),
        sa.Column("description", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("doc_type", doc_type_enum, nullable=False),
        sa.Column("file_path", sa.String(1024), nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("status", doc_status_enum),
        sa.Column("page_count", sa.Integer()),
        sa.Column("chunk_count", sa.Integer()),
        sa.Column("error_message", sa.String(1024)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "rfis",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False, index=True),
        sa.Column("number", sa.String(32), nullable=False),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("status", rfi_status_enum),
        sa.Column("priority", priority_enum),
        sa.Column("submitted_by", sa.String(255)),
        sa.Column("assigned_to", sa.String(255)),
        sa.Column("submitted_date", sa.Date()),
        sa.Column("due_date", sa.Date()),
        sa.Column("response", sa.Text()),
        sa.Column("cost_impact", sa.Numeric(14, 2)),
        sa.Column("schedule_impact_days", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "submittals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False, index=True),
        sa.Column("number", sa.String(32), nullable=False),
        sa.Column("spec_section", sa.String(64)),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("status", submittal_status_enum),
        sa.Column("submitted_date", sa.Date()),
        sa.Column("reviewed_date", sa.Date()),
        sa.Column("reviewer", sa.String(255)),
        sa.Column("revision", sa.Integer()),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "risks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("category", sa.String(64)),
        sa.Column("description", sa.Text()),
        sa.Column("likelihood", sa.Integer()),
        sa.Column("impact", sa.Integer()),
        sa.Column("status", risk_status_enum),
        sa.Column("owner", sa.String(255)),
        sa.Column("mitigation_plan", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "non_conformance_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False, index=True),
        sa.Column("ncr_number", sa.String(32), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("location", sa.String(255)),
        sa.Column("spec_reference", sa.String(128)),
        sa.Column("severity", severity_enum),
        sa.Column("status", ncr_status_enum),
        sa.Column("identified_by", sa.String(255)),
        sa.Column("identified_date", sa.Date()),
        sa.Column("corrective_action", sa.Text()),
        sa.Column("closed_date", sa.Date()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "safety_issues",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False, index=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("location", sa.String(255)),
        sa.Column("severity", severity_enum),
        sa.Column("category", safety_category_enum),
        sa.Column("status", safety_status_enum),
        sa.Column("reported_by", sa.String(255)),
        sa.Column("reported_date", sa.Date()),
        sa.Column("corrective_action", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "schedule_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False, index=True),
        sa.Column("task_name", sa.String(255), nullable=False),
        sa.Column("planned_start", sa.Date()),
        sa.Column("planned_finish", sa.Date()),
        sa.Column("actual_start", sa.Date()),
        sa.Column("actual_finish", sa.Date()),
        sa.Column("percent_complete", sa.Integer()),
        sa.Column("status", schedule_status_enum),
        sa.Column("predecessor", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "cost_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False, index=True),
        sa.Column("category", sa.String(128), nullable=False),
        sa.Column("budget_amount", sa.Numeric(14, 2)),
        sa.Column("committed_amount", sa.Numeric(14, 2)),
        sa.Column("actual_amount", sa.Numeric(14, 2)),
        sa.Column("change_order_number", sa.String(64)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "daily_inspection_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False, index=True),
        sa.Column("report_date", sa.Date(), nullable=False),
        sa.Column("inspector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("inspector_name", sa.String(255)),
        sa.Column("weather_temp_f", sa.Integer()),
        sa.Column("weather_conditions", sa.String(255)),
        sa.Column("contractor_activities", postgresql.JSONB()),
        sa.Column("equipment_onsite", postgresql.JSONB()),
        sa.Column("materials_delivered", postgresql.JSONB()),
        sa.Column("quantities_installed", postgresql.JSONB()),
        sa.Column("deficiencies", postgresql.JSONB()),
        sa.Column("photos", postgresql.JSONB()),
        sa.Column("narrative", sa.Text()),
        sa.Column("status", inspection_report_status_enum),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "inspection_findings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False, index=True),
        sa.Column(
            "inspection_report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("daily_inspection_reports.id"), index=True
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("location", sa.String(255)),
        sa.Column("category", sa.String(128)),
        sa.Column("severity", severity_enum),
        sa.Column("status", sa.String(32)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "design_review_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False, index=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("reviewed_by", sa.String(255)),
        sa.Column("review_date", sa.Date()),
        sa.Column("status", design_review_status_enum),
        sa.Column("summary", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "design_review_findings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "submission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("design_review_submissions.id"),
            nullable=False, index=True,
        ),
        sa.Column("category", design_review_category_enum, nullable=False),
        sa.Column("severity", severity_enum),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("sheet_reference", sa.String(128)),
        sa.Column("recommendation", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "bridges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nbi_structure_number", sa.String(32), nullable=False, unique=True, index=True),
        sa.Column("state", sa.String(2)),
        sa.Column("county", sa.String(128)),
        sa.Column("facility_carried", sa.String(255)),
        sa.Column("feature_intersected", sa.String(255)),
        sa.Column("year_built", sa.Integer()),
        sa.Column("adt", sa.Integer()),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
        sa.Column("deck_condition", sa.Integer()),
        sa.Column("superstructure_condition", sa.Integer()),
        sa.Column("substructure_condition", sa.Integer()),
        sa.Column("structural_evaluation", sa.Integer()),
        sa.Column("deck_area_sqm", sa.Float()),
        sa.Column("owner", sa.String(255)),
        sa.Column("material_type", sa.String(128)),
        sa.Column("design_type", sa.String(128)),
        sa.Column("condition", bridge_condition_enum),
    )

    op.create_table(
        "crash_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("state", sa.String(2)),
        sa.Column("county", sa.String(128)),
        sa.Column("case_year", sa.Integer()),
        sa.Column("crash_date", sa.Date()),
        sa.Column("fatalities", sa.Integer()),
        sa.Column("route", sa.String(255)),
        sa.Column("weather", sa.String(128)),
        sa.Column("light_condition", sa.String(128)),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
    )

    op.create_table(
        "pavement_segments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("state", sa.String(2)),
        sa.Column("route", sa.String(255)),
        sa.Column("county", sa.String(128)),
        sa.Column("iri", sa.Float()),
        sa.Column("psr", sa.Float()),
        sa.Column("surface_type", sa.String(128)),
        sa.Column("through_lanes", sa.Integer()),
        sa.Column("aadt", sa.Integer()),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
    )

    op.create_table(
        "generated_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False, index=True),
        sa.Column("report_type", report_type_enum, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("period_start", sa.Date()),
        sa.Column("period_end", sa.Date()),
        sa.Column("file_path", sa.String(1024), nullable=False),
        sa.Column("generated_by", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    for table in [
        "generated_reports", "pavement_segments", "crash_records", "bridges",
        "design_review_findings", "design_review_submissions", "inspection_findings",
        "daily_inspection_reports", "cost_items", "schedule_items", "safety_issues",
        "non_conformance_reports", "risks", "submittals", "rfis", "documents", "projects", "users",
    ]:
        op.drop_table(table)

    for enum_name in [
        "role_enum", "doc_type_enum", "doc_status_enum", "priority_enum", "severity_enum", "rfi_status_enum",
        "submittal_status_enum", "risk_status_enum", "ncr_status_enum", "safety_category_enum",
        "safety_status_enum", "schedule_status_enum", "inspection_report_status_enum",
        "design_review_category_enum", "design_review_status_enum", "report_type_enum", "bridge_condition_enum",
    ]:
        postgresql.ENUM(name=enum_name).drop(op.get_bind(), checkfirst=True)
