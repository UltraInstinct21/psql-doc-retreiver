import asyncio
import asyncpg
import json
import logging
import time
from pathlib import Path

from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGEngine, PGVectorStore
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHUNKS_DIR = Path("chunks")
POSTGRES_USER = "sarthi"
POSTGRES_PASSWORD = "2106"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DB = "rag_db_qwen3"
TABLE_NAME = "pg_docs_topicwise"
VECTOR_SIZE = 1024
BATCH_SIZE = 64

CONNECTION_STRING = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)


def load_documents():
    docs = []
    chunks_dir = Path("chunks_final") if Path("chunks_final").exists() else CHUNKS_DIR
    for path in sorted(chunks_dir.glob("*.json")):
        with path.open() as f:
            chunk = json.load(f)

        content = chunk.get("content", "").strip()
        if not content:
            continue

        docs.append(
            Document(
                page_content=content,
                metadata={
                    "heading": chunk.get("heading", ""),
                    "level": chunk.get("level", -1),
                    "source": path.name,
                },
            )
        )

    return docs


async def main():
    docs = load_documents()
    logger.info("Loaded %s documents", len(docs))

    embedding_model = OllamaEmbeddings(
        model="qwen3-embedding:8b",
        dimensions=1024,
    )

    pg_engine = PGEngine.from_connection_string(CONNECTION_STRING)
    try:
        await pg_engine.ainit_vectorstore_table(
            table_name=TABLE_NAME,
            vector_size=VECTOR_SIZE,
        )
    except Exception as e:
        logger.info("Table already exists or initialization skipped: %s", e)

    db_url = CONNECTION_STRING.replace("postgresql+asyncpg://", "postgresql://")
    try:
        conn = await asyncpg.connect(db_url)
        await conn.execute(f"CREATE INDEX IF NOT EXISTS pg_docs_hnsw_idx ON {TABLE_NAME} USING hnsw (embedding vector_cosine_ops);")
        await conn.execute(f"CREATE INDEX IF NOT EXISTS pg_docs_fts_idx ON {TABLE_NAME} USING gin(to_tsvector('english', content));")
        await conn.close()
        logger.info("Database vector and FTS indexes initialized.")
    except Exception as e:
        logger.warning("Database index creation skipped/failed: %s", e)

    store = await PGVectorStore.create(
        engine=pg_engine,
        table_name=TABLE_NAME,
        embedding_service=embedding_model,
    )

    # Check current count for resuming
    db_url = CONNECTION_STRING.replace("postgresql+asyncpg://", "postgresql://")
    try:
        conn = await asyncpg.connect(db_url)
        current_count = await conn.fetchval(f"SELECT count(*) FROM {TABLE_NAME}")
        await conn.close()
    except Exception:
        current_count = 0

    if current_count > 0:
        if current_count >= len(docs):
            logger.info("All %s documents are already embedded in the database.", len(docs))
            return
        logger.info("Found %s existing documents. Resuming from index %s", current_count, current_count)
        docs = docs[current_count:]

    start_time = time.time()
    for i in tqdm(range(0, len(docs), BATCH_SIZE), desc="Embedding"):
        await store.aadd_documents(docs[i : i + BATCH_SIZE])

    logger.info("Done in %.2fs", time.time() - start_time)


if __name__ == "__main__":
    asyncio.run(main())