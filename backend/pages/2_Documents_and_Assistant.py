import streamlit as st

from streamlit_common import apply_page_style, badge, get_db_session, init_app, sidebar_controls

apply_page_style()
init_app()

from app.core.config import get_settings  # noqa: E402
from app.models.document import Document  # noqa: E402
from app.models.enums import DocTypeEnum  # noqa: E402
from app.services import ingestion, rag_service  # noqa: E402

settings = get_settings()

st.title("Documents & AI Assistant")

DOC_TYPES = [t.value for t in DocTypeEnum]

with get_db_session() as db:
    current_user, project = sidebar_controls(db)
    if project is None:
        st.stop()
    pid = project.id

    doc_tab, chat_tab = st.tabs(["📄 Document Library", "🤖 AI Assistant"])

    with doc_tab:
        st.caption(
            "Uploaded documents are automatically chunked and embedded for the AI Assistant. "
            "Ask questions in the Assistant tab and get cited answers."
        )
        with st.form("upload_form", clear_on_submit=True):
            title = st.text_input("Title")
            doc_type = st.selectbox("Document Type", DOC_TYPES)
            file = st.file_uploader("File (PDF or text)", type=["pdf", "txt"])
            if st.form_submit_button("Upload & Index") and file and title:
                document = Document(
                    project_id=pid, title=title, doc_type=DocTypeEnum(doc_type), file_path="",
                    uploaded_by=current_user.id if current_user else None,
                )
                db.add(document)
                db.commit()
                db.refresh(document)
                content = file.read()
                file_path = ingestion.save_upload(str(pid), str(document.id), file.name, content, settings.storage_dir)
                document.file_path = file_path
                db.commit()
                with st.spinner("Indexing document…"):
                    ingestion.ingest_document(db, document)
                st.success(f"Uploaded and indexed '{title}'.")
                st.rerun()

        docs = db.query(Document).filter(Document.project_id == pid).order_by(Document.created_at.desc()).all()
        if docs:
            for d in docs:
                cols = st.columns([3, 1, 1, 1])
                cols[0].markdown(f"**{d.title}**")
                cols[1].markdown(badge(d.doc_type.value, tone="neutral"), unsafe_allow_html=True)
                cols[2].markdown(badge(d.status.value), unsafe_allow_html=True)
                cols[3].caption(f"{d.chunk_count} chunks")
        else:
            st.caption("No documents uploaded yet.")

    with chat_tab:
        st.caption(
            "Ask questions about uploaded specifications, FHWA manuals, inspection reports, RFIs, submittals, "
            "and plan sheets. Answers are cited to source documents."
        )
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if msg.get("citations"):
                    st.caption(
                        " · ".join(
                            f"[{i+1}] {c['document_title']}" + (f" p.{c['page_number']}" if c["page_number"] else "")
                            for i, c in enumerate(msg["citations"])
                        )
                    )

        question = st.chat_input("Ask a question about project documents…")
        if question:
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.spinner("Thinking…"):
                response = rag_service.answer_question(str(pid), question)
            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": response.answer,
                    "citations": [
                        {"document_title": c.document_title, "page_number": c.page_number} for c in response.citations
                    ],
                }
            )
            st.rerun()
