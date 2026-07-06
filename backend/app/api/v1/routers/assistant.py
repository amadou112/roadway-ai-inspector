from fastapi import APIRouter, Depends, Request

from app.core.deps import get_current_user
from app.core.rate_limit import LLM_RATE_LIMIT, limiter
from app.models.user import User
from app.schemas.document import ChatRequest, ChatResponse
from app.services import rag_service

router = APIRouter(prefix="/api/v1/assistant", tags=["assistant"])


@router.post("/chat", response_model=ChatResponse)
@limiter.limit(LLM_RATE_LIMIT)
def chat(request: Request, payload: ChatRequest, _: User = Depends(get_current_user)):
    doc_type = payload.doc_type.value if payload.doc_type else None
    return rag_service.answer_question(str(payload.project_id), payload.question, doc_type)
