import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import DocStatusEnum, DocTypeEnum


class DocumentOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    doc_type: DocTypeEnum
    status: DocStatusEnum
    page_count: int
    chunk_count: int
    error_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatCitation(BaseModel):
    document_id: uuid.UUID
    document_title: str
    page_number: int | None = None
    snippet: str


class ChatRequest(BaseModel):
    project_id: uuid.UUID
    question: str
    doc_type: DocTypeEnum | None = None


class ChatResponse(BaseModel):
    answer: str
    citations: list[ChatCitation]
