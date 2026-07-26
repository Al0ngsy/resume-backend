# Resume Backend

AI-powered resume chatbot backend for Le Quoc Anh Tran, Backend Software Engineer.

Serve as Python learning project.

## Tech Stack

- **Framework:** FastAPI
- **Language:** Python 3.11+
- **Package Manager:** uv
- **LLM Abstraction:** OpenAI-compatible (Ollama → OpenRouter)
- **Database:** Neon PostgreSQL + pgvector (RAG vector search + conversation persistence)
- **Embeddings:** Jina AI (jina-embeddings-v3, 1024 dims) — 10M free tokens
- **Validation:** Pydantic v2 + pydantic-settings
- **Rate Limiting:** slowapi (per-IP + per-conversation)
- **Logging:** structlog (structured JSON)
- **Server:** uvicorn

## Getting Started

```bash
# Install dependencies
uv sync

# Copy and configure environment
cp .env.example .env

# Run database migrations
uv run alembic upgrade head

# Run dev server
uv run uvicorn src.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000). Health check at `/api/health`.

## Testing

```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run a specific test file
uv run pytest tests/test_guard.py -v

# Run a specific test by name
uv run pytest -k "injection" -v
```

## API Endpoints

```bash

| Method | Path                      | Description                          |
| ------ | ------------------------- | ------------------------------------ |
| GET    | `/`                       | Root                                 |
| GET    | `/api/health`             | Health check + uptime                 |
| POST   | `/api/chat`               | Chat with the AI (non-streaming)     |
| POST   | `/api/chat/stream`         | Chat with the AI (SSE streaming + step progress) |
| POST   | `/api/conversations`      | Create new conversation              |
| GET    | `/api/conversations/{id}` | Get conversation history            |
| POST   | `/api/admin/reindex`       | Re-index RAG documents               |

```

## Architecture

```bash

Middleware Layer
├── CORS (Cloudflare Pages origin)
├── Rate limiter (per IP + per conversation)
└── Request ID injection

Guard Layer
├── Input validation (prompt injection scan)
├── Content safety (topic/policy check)
└── Output filtering (PII leak prevention)

Router Layer
├── Chat endpoints (SSE streaming with step events + RAG)
├── Conversation endpoints (DB-backed)
├── Health endpoint
└── Admin endpoints (reindex)

Core Layer
├── Prompt builder (safety preamble + RAG context)
├── LLM abstraction (swappable providers)
├── RAG pipeline (PDF extraction → chunking → embedding → vector search)
├── Embedding service (Jina AI, 1024 dims)
├── Conversation store (Neon PostgreSQL via SQLAlchemy 2.0 async)
└── Structured logging (structlog JSON)

```

## RAG Pipeline

The chatbot uses Retrieval-Augmented Generation (RAG) to answer recruiter questions:

1. User question is embedded via Jina AI (jina-embeddings-v3, 1024 dimensions)
2. pgvector cosine similarity search retrieves the top-5 most relevant document chunks
3. Retrieved chunks are injected into the system prompt as context
4. The LLM generates a response grounded in that context

### Data Sources

| Source   | File                                              | Description                      |
| -------- | ------------------------------------------------- | -------------------------------- |
| `pdf_en` | `resume-frontend/public/lequocanh_tran_cv_en.pdf` | English CV PDF                   |
| `pdf_de` | `resume-frontend/public/lequocanh_tran_cv_de.pdf` | German CV PDF                    |
| `qa`     | `resume-backend/data/mock-qa.json`                | Recruiter Q&A pairs (JSON array) |

Each source is extracted (PDFs via PyMuPDF, JSON parsed directly), chunked into
~500-token overlapping segments, embedded, and stored in the `documents` table
with a pgvector HNSW cosine index.

### Re-indexing (When Data Changes)

When you add or change a CV PDF or the Q&A file, you need to re-embed the changed
source so the RAG pipeline retrieves the updated content. There are two modes:

#### Full Re-index (all sources)

Re-embeds everything — all PDFs and the Q&A file. Use this when multiple sources
changed or for a clean reset:

```bash
# Local
curl -X POST http://localhost:8000/api/admin/reindex \
  -H "X-API-Key: <your-api-key>"

