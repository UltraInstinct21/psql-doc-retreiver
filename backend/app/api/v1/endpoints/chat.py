from fastapi import APIRouter, Depends

from backend.app.api.dependencies import get_rag_service
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.rag_service import RAGService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, rag_service: RAGService = Depends(get_rag_service)):
    return await rag_service.chat(
        query=payload.query,
        retrieval_enabled=payload.retrieval_enabled,
        top_k=payload.top_k,
    )
