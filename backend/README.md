# Backend

Production-ready FastAPI scaffold for the PostgreSQL RAG app.

## Structure

- `app/core` - environment and app settings
- `app/schemas` - request/response models
- `app/services` - query rewrite, retrieval, and generation pipeline
- `app/api/v1/endpoints` - chat, rewrite, retrieval, and health routes

## Endpoints

- `GET /api/v1/health`
- `POST /api/v1/rewrite`
- `POST /api/v1/retrieval`
- `POST /api/v1/chat`

## Run

```bash
cd /home/sarthi/Projects/psql-doc-retreiver
uvicorn backend.app.main:app --reload
```
