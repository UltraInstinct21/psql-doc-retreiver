from __future__ import annotations

import math
import os
import re
from functools import lru_cache

try:
    import torch
except Exception:  # pragma: no cover
    torch = None

import json
import asyncpg
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
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
def _build_embedding_model() -> OllamaEmbeddings:
    return OllamaEmbeddings(
        model="qwen3-embedding:8b",
        dimensions=1024,
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


def _doc_identity(doc) -> str:
    meta = doc.metadata or {}
    return str(meta.get("chunk_id") or meta.get("heading") or doc.page_content[:120])


def _sigmoid(x: float) -> float:
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


def _chunk_to_result(doc, score: float) -> RetrievedChunk:
    title = str((doc.metadata or {}).get("heading") or "Untitled")
    source = str((doc.metadata or {}).get("source") or settings.table_name)
    snippet = re.sub(r"\s+", " ", doc.page_content).strip()[:240]
    return RetrievedChunk(title=title, score=float(score), snippet=snippet, content=doc.page_content, source=source)


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

    async def _fetch_fts_results(self, query: str, limit: int) -> list[tuple[Document, float]]:
        db_url = settings.connection_string.replace("postgresql+asyncpg://", "postgresql://")
        try:
            conn = await asyncpg.connect(db_url)
            rows = await conn.fetch(
                f"""
                SELECT content, langchain_metadata, 
                       ts_rank_cd(to_tsvector('english', content), websearch_to_tsquery('english', $1)) as rank
                FROM {settings.table_name}
                WHERE to_tsvector('english', content) @@ websearch_to_tsquery('english', $1)
                ORDER BY rank DESC
                LIMIT $2;
                """,
                query,
                limit
            )
            await conn.close()
        except Exception:
            return []

        results = []
        for row in rows:
            meta = json.loads(row['langchain_metadata']) if isinstance(row['langchain_metadata'], str) else row['langchain_metadata']
            doc = Document(page_content=row['content'], metadata=meta)
            results.append((doc, float(row['rank'])))
        return results

    async def retrieve(
        self,
        search_queries: list[str],
        rerank_query: str,
        intent: str = "conceptual",
        top_k: int | None = None,
        candidate_k: int | None = None,
    ) -> list[RetrievedChunk]:
        await self.initialize()

        top_k = top_k or settings.top_k
        candidate_k = candidate_k or settings.retrieval_k

        # Collect and rank documents from vector search and full-text search
        vector_ranks = {}
        fts_ranks = {}
        doc_map = {}

        for search_query in search_queries:
            # Vector Search
            try:
                pairs = await self._store.asimilarity_search_with_score(search_query, k=candidate_k)
                pairs_sorted = sorted(pairs, key=lambda x: x[1])  # ascending distance
                for rank, (doc, _) in enumerate(pairs_sorted):
                    ident = _doc_identity(doc)
                    doc_map[ident] = doc
                    if ident not in vector_ranks or rank < vector_ranks[ident]:
                        vector_ranks[ident] = rank
            except Exception:
                pass

            # FTS Search
            fts_pairs = await self._fetch_fts_results(search_query, limit=candidate_k)
            fts_sorted = sorted(fts_pairs, key=lambda x: x[1], reverse=True)  # descending rank
            for rank, (doc, _) in enumerate(fts_sorted):
                ident = _doc_identity(doc)
                doc_map[ident] = doc
                if ident not in fts_ranks or rank < fts_ranks[ident]:
                    fts_ranks[ident] = rank

        if not doc_map:
            return []

        # Determine Reciprocal Rank Fusion (wRRF) weights based on query intent
        intent_lower = intent.lower() if intent else "conceptual"
        if intent_lower in ("entity", "code", "syntax"):
            v_weight = 0.4
            f_weight = 0.6
        elif intent_lower in ("conceptual", "explanation"):
            v_weight = 0.7
            f_weight = 0.3
        else:
            v_weight = 0.5
            f_weight = 0.5

        # Weighted Reciprocal Rank Fusion (wRRF)
        rrf_scores = {}
        for ident in doc_map:
            v_rank = vector_ranks.get(ident, 9999)
            f_rank = fts_ranks.get(ident, 9999)
            
            # contribution score (k=60) with dynamic weights
            v_score = v_weight / (60 + v_rank + 1) if v_rank < 9999 else 0.0
            f_score = f_weight / (60 + f_rank + 1) if f_rank < 9999 else 0.0
            
            rrf_scores[ident] = v_score + f_score

        # Sort combined documents by RRF score descending
        sorted_rrf = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        hybrid = [(doc_map[ident], score) for ident, score in sorted_rrf]

        docs = [doc for doc, _ in hybrid[:candidate_k]]
        if not docs:
            return []

        try:
            rerank_scores = _build_reranker().predict([(rerank_query, doc.page_content) for doc in docs])
            order = sorted(range(len(rerank_scores)), key=lambda i: rerank_scores[i], reverse=True)[:top_k]
            final_docs = [docs[i] for i in order]
            return [_chunk_to_result(doc, _sigmoid(float(rerank_scores[idx]))) for doc, idx in zip(final_docs, order)]
        except Exception:
            return [_chunk_to_result(doc, hybrid[idx][1]) for idx, doc in enumerate(docs[:top_k])]
