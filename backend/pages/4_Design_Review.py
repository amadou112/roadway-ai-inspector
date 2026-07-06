import tempfile
from datetime import date

import streamlit as st

from streamlit_common import apply_page_style, badge, get_db_session, init_app, sidebar_controls

apply_page_style()
init_app()

from app.models.design_review import DesignReviewFinding, DesignReviewSubmission  # noqa: E402
from app.models.document import Document  # noqa: E402
from app.models.enums import DesignReviewStatusEnum  # noqa: E402
from app.services import design_review_service, ingestion, pdf_service  # noqa: E402

st.title("Design Review Assistant")
st.caption(
    "AI-powered review of design documents for missing items, conflicts, constructability, safety, "
    "and compliance gaps."
)

with get_db_session() as db:
    current_user, project = sidebar_controls(db)
    if project is None:
        st.stop()
    pid = project.id

    documents = db.query(Document).filter(Document.project_id == pid).order_by(Document.created_at.desc()).all()

    if not documents:
        st.info("Upload a plan sheet or design document in the Documents tab first.")
    else:
        doc_titles = [d.title for d in documents]
        picked_title = st.selectbox("Design Document", doc_titles)
        picked_doc = documents[doc_titles.index(picked_title)]

        if st.button("Run AI Review", type="primary"):
            submission = DesignReviewSubmission(
                project_id=pid, document_id=picked_doc.id,
                reviewed_by=current_user.full_name if current_user else None,
                review_date=date.today(), status=DesignReviewStatusEnum.processing,
            )
            db.add(submission)
            db.commit()
            db.refresh(submission)

            with st.spinner("Running AI design review…"):
                try:
                    pages = ingestion.extract_pages(picked_doc.file_path)
                    design_text = "\n".join(pages)
                    findings = design_review_service.review_design_document(str(pid), design_text)
                    for f in findings:
                        db.add(
                            DesignReviewFinding(
                                submission_id=submission.id,
                                category=f.get("category", "compliance"),
                                severity=f.get("severity", "medium"),
                                description=f.get("description", ""),
                                sheet_reference=f.get("sheet_reference"),
                                recommendation=f.get("recommendation"),
                            )
                        )
                    submission.status = DesignReviewStatusEnum.completed
                    submission.summary = f"{len(findings)} findings identified across constructability, safety, and compliance review."
                except Exception as exc:  # noqa: BLE001
                    submission.status = DesignReviewStatusEnum.failed
                    submission.summary = f"Review failed: {exc}"
                db.commit()
            st.rerun()

    st.divider()
    st.subheader("Past Reviews")
    submissions = (
        db.query(DesignReviewSubmission)
        .filter(DesignReviewSubmission.project_id == pid)
        .order_by(DesignReviewSubmission.created_at.desc())
        .all()
    )
    if not submissions:
        st.caption("No design reviews yet.")
    for s in submissions:
        doc = db.get(Document, s.document_id)
        with st.expander(f"{doc.title if doc else s.document_id} — {s.reviewed_by}"):
            st.markdown(badge(s.status.value), unsafe_allow_html=True)
            st.write(s.summary)
            findings = db.query(DesignReviewFinding).filter(DesignReviewFinding.submission_id == s.id).all()
            for f in findings:
                st.markdown(
                    f"{badge(f.category.value, tone='neutral')} {badge(f.severity.value)} — {f.description}",
                    unsafe_allow_html=True,
                )
                if f.recommendation:
                    st.caption(f"Recommendation: {f.recommendation}")

            if s.status == DesignReviewStatusEnum.completed:
                findings_rows = [["Category", "Severity", "Description", "Sheet", "Recommendation"]] + [
                    [f.category.value, f.severity.value, f.description, f.sheet_reference or "-", f.recommendation or "-"]
                    for f in findings
                ]
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    pdf_service.build_pdf(
                        file_path=tmp.name,
                        title="Design Review Report",
                        subtitle=f"{project.name} — Document: {doc.title if doc else ''} — Reviewed by {s.reviewed_by}",
                        sections=[("Summary", s.summary or "")],
                        tables=[("Findings", findings_rows)],
                    )
                    with open(tmp.name, "rb") as f:
                        st.download_button(
                            "⬇ Download PDF", f.read(), file_name=f"design_review_{s.id}.pdf",
                            mime="application/pdf", key=f"dl_{s.id}",
                        )
