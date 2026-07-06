import json

from app.services import vectorstore
from app.services.llm_provider import chat_completion

SYSTEM_PROMPT = """You are a senior state DOT design reviewer performing constructability and \
compliance review of a roadway/bridge design submission. Review the provided design document \
text and the related specification excerpts, then identify findings across these categories: \
missing_item, conflict, risk, constructability, safety, compliance.

Respond with ONLY a JSON array (no markdown fences) of objects with fields:
category (one of the categories above), severity (low|medium|high|critical), description \
(specific, actionable), sheet_reference (string or null), recommendation (string).
Return between 3 and 12 findings. Be specific to the content provided; do not repeat generic \
boilerplate."""


def _parse_findings(raw: str) -> list[dict]:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.split("\n", 1)[-1] if cleaned.lower().startswith("json") else cleaned
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            data = data.get("findings", [])
        return [f for f in data if isinstance(f, dict) and "description" in f]
    except json.JSONDecodeError:
        return [
            {
                "category": "compliance",
                "severity": "medium",
                "description": raw[:500],
                "sheet_reference": None,
                "recommendation": "Review LLM output manually — response was not valid JSON.",
            }
        ]


def review_design_document(project_id: str, design_text: str) -> list[dict]:
    spec_context = ""
    try:
        results = vectorstore.query(design_text[:2000], project_id=project_id, doc_type="spec", top_k=4)
        docs = results.get("documents", [[]])[0]
        if docs:
            spec_context = "\n\n".join(docs)
    except Exception:  # noqa: BLE001
        spec_context = ""

    user_prompt = (
        f"Design document text (truncated to 8000 chars):\n{design_text[:8000]}\n\n"
        f"Relevant specification excerpts for compliance grounding:\n{spec_context or '(none indexed yet)'}"
    )
    raw = chat_completion(SYSTEM_PROMPT, user_prompt, temperature=0.2)
    return _parse_findings(raw)
