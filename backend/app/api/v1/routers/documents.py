import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.enums import DocTypeEnum
from app.models.user import User
from app.schemas.document import DocumentOut
from app.services import ingestion

router = APIRouter(prefix="/api/v1/projects/{project_id}/documents", tags=["documents"])
settings = get_settings()


@router.get("", response_model=list[DocumentOut])
def list_documents(project_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Document).filter(Document.project_id == project_id).order_by(Document.created_at.desc()).all()


@router.post("", response_model=DocumentOut)
async def upload_document(
    project_id: uuid.UUID,
    title: str = Form(...),
    doc_type: DocTypeEnum = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = Document(
        project_id=project_id,
        title=title,
        doc_type=doc_type,
        file_path="",
        uploaded_by=current_user.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    content = await file.read()
    file_path = ingestion.save_upload(
        str(project_id), str(document.id), file.filename or "upload", content, settings.storage_dir
    )
    document.file_path = file_path
    db.commit()

    ingestion.ingest_document(db, document)
    db.refresh(document)
    return document


@router.delete("/{document_id}")
def delete_document(
    project_id: uuid.UUID,
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    from app.services import vectorstore

    document = db.get(Document, document_id)
    if not document or document.project_id != project_id:
        raise HTTPException(status_code=404, detail="Not found")
    vectorstore.delete_document_chunks(str(document.id))
    db.delete(document)
    db.commit()
    return {"ok": True}
