from fastapi import APIRouter, Depends

from backend.app.api.dependencies import get_rag_service
from backend.app.schemas.chat import RewriteRequest, RewriteResponse
from backend.app.services.rag_service import RAGService

router = APIRouter(prefix="/rewrite", tags=["rewrite"])


@router.post("", response_model=RewriteResponse)
async def rewrite(payload: RewriteRequest, rag_service: RAGService = Depends(get_rag_service)):
    rewrite_plan = await rag_service.rewrite(payload.query)
    return RewriteResponse(query=payload.query, rewrite=rewrite_plan)
