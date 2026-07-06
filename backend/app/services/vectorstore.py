import chromadb

from app.core.config import get_settings
from app.services.llm_provider import embed_texts

settings = get_settings()

_client: chromadb.ClientAPI | None = None
_COLLECTION_NAME = "documents"


def get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_dir)
    return _client


def get_collection():
    return get_client().get_or_create_collection(name=_COLLECTION_NAME)


def add_chunks(
    ids: list[str],
    texts: list[str],
    metadatas: list[dict],
) -> None:
    if not ids:
        return
    embeddings = embed_texts(texts)
    get_collection().upsert(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)


def delete_document_chunks(document_id: str) -> None:
    get_collection().delete(where={"document_id": document_id})


def query(
    query_text: str,
    project_id: str,
    doc_type: str | None = None,
    top_k: int = 6,
) -> dict:
    where: dict = {"project_id": project_id}
    if doc_type:
        where = {"$and": [{"project_id": project_id}, {"doc_type": doc_type}]}

    embedding = embed_texts([query_text])[0]
    return get_collection().query(
        query_embeddings=[embedding],
        n_results=top_k,
        where=where,
    )
