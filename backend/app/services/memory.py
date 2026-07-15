from __future__ import annotations

import uuid
import logging

import psycopg
from langchain_core.messages import HumanMessage, AIMessage
from langchain_postgres import PostgresChatMessageHistory
from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)

CHAT_HISTORY_TABLE = "chat_history"
DEFAULT_WINDOW = 5


class SessionMemory:
    """Session-level chat history backed by PostgresChatMessageHistory.

    Uses a shared async connection pool — one checkout per request,
    lightweight with no connection leak.
    """

    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._pool = pool

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def get_recent_context(self, session_id: str, last_k: int = DEFAULT_WINDOW) -> str:
        """Return the last *last_k* conversational turns as ``User: …\nAssistant: …``.

        Returns empty string when there is no history.
        """
        conn, history = await self._connect(session_id)
        try:
            messages = await history.aget_messages()
        finally:
            await self._release(conn)

        turns = [m for m in messages if isinstance(m, HumanMessage | AIMessage)]
        window = turns[-last_k * 2:]

        if not window:
            return ""

        lines: list[str] = []
        for msg in window:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            lines.append(f"{role}: {msg.content}")
        return "\n".join(lines)

    async def save_turn(self, session_id: str, user_query: str, assistant_answer: str) -> None:
        """Persist one user → assistant exchange."""
        conn, history = await self._connect(session_id)
        try:
            await history.aadd_messages([
                HumanMessage(content=user_query),
                AIMessage(content=assistant_answer),
            ])
        finally:
            await self._release(conn)

    async def clear_session(self, session_id: str) -> None:
        """Delete all messages for a session."""
        conn, history = await self._connect(session_id)
        try:
            await history.aclear()
        finally:
            await self._release(conn)

    @staticmethod
    async def create_tables(pool: AsyncConnectionPool) -> None:
        """One-time schema bootstrap (CREATE TABLE IF NOT EXISTS). Idempotent."""
        conn = await pool.getconn()
        try:
            await PostgresChatMessageHistory.acreate_tables(conn, CHAT_HISTORY_TABLE)
            logger.info("Ensured chat_history table exists.")
        finally:
            await pool.putconn(conn)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _connect(self, session_id: str) -> tuple[psycopg.AsyncConnection, PostgresChatMessageHistory]:
        conn: psycopg.AsyncConnection = await self._pool.getconn()
        try:
            uuid.UUID(session_id)
        except ValueError:
            await self._pool.putconn(conn)
            raise ValueError(f"session_id must be a valid UUID, got {session_id!r}")
        return conn, PostgresChatMessageHistory(
            CHAT_HISTORY_TABLE,
            session_id,
            async_connection=conn,
        )

    async def _release(self, conn: psycopg.AsyncConnection) -> None:
        await self._pool.putconn(conn)
