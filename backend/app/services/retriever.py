from __future__ import annotations

import asyncio
import os
import re
from functools import lru_cache

try:
    import torch
except Exception:  # pragma: no cover
    torch = None

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGEngine, PGVectorStore
from sentence_transformers import CrossEncoder

from backend.app.core.config import settings
from backend.app.schemas.chat import RetrievedChunk


def _pick_reranker_device() -> str:
    if settings.reranker_device == "auto":
        return "cuda" if torch and torch.cuda.is_available() else "cpu"
    if settings.reranker_device == "cuda" and not (torch and torch.cuda.is_available()):
        return "cpu"
    return settings.reranker_device


@lru_cache(maxsize=1)
def _build_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs={"device": settings.embedding_device},
        encode_kwargs={"normalize_embeddings": True},
    )


@lru_cache(maxsize=1)
def _build_reranker() -> CrossEncoder:
    return CrossEncoder(
        "BAAI/bge-reranker-large",
        max_length=512,
        device=_pick_reranker_device(),
        trust_remote_code=True,
        cache_folder=os.path.expanduser("~/.cache/huggingface"),
    )


def _query_terms(query: str) -> set[str]:
    return {word.lower() for word in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]+", query)}


def _keyword_score(query_terms: set[str], doc) -> float:
    text = f"{doc.metadata.get('heading', '')} {doc.page_content}".lower()
    words = set(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]+", text))
    if not query_terms:
        return 0.0
    return min(1.0, len(query_terms & words) / len(query_terms))


def _doc_identity(doc) -> str:
    meta = doc.metadata or {}
    return str(meta.get("chunk_id") or meta.get("heading") or doc.page_content[:120])


def _chunk_to_result(doc, score: float) -> RetrievedChunk:
    title = str((doc.metadata or {}).get("heading") or "Untitled")
    source = str((doc.metadata or {}).get("source") or settings.table_name)
    snippet = re.sub(r"\s+", " ", doc.page_content).strip()[:240]
    return RetrievedChunk(title=title, score=float(score), snippet=snippet, source=source)


class RetrieverService:
    def __init__(self) -> None:
        self._store = None
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return

        engine = PGEngine.from_connection_string(settings.connection_string)
        self._store = await PGVectorStore.create(
            engine=engine,
            table_name=settings.table_name,
            embedding_service=_build_embedding_model(),
        )
        self._initialized = True

    async def retrieve(self, search_queries: list[str], rerank_query: str, top_k: int | None = None, candidate_k: int | None = None) -> list[RetrievedChunk]:
        await self.initialize()

        top_k = top_k or settings.top_k
        candidate_k = candidate_k or settings.retrieval_k

        scored: dict[str, tuple] = {}
        for search_query in search_queries:
            try:
                pairs = await self._store.asimilarity_search_with_score(search_query, k=candidate_k)
                docs = [(doc, float(score), search_query) for doc, score in pairs]
            except Exception:
                docs = [
                    (doc, float(i), search_query)
                    for i, doc in enumerate(await self._store.asimilarity_search(search_query, k=candidate_k))
                ]

            for doc, score, source_query in docs:
                ident = _doc_identity(doc)
                if ident not in scored or score < scored[ident][1]:
                    scored[ident] = (doc, score, source_query)

        if not scored:
            return []

        query_terms = _query_terms(rerank_query)
        scored_list = list(scored.values())
        scored_list.sort(key=lambda item: item[1])
        total = max(1, len(scored_list) - 1)

        hybrid = []
        for rank, (doc, _, source_query) in enumerate(scored_list):
            semantic = 1.0 - (rank / total)
            keyword = _keyword_score(query_terms, doc)
            query_bonus = 0.05 if source_query == search_queries[0] else 0.0
            hybrid.append((doc, 0.7 * semantic + 0.3 * keyword + query_bonus))

        hybrid.sort(key=lambda item: item[1], reverse=True)
        docs = [doc for doc, _ in hybrid[:candidate_k]]
        if not docs:
            return []

        try:
            rerank_scores = _build_reranker().predict([(rerank_query, doc.page_content) for doc in docs])
            order = sorted(range(len(rerank_scores)), key=lambda i: rerank_scores[i], reverse=True)[:top_k]
            final_docs = [docs[i] for i in order]
            return [_chunk_to_result(doc, rerank_scores[idx]) for doc, idx in zip(final_docs, order)]
        except Exception:
            return [_chunk_to_result(doc, hybrid[idx][1]) for idx, doc in enumerate(docs[:top_k])]
