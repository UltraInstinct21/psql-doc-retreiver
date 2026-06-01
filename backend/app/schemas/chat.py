from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class QueryRewritePlan(BaseModel):
    intent: str = "conceptual"
    rewritten_query: str = ""
    search_queries: list[str] = Field(default_factory=list)
    rerank_query: str = ""
    entities: dict[str, str | None] = Field(
        default_factory=lambda: {
            "table_name": None,
            "function_name": None,
            "api": None,
            "class_name": None,
            "library_name": None,
        }
    )
    difficulty: str = "intermediate"


class RetrievedChunk(BaseModel):
    title: str
    score: float
    snippet: str
    source: str


class AnswerPayload(BaseModel):
    sql: str = ""
    explanation: str = ""
    optimization_notes: str = ""
    assumptions: str = ""


class ChatRequest(BaseModel):
    query: str = Field(min_length=1)
    retrieval_enabled: bool = True
    top_k: int | None = None


class RewriteRequest(BaseModel):
    query: str = Field(min_length=1)


class RetrievalRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int | None = None


class RewriteResponse(BaseModel):
    query: str
    rewrite: QueryRewritePlan


class RetrievalResponse(BaseModel):
    query: str
    rewrite: QueryRewritePlan
    chunks: list[RetrievedChunk]


class ChatResponse(BaseModel):
    query: str
    rewrite: QueryRewritePlan
    answer: AnswerPayload
    chunks: list[RetrievedChunk]
    retrieval_enabled: bool = True
