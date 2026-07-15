from __future__ import annotations

from dataclasses import dataclass, field
import os

from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str, default: str) -> tuple[str, ...]:
    raw = value or default
    return tuple(item.strip() for item in raw.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    app_name: str = "postgres-rag-api"
    api_v1_prefix: str = "/api/v1"
    postgres_user: str = os.getenv("POSTGRES_USER", "sarthi")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "2106")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: str = os.getenv("POSTGRES_PORT", "5432")
    postgres_db: str = os.getenv("POSTGRES_DB", "rag_db_qwen3")
    table_name: str = os.getenv("TABLE_NAME", "pg_docs_topicwise")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    frontend_origins: tuple[str, ...] = field(
        default_factory=lambda: _split_csv(
            os.getenv("FRONTEND_ORIGINS", "http://localhost:5173"),
            "http://localhost:5173",
        )
    )
    reranker_device: str = os.getenv("RERANKER_DEVICE", "cpu")
    embedding_device: str = os.getenv("EMBEDDING_DEVICE", "cuda")
    top_k: int = int(os.getenv("TOP_K", "5"))
    retrieval_k: int = int(os.getenv("RETRIEVAL_K", "20"))
    query_rewrite_limit: int = int(os.getenv("QUERY_REWRITE_LIMIT", "3"))

    @property
    def connection_string(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def pg_connection_string(self) -> str:
        """Plain postgresql:// connection string (for psycopg pools)."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
