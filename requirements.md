# Requirements

This document lists the relevant packages required to run the `psql-doc-retreiver` project.

## Core Dependencies

These are the primary packages directly imported and utilized within the project's source code:

- **fastapi** (`0.135.3`): Framework for the web API backend.
- **langchain-core** (`1.2.28`): Core LangChain abstractions.
- **langchain-huggingface** (`1.2.1`): Used for `HuggingFaceEmbeddings`.
- **langchain-postgres** (`0.0.17`): Integrating PostgreSQL via `PGEngine` and `PGVectorStore`.
- **langchain-ollama** (`1.1.0`): Integration for querying local `ChatOllama` models. 
- **langchain-google-genai**: Integration for Gemini-based response generation.
- **tqdm** (`4.67.3`): Required for displaying progress loops in processing scripts.
- **python-dotenv**: Loads API keys and runtime config from `.env`.

## Database & Model Providers

- **psycopg** (`3.3.3`): PostgreSQL database adapter for Python (underlying library for `langchain-postgres`).
- **SQLAlchemy** (`2.0.49`): Underlying database toolkit.
- **sentence-transformers** (`5.3.0`): For computing HuggingFace embeddings.

## Web Server

- **uvicorn** (`0.44.0`): The ASGI web server implementation for FastAPI.
- **httpx** (`0.28.1`): For asynchronous HTTP client operations.

## Additional Utils & Processing

- **PyMuPDF** (`1.27.2.2`): Useful for PDF manipulation and extraction.
- **jupyter** (`1.1.1`): For testing and prototyping iteratively.

---

> **Note**: To fully install the environment programmatically, consider generating a `requirements.txt` via `pip freeze > requirements.txt`.
