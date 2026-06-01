from __future__ import annotations

import asyncio
import json
import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.app.core.config import settings
from backend.app.schemas.chat import AnswerPayload, RetrievedChunk, QueryRewritePlan


class AnswerGenerator:
    def __init__(self) -> None:
        self._chain = None
        self._logger = logging.getLogger(__name__)
        if settings.gemini_api_key:
            prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    """
You are a PostgreSQL documentation assistant.

Return JSON only with keys:
- sql
- explanation
- optimization_notes
- assumptions

Rules:
- Answer using the provided context only.
- If the user asks for SQL, put the query in sql.
- Keep explanation concise and technical.
- Keep optimization_notes focused on query performance or schema guidance.
- Keep assumptions explicit and minimal.
- Do not add markdown or code fences.
""",
                ),
                (
                    "user",
                    "QUESTION:\n{question}\n\nREWRITE:\n{rewrite}\n\nCONTEXT:\n{context}\n\nReturn JSON only.",
                ),
            ])
            llm = ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                temperature=0.2,
                google_api_key=settings.gemini_api_key,
            )
            self._chain = prompt | llm | StrOutputParser()

    def _default_answer(self) -> AnswerPayload:
        return AnswerPayload(
            sql="",
            explanation="Set GEMINI_API_KEY to enable answer generation.",
            optimization_notes="",
            assumptions="",
        )

    def _build_context(self, chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return ""
        blocks = []
        for chunk in chunks:
            blocks.append(
                f"TITLE: {chunk.title}\nSOURCE: {chunk.source}\nSCORE: {chunk.score:.4f}\nSNIPPET: {chunk.snippet}"
            )
        return "\n\n---\n\n".join(blocks)

    def _parse_payload(self, raw: str) -> AnswerPayload:
        try:
            data = json.loads(raw)
        except Exception as err:
            self._logger.warning("Failed to parse generator LLM output, returning default answer. error=%s output=%r", err, raw)
            return self._default_answer()

        return AnswerPayload(
            sql=str(data.get("sql", "")).strip(),
            explanation=str(data.get("explanation", "")).strip(),
            optimization_notes=str(data.get("optimization_notes", "")).strip(),
            assumptions=str(data.get("assumptions", "")).strip(),
        )

    async def generate(self, question: str, rewrite: QueryRewritePlan, chunks: list[RetrievedChunk]) -> AnswerPayload:
        if not self._chain:
            return self._default_answer()

        context = self._build_context(chunks)
        raw = await asyncio.to_thread(
            self._chain.invoke,
            {"question": question, "rewrite": rewrite.model_dump_json(), "context": context},
        )
        return self._parse_payload(raw)
