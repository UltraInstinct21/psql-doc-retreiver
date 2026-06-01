from fastapi import APIRouter, Depends

from backend.app.api.dependencies import get_rag_service
from backend.app.services.rag_service import RAGService

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(rag_service: RAGService = Depends(get_rag_service)):
    return await rag_service.health()
