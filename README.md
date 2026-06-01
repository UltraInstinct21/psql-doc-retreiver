# PostgreSQL Documentation Retrieval System

RAG pipeline for querying PostgreSQL documentation using hybrid retrieval (dense + sparse) with cross-encoder reranking.

## Pipeline

1. **Chunking** — Topic-wise semantic chunking (structural → semantic → token-safe split)
2. **Embedding** — BGE-large-en-v1.5 → PGVectorStore (1024 dims)
3. **Retrieval** — Hybrid search (vector + keyword) with BAAI/bge-reranker-large

## Usage

```bash
python topicwise_chunking.py    # Step 1: chunk docs
python embed_process.py         # Step 2: generate & store embeddings
python retreiver.py             # Step 3: query the system
python rag_chat.py              # Or use the interactive chat
```

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your GEMINI_API_KEY
```

Requires PostgreSQL with pgvector extension.
