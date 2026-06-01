import asyncio
import json
import logging
import time
from pathlib import Path

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGEngine, PGVectorStore
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHUNKS_DIR = Path("chunks")
POSTGRES_USER = "sarthi"
POSTGRES_PASSWORD = "2106"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DB = "rag_db"
TABLE_NAME = "pg_docs_topicwise_v1"
VECTOR_SIZE = 1024
BATCH_SIZE = 64

CONNECTION_STRING = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)


def load_documents():
    docs = []
    for path in sorted(CHUNKS_DIR.glob("*.json")):
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

    embedding_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs={"device": "cuda"},
        encode_kwargs={"normalize_embeddings": True, "batch_size": 16},
    )

    pg_engine = PGEngine.from_connection_string(CONNECTION_STRING)
    await pg_engine.ainit_vectorstore_table(
        table_name=TABLE_NAME,
        vector_size=VECTOR_SIZE,
    )

    store = await PGVectorStore.create(
        engine=pg_engine,
        table_name=TABLE_NAME,
        embedding_service=embedding_model,
    )

    start_time = time.time()
    for i in tqdm(range(0, len(docs), BATCH_SIZE), desc="Embedding"):
        await store.aadd_documents(docs[i : i + BATCH_SIZE])

    logger.info("Done in %.2fs", time.time() - start_time)


if __name__ == "__main__":
    asyncio.run(main())