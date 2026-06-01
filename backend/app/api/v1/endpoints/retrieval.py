from fastapi import APIRouter, Depends

from backend.app.api.dependencies import get_rag_service
from backend.app.schemas.chat import RetrievalRequest, RetrievalResponse
from backend.app.services.rag_service import RAGService

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.post("", response_model=RetrievalResponse)
async def retrieval(payload: RetrievalRequest, rag_service: RAGService = Depends(get_rag_service)):
    rewrite_plan, chunks = await rag_service.retrieve(payload.query, top_k=payload.top_k)
    return RetrievalResponse(query=payload.query, rewrite=rewrite_plan, chunks=chunks)
