from fastapi import APIRouter, Depends

from backend.app.api.dependencies import get_rag_service
from backend.app.core.config import settings
from backend.app.schemas.chat import RetrievalRequest, RetrievalResponse
from backend.app.services.rag_service import RAGService

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.post("", response_model=RetrievalResponse)
async def retrieval(payload: RetrievalRequest, rag_service: RAGService = Depends(get_rag_service)):
    rewrite = await rag_service.rewrite(payload.query)
    chunks = await rag_service.retriever.retrieve(
        search_queries=rewrite.search_queries,
        rerank_query=rewrite.rerank_query,
        intent=rewrite.intent,
        top_k=payload.top_k or settings.top_k,
        candidate_k=max(settings.retrieval_k, payload.top_k or settings.top_k),
    )
    return RetrievalResponse(query=payload.query, rewrite=rewrite, chunks=chunks)
