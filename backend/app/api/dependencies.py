from fastapi import Request

from backend.app.services.memory import SessionMemory
from backend.app.services.rag_service import RAGService


def get_rag_service(request: Request) -> RAGService:
    return request.app.state.rag_service


def get_memory(request: Request) -> SessionMemory:
    return request.app.state.memory
