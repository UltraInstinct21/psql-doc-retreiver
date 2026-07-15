import uuid

from fastapi import APIRouter, Depends

from backend.app.api.dependencies import get_memory, get_rag_service
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.memory import SessionMemory
from backend.app.services.rag_service import RAGService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
    memory: SessionMemory = Depends(get_memory),
):
    # Auto-assign a session if the client did not provide one
    session_id = payload.session_id.strip() or str(uuid.uuid4())

    history = await memory.get_recent_context(session_id)

    response = await rag_service.chat(
        query=payload.query,
        session_id=session_id,
        history=history,
        retrieval_enabled=payload.retrieval_enabled,
        top_k=payload.top_k,
    )

    # Persist the exchange
    await memory.save_turn(session_id, payload.query, response.answer.model_dump_json())

    return response