# Production
curl -X POST https://resume-backend-66rk.onrender.com/api/admin/reindex \
  -H "X-API-Key: <your-api-key>"
```

Response:

```json
{
  "status": "ok",
  "message": "Re-indexing complete",
  "summary": { "pdf_en": 4, "pdf_de": 5, "qa": 41 }
}
```

#### Incremental Re-index (single source)

Re-embeds only one source — the other sources stay untouched. Use this when you
only changed one file to save embedding API calls and time:

```bash
# Re-index only the English PDF (e.g., after updating the EN CV)
curl -X POST "http://localhost:8000/api/admin/reindex?source=pdf_en" \
  -H "X-API-Key: <your-api-key>"

# Re-index only the German PDF
curl -X POST "http://localhost:8000/api/admin/reindex?source=pdf_de" \
  -H "X-API-Key: <your-api-key>"

# Re-index only the Q&A pairs (e.g., after adding/editing mock-qa.json)
curl -X POST "http://localhost:8000/api/admin/reindex?source=qa" \
  -H "X-API-Key: <your-api-key>"
```

Response:

```json
{
  "status": "ok",
  "message": "Re-indexed source 'qa'",
  "source": "qa",
  "chunks": 41
}
```

Valid sources: `pdf_en`, `pdf_de`, `qa`.

#### When to Use Which

| Scenario                               | Command                            |
| -------------------------------------- | ---------------------------------- |
| Updated the English CV PDF             | `?source=pdf_en`                   |
| Updated the German CV PDF              | `?source=pdf_de`                   |
| Added/edited Q&A pairs in mock-qa.json | `?source=qa`                       |
| Changed multiple files at once         | (no `source` param — full reindex) |
| Clean reset / troubleshooting          | (no `source` param — full reindex) |

The admin endpoint is rate-limited to 5 calls/day to prevent abuse.

## Environment Variables

| Variable                      | Description                       | Default                     |
| ----------------------------- | --------------------------------- | --------------------------- |
| `LLM_PROVIDER`                | LLM provider: ollama, openrouter  | `ollama`                    |
| `OLLAMA_BASE_URL`             | Ollama API base URL               | `http://localhost:11434/v1` |
| `OLLAMA_MODEL`                | Ollama model name                 | `llama3.2`                  |
| `OLLAMA_API_KEY`              | Ollama API key                    | —                           |
| `OPENROUTER_API_KEY`          | OpenRouter API key (fallback)     | —                           |
| `OPENROUTER_MODEL`            | OpenRouter model name             | —                           |
| `DATABASE_URL`                | Neon PostgreSQL connection string | —                           |
| `EMBEDDING_API_KEY`           | Jina AI API key (for embeddings)  | —                           |
| `EMBEDDING_BASE_URL`          | Embedding API base URL            | `https://api.jina.ai/v1`    |
| `EMBEDDING_MODEL`             | Embedding model name              | `jina-embeddings-v3`        |
| `EMBEDDING_DIMENSIONS`        | Embedding vector dimensions       | `1024`                      |
| `RATE_LIMIT_PER_IP`           | Requests per IP                   | `10/minute`                 |
| `RATE_LIMIT_PER_CONVERSATION` | Requests per conversation         | `30/5minutes`               |
| `CORS_ORIGINS`                | Allowed CORS origins              | `http://localhost:3000`     |
| `API_KEY`                     | Shared secret for frontend auth   | —                           |
| `LOG_LEVEL`                   | Log level                         | `info`                      |

## Database Migrations

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Generate a new migration after model changes
uv run alembic revision --autogenerate -m "description_of_change"

# Rollback one migration
uv run alembic downgrade -1
```
