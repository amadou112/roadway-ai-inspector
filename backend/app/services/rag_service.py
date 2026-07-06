from app.schemas.document import ChatCitation, ChatResponse
from app.services import vectorstore
from app.services.llm_provider import chat_completion

SYSTEM_PROMPT = """You are the Roadway AI Inspector & Design Assistant, a construction and \
engineering document assistant for a state DOT. Answer the user's question using ONLY the \
provided context excerpts from uploaded DOT specifications, FHWA manuals, inspection reports, \
RFIs, submittals, plan sheets, and daily reports. Cite sources inline using the format \
[Source N] matching the numbered excerpts below. If the context does not contain the answer, \
say so plainly rather than guessing."""


def answer_question(project_id: str, question: str, doc_type: str | None = None) -> ChatResponse:
    results = vectorstore.query(question, project_id=project_id, doc_type=doc_type, top_k=6)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return ChatResponse(
            answer=(
                "No indexed documents were found for this project yet. Upload specifications, "
                "manuals, or reports in the Documents tab, then ask again."
            ),
            citations=[],
        )

    context_blocks = []
    citations: list[ChatCitation] = []
    for i, (text, meta) in enumerate(zip(documents, metadatas), start=1):
        context_blocks.append(f"[Source {i}] ({meta.get('document_title')}, p.{meta.get('page_number')}):\n{text}")
        citations.append(
            ChatCitation(
                document_id=meta.get("document_id"),
                document_title=meta.get("document_title", "Unknown"),
                page_number=meta.get("page_number"),
                snippet=text[:300],
            )
        )

    user_prompt = (
        f"Context excerpts:\n\n{chr(10).join(context_blocks)}\n\n"
        f"Question: {question}\n\n"
        "Answer concisely and cite sources as [Source N]."
    )

    answer = chat_completion(SYSTEM_PROMPT, user_prompt)
    return ChatResponse(answer=answer, citations=citations)
