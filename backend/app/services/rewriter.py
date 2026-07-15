from __future__ import annotations

import asyncio
import json
import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.app.core.config import settings
from backend.app.schemas.chat import QueryRewritePlan


class QueryRewriter:
    def __init__(self) -> None:
        self._chain = None
        self._logger = logging.getLogger(__name__)
        if settings.gemini_api_key:
            prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    """
You are QueryRewriteAgent for a PostgreSQL documentation RAG system.

Goal:
- Rewrite the user query for retrieval, not for answering.
- Use the conversation history to resolve coreferences, context, and follow-ups.
- Produce retrieval-friendly language that matches documentation vocabulary.
- Keep rewrites concise, factual, and grounded in the user query.

Required output:
- Return JSON only.
- Use exactly these keys:
  - intent: one of [sql_syntax, definition, how_to, debugging, conceptual, api_lookup, configuration]
  - rewritten_query: a single canonical retrieval query
  - search_queries: 2 to 3 short retrieval queries ordered by usefulness
  - rerank_query: the best single query for cross-encoder reranking
  - entities: object with keys table_name, function_name, api, class_name, library_name
  - difficulty: one of [beginner, intermediate, advanced]

Rewrite rules:
- Normalize casual wording into technical terms. Examples: show entries -> SELECT rows, get data -> retrieve rows, combine tables -> JOIN, add row -> INSERT, remove data -> DELETE.
- Canonicalize SQL when possible. Example: code to see all entries in customers table -> SELECT * FROM customers.
- If the query is about concepts, bias toward tutorial, overview, concept, and example terms.
- If the query is about errors, bias toward error, fix, permission, timeout, and troubleshooting terms.
- If the query mentions a concrete entity, extract it into the entities object.
- Generate short multi-queries that preserve the original meaning without drifting to unrelated topics.
- Do not invent facts, schema, or APIs that are not in the user query.
- Do not add explanation text, markdown, or code fences.
""",
                ),
                (
                    "user",
                    "CONVERSATION_HISTORY:\n{history}\n\nUSER_QUERY:\n{query}\n\nRewrite this query for retrieval, taking history into account. Return JSON only.",
                ),
            ])
            llm = ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                temperature=0.2,
                google_api_key=settings.gemini_api_key,
            )
            self._chain = prompt | llm | StrOutputParser()

    def _default_plan(self, query: str) -> QueryRewritePlan:
        return QueryRewritePlan(
            intent="conceptual",
            rewritten_query=query,
            search_queries=[query],
            rerank_query=query,
        )

    def _normalize_plan(self, raw: str, query: str) -> QueryRewritePlan:
        try:
            data = json.loads(raw)
        except Exception as err:
            # Attempt to extract a JSON object from the raw text as a fallback
            import re

            m = re.search(r"\{.*\}", raw, re.S)
            if m:
                try:
                    data = json.loads(m.group(0))
                except Exception as err2:
                    self._logger.warning(
                        "Failed to parse extracted JSON from rewriter output, returning default plan. err1=%s err2=%s output=%r",
                        err,
                        err2,
                        raw,
                    )
                    return self._default_plan(query)
            else:
                self._logger.warning("Failed to parse rewriter LLM output, returning default plan. error=%s output=%r", err, raw)
                return self._default_plan(query)

        search_queries = data.get("search_queries") or [data.get("rewritten_query", query)]
        if isinstance(search_queries, str):
            search_queries = [search_queries]
        search_queries = [str(item).strip() for item in search_queries if str(item).strip()]
        if query not in search_queries:
            search_queries.insert(0, query)
        search_queries = search_queries[: settings.query_rewrite_limit]

        entities = data.get("entities") or {}
        if not isinstance(entities, dict):
            entities = {}

        return QueryRewritePlan(
            intent=str(data.get("intent", "conceptual")),
            rewritten_query=str(data.get("rewritten_query", query)).strip(),
            search_queries=search_queries,
            rerank_query=str(data.get("rerank_query", data.get("rewritten_query", query))).strip(),
            entities={
                "table_name": entities.get("table_name"),
                "function_name": entities.get("function_name"),
                "api": entities.get("api"),
                "class_name": entities.get("class_name"),
                "library_name": entities.get("library_name"),
            },
            difficulty=str(data.get("difficulty", "intermediate")),
        )

    async def rewrite(self, query: str, history: str = "") -> QueryRewritePlan:
        if not self._chain:
            return self._default_plan(query)

        try:
            raw = await asyncio.to_thread(self._chain.invoke, {"query": query, "history": history})
            self._logger.debug("Rewriter raw output: %s", raw)
            return self._normalize_plan(raw, query)
        except Exception as err:
            self._logger.warning("Query rewriting failed due to network/API error: %s. Returning default plan.", err)
            return self._default_plan(query)
