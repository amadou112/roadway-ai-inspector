from datetime import date

import streamlit as st

from streamlit_common import apply_page_style, badge, get_db_session, init_app, sidebar_controls

apply_page_style()
init_app()

from app.models.inspection import DailyInspectionReport  # noqa: E402
from app.services import inspection_service, pdf_service  # noqa: E402

st.title("Daily Inspection Reports")

with get_db_session() as db:
    current_user, project = sidebar_controls(db)
    if project is None:
        st.stop()
    pid = project.id

    new_tab, history_tab = st.tabs(["📝 New Report", "📋 History"])

    with new_tab:
        st.caption("Enter field data — AI will generate the narrative report (stub text if no OpenAI key is set).")

        col1, col2, col3 = st.columns(3)
        report_date = col1.date_input("Report Date", value=date.today())
        weather_temp = col2.number_input("Temp (°F)", value=65)
        weather_conditions = col3.text_input("Conditions", value="Clear")

        contractor_activities = st.text_area(
            "Contractor Activities (one per line)", placeholder="Placed concrete deck pour, Station 12+00 to 14+50"
        )
        equipment_onsite = st.text_area("Equipment Onsite (one per line)", placeholder="Concrete pump truck")

        st.markdown("**Materials Delivered / Quantities Installed**")
        mcol1, mcol2, mcol3 = st.columns(3)
        material_item = mcol1.text_input("Item", key="mat_item")
        material_qty = mcol2.text_input("Quantity", key="mat_qty")
        material_unit = mcol3.text_input("Unit", key="mat_unit")

        st.markdown("**Deficiencies**")
        dcol1, dcol2, dcol3 = st.columns(3)
        deficiency_desc = dcol1.text_input("Description", key="def_desc")
        deficiency_severity = dcol2.selectbox("Severity", ["low", "medium", "high", "critical"], key="def_sev")
        deficiency_location = dcol3.text_input("Location", key="def_loc")

        if st.button("Generate Inspection Report", type="primary"):
            report = DailyInspectionReport(
                project_id=pid,
                report_date=report_date,
                inspector_id=current_user.id if current_user else None,
                inspector_name=current_user.full_name if current_user else None,
                weather_temp_f=weather_temp,
                weather_conditions=weather_conditions,
                contractor_activities=[a.strip() for a in contractor_activities.splitlines() if a.strip()],
                equipment_onsite=[e.strip() for e in equipment_onsite.splitlines() if e.strip()],
                materials_delivered=[{"item": material_item, "quantity": material_qty, "unit": material_unit}] if material_item else [],
                quantities_installed=[],
                deficiencies=[{"description": deficiency_desc, "severity": deficiency_severity, "location": deficiency_location}] if deficiency_desc else [],
                photos=[],
            )
            with st.spinner("Generating narrative with AI…"):
                report.narrative = inspection_service.generate_narrative(report)
            db.add(report)
            db.commit()
            st.success("Report generated — see it in the History tab.")

    with history_tab:
        reports = (
            db.query(DailyInspectionReport)
            .filter(DailyInspectionReport.project_id == pid)
            .order_by(DailyInspectionReport.report_date.desc())
            .all()
        )
        if not reports:
            st.caption("No inspection reports yet.")
        for r in reports:
            with st.expander(f"{r.report_date} — {r.inspector_name or 'Unknown inspector'}"):
                st.markdown(badge(r.status.value), unsafe_allow_html=True)
                st.write(r.narrative)
                if r.deficiencies:
                    st.markdown("**Deficiencies**")
                    for d in r.deficiencies:
                        st.markdown(f"- {badge(d.get('severity', 'medium'))} {d.get('description')}", unsafe_allow_html=True)

                import tempfile

                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    quantities_rows = [["Item", "Quantity", "Unit"]] + [
                        [q.get("item", "-"), str(q.get("quantity", "-")), q.get("unit", "-")] for q in r.quantities_installed
                    ] or [["Item", "Quantity", "Unit"], ["None recorded", "-", "-"]]
                    deficiency_rows = [["Description", "Severity", "Location"]] + [
                        [d.get("description", "-"), d.get("severity", "-"), d.get("location", "-")] for d in r.deficiencies
                    ] or [["Description", "Severity", "Location"], ["None recorded", "-", "-"]]
                    pdf_service.build_pdf(
                        file_path=tmp.name,
                        title="Daily Inspection Report",
                        subtitle=f"{project.name} — {r.report_date} — Inspector: {r.inspector_name}",
                        sections=[("Narrative Report", r.narrative or "")],
                        tables=[("Quantities Installed", quantities_rows), ("Deficiencies", deficiency_rows)],
                    )
                    with open(tmp.name, "rb") as f:
                        st.download_button(
                            "⬇ Download PDF", f.read(), file_name=f"inspection_report_{r.report_date}.pdf",
                            mime="application/pdf", key=f"dl_{r.id}",
                        )
