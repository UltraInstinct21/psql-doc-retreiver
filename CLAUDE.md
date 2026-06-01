# PostgreSQL Documentation Retrieval System

This system implements a complete RAG (Retrieval-Augmented Generation) pipeline for PostgreSQL documentation with:

## 1. Topicwise Chunking Strategy
- **Layer 1: Structural Chunking** - Split on Part/Chapter/Section hierarchy
- **Layer 2: Semantic Sub-chunking** - Concept/syntax/example/output units within sections
- **Layer 3: Token Safety Split** - Enforce chunk token budget without breaking SQL/code blocks

Key files:
- `semantic_chunking.py` - Implements the 3-layer hybrid chunking approach
- `prepare_for_embedding.py` - Converts chunks to LangChain Document format
- `embed_process.py` - Handles embedding generation and storage in PostgreSQL

## 2. Embedding Process
- Uses BGE-large-en-v1.5 model (1024 dimensions) via HuggingFaceEmbeddings
- Stores embeddings in PostgreSQL using PGVectorStore
- Batch processing with progress tracking
- Connection details configured in embed_process.py
- Table name: pg_docs_topicwise

## 3. Hybrid Retrieval
- Dense retrieval: Vector similarity search using pgvector
- Sparse retrieval: Keyword-based scoring via metadata matching
- Hybrid fusion: Combines semantic and metadata scores with configurable weights
- Reranking: Cross-encoder (BAAI/bge-reranker-large) for relevance scoring

## 4. Usage Workflow
1. Run semantic chunking: `python semantic_chunking.py`
2. Prepare documents: `python prepare_for_embedding.py`
3. Generate embeddings: `python embed_process.py`
4. Query system: Use retriever.py or rag_chat.py

## 5. Directory Structure
- `output/` - Raw parsed document chunks
- `rag_chunks/` - Processed semantic chunks (JSON/JSONL/CSV)
- `chunks/` - PDF chunks from initial processing
- `code_split/` - Separated code/explanation blocks
- `venv/` - Python virtual environment
- `*.json` - Various intermediate data files

## 6. Configuration
- Database: PostgreSQL with pgvector extension
- Model: BAAI/bge-large-en-v1.5
- Chunk size: Target 650 tokens (min 80 tokens)
- Embedding batch size: 64