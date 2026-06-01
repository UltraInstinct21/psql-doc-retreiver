from fastapi import APIRouter

from backend.app.api.v1.endpoints.chat import router as chat_router
from backend.app.api.v1.endpoints.health import router as health_router
from backend.app.api.v1.endpoints.retrieval import router as retrieval_router
from backend.app.api.v1.endpoints.rewrite import router as rewrite_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(chat_router)
api_router.include_router(rewrite_router)
api_router.include_router(retrieval_router)
