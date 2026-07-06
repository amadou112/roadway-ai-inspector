from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.document import ChatRequest, ChatResponse
from app.services import rag_service

router = APIRouter(prefix="/api/v1/assistant", tags=["assistant"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, _: User = Depends(get_current_user)):
    doc_type = payload.doc_type.value if payload.doc_type else None
    return rag_service.answer_question(str(payload.project_id), payload.question, doc_type)
