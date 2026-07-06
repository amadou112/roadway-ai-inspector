"""Thin wrapper around the OpenAI API so the rest of the app never imports
`openai` directly. Falls back to a deterministic stub when no API key is
configured, so the app remains runnable/demoable without a key.
"""

from openai import OpenAI

from app.core.config import get_settings

settings = get_settings()

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def is_llm_enabled() -> bool:
    return settings.llm_enabled


def chat_completion(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    if not settings.llm_enabled:
        return (
            "[LLM disabled — no OPENAI_API_KEY configured]\n\n"
            "This is a stub response so the workflow can be demoed end-to-end. "
            "Set OPENAI_API_KEY in your .env to get real AI-generated output.\n\n"
            f"Prompt received:\n{user_prompt[:800]}"
        )
    client = _get_client()
    response = client.chat.completions.create(
        model=settings.openai_chat_model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content or ""


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not settings.llm_enabled:
        # Deterministic pseudo-embedding so Chroma still works without a key.
        return [_fake_embedding(t) for t in texts]
    client = _get_client()
    response = client.embeddings.create(model=settings.openai_embedding_model, input=texts)
    return [item.embedding for item in response.data]


def _fake_embedding(text: str, dims: int = 256) -> list[float]:
    import hashlib

    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return [((digest[i % len(digest)] / 255.0) * 2 - 1) for i in range(dims)]
