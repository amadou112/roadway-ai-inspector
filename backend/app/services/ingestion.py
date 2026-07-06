import os

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.enums import DocStatusEnum
from app.services import vectorstore

_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)


def extract_pages(file_path: str) -> list[str]:
    """Returns a list of page texts. Non-PDF files are treated as a single page."""
    if file_path.lower().endswith(".pdf"):
        reader = PdfReader(file_path)
        return [page.extract_text() or "" for page in reader.pages]
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return [f.read()]


def ingest_document(db: Session, document: Document) -> None:
    try:
        pages = extract_pages(document.file_path)
        ids: list[str] = []
        texts: list[str] = []
        metadatas: list[dict] = []

        for page_number, page_text in enumerate(pages, start=1):
            if not page_text.strip():
                continue
            for chunk_index, chunk in enumerate(_splitter.split_text(page_text)):
                chunk_id = f"{document.id}-{page_number}-{chunk_index}"
                ids.append(chunk_id)
                texts.append(chunk)
                metadatas.append(
                    {
                        "document_id": str(document.id),
                        "document_title": document.title,
                        "project_id": str(document.project_id),
                        "doc_type": document.doc_type.value,
                        "page_number": page_number,
                    }
                )

        vectorstore.add_chunks(ids, texts, metadatas)

        document.page_count = len(pages)
        document.chunk_count = len(ids)
        document.status = DocStatusEnum.indexed
        document.error_message = None
    except Exception as exc:  # noqa: BLE001
        document.status = DocStatusEnum.failed
        document.error_message = str(exc)[:1024]
    finally:
        db.add(document)
        db.commit()


def save_upload(project_id: str, document_id: str, filename: str, content: bytes, storage_dir: str) -> str:
    project_dir = os.path.join(storage_dir, project_id, document_id)
    os.makedirs(project_dir, exist_ok=True)
    file_path = os.path.join(project_dir, filename)
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path
