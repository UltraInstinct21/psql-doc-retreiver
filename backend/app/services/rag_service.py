from __future__ import annotations

from backend.app.core.config import settings
from backend.app.schemas.chat import ChatResponse, QueryRewritePlan, RetrievedChunk
from backend.app.services.generator import AnswerGenerator
from backend.app.services.retriever import RetrieverService
from backend.app.services.rewriter import QueryRewriter


class RAGService:
    def __init__(self) -> None:
        self.rewriter = QueryRewriter()
        self.retriever = RetrieverService()
        self.generator = AnswerGenerator()

    async def initialize(self) -> None:
        await self.retriever.initialize()

    async def rewrite(self, query: str) -> QueryRewritePlan:
        return await self.rewriter.rewrite(query)

    async def retrieve(self, query: str, top_k: int | None = None) -> tuple[QueryRewritePlan, list[RetrievalChunk]]:
        rewrite = await self.rewrite(query)
        chunks = await self.retriever.retrieve(
            search_queries=rewrite.search_queries,
            rerank_query=rewrite.rerank_query,
            top_k=top_k or settings.top_k,
            candidate_k=max(settings.retrieval_k, top_k or settings.top_k),
        )
        return rewrite, chunks

    async def chat(self, query: str, retrieval_enabled: bool = True, top_k: int | None = None) -> ChatResponse:
        rewrite = await self.rewrite(query)
        chunks: list[RetrievedChunk] = []
        if retrieval_enabled:
            chunks = await self.retriever.retrieve(
                search_queries=rewrite.search_queries,
                rerank_query=rewrite.rerank_query,
                top_k=top_k or settings.top_k,
                candidate_k=max(settings.retrieval_k, top_k or settings.top_k),
            )
        answer = await self.generator.generate(rewrite.rewritten_query, rewrite, chunks)
        return ChatResponse(
            query=query,
            rewrite=rewrite,
            answer=answer,
            chunks=chunks,
            retrieval_enabled=retrieval_enabled,
        )

    async def health(self) -> dict:
        return {
            "status": "ok",
            "app_name": settings.app_name,
            "table_name": settings.table_name,
            "retrieval_enabled": True,
            "generation_enabled": bool(settings.gemini_api_key),
        }
