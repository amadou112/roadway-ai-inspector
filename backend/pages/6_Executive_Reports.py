import streamlit as st

from streamlit_common import apply_page_style, badge, get_db_session, init_app, sidebar_controls

apply_page_style()
init_app()

from app.models.report import GeneratedReport  # noqa: E402
from app.services import report_service  # noqa: E402

st.title("Executive Reporting")
st.caption("DOT-ready PDF reports with AI-generated executive narratives.")

with get_db_session() as db:
    current_user, project = sidebar_controls(db)
    if project is None:
        st.stop()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Weekly Status Report**")
        st.caption("RFIs, submittals, risks, NCRs, safety, schedule, and cost KPIs with an executive summary.")
        if st.button("Generate Weekly Status Report"):
            with st.spinner("Generating…"):
                file_path = report_service.generate_weekly_status_report(
                    db, project, None, None, current_user.full_name if current_user else None
                )
                record = GeneratedReport(
                    project_id=project.id, report_type="weekly_status", title="Weekly Project Status Report",
                    file_path=file_path, generated_by=current_user.full_name if current_user else None,
                )
                db.add(record)
                db.commit()
            st.success("Generated — see below.")
            st.rerun()

    with col2:
        st.markdown("**Risk Summary Report**")
        st.caption("Open risks ranked by score with an AI risk posture narrative.")
        if st.button("Generate Risk Summary Report"):
            with st.spinner("Generating…"):
                file_path = report_service.generate_risk_summary_report(
                    db, project, current_user.full_name if current_user else None
                )
                record = GeneratedReport(
                    project_id=project.id, report_type="risk_summary", title="Project Risk Summary Report",
                    file_path=file_path, generated_by=current_user.full_name if current_user else None,
                )
                db.add(record)
                db.commit()
            st.success("Generated — see below.")
            st.rerun()

    st.divider()
    st.subheader("Generated Reports")
    reports = (
        db.query(GeneratedReport)
        .filter(GeneratedReport.project_id == project.id)
        .order_by(GeneratedReport.created_at.desc())
        .all()
    )
    if not reports:
        st.caption("No reports generated yet.")
    for r in reports:
        cols = st.columns([3, 1, 1, 2])
        cols[0].markdown(f"**{r.title}**")
        cols[1].markdown(badge(r.report_type.value, tone="neutral"), unsafe_allow_html=True)
        cols[2].caption(r.generated_by or "—")
        try:
            with open(r.file_path, "rb") as f:
                cols[3].download_button(
                    "⬇ Download PDF", f.read(), file_name=f"{r.title}.pdf", mime="application/pdf", key=f"dl_{r.id}"
                )
        except FileNotFoundError:
            cols[3].caption("File no longer available (disk was reset).")
