# PostgreSQL Documentation Retrieval System

RAG pipeline for querying PostgreSQL documentation using hybrid retrieval (dense + sparse) with cross-encoder reranking, with a React frontend and FastAPI backend.

## System Architecture

```
Frontend (Vite + React)  →  Backend (FastAPI)  →  PGVector (pgvector)
     :5173                      :8000                   :5432
```

## Pipeline

1. **Chunking** — Topic-wise semantic chunking (structural → semantic → token-safe split)
2. **Embedding** — BGE-large-en-v1.5 → PGVectorStore (1024 dims)
3. **Retrieval** — Hybrid search (vector + keyword) with BAAI/bge-reranker-large

## Setup

### Backend

```bash
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env          # fill in GEMINI_API_KEY
cp backend/.env.example backend/.env   # fill in DB + API key
```

Requires PostgreSQL with pgvector extension.

### Frontend

```bash
cd Frontend/psql-generator
npm install
```

## Usage

### 1. Process docs and generate embeddings

```bash
python topicwise_chunking.py    # chunk PDF into semantic sections
python embed_process.py         # generate & store embeddings
```

### 2. Start the backend

```bash
uvicorn backend.app.main:app --reload --port 8000
```

### 3. Start the frontend

```bash
cd Frontend/psql-generator
npm run dev
```

Open `http://localhost:5173` in your browser.

### CLI querying (alternative)

```bash
python retreiver.py             # direct query interface
python rag_chat.py              # interactive chat with Gemini
```
