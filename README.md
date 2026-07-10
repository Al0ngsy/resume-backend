# Resume Backend

AI-powered resume chatbot backend for Le Quoc Anh Tran, Backend Software Engineer.

Serve as Python learning project.

## Tech Stack

- **Framework:** FastAPI
- **Language:** Python 3.11+
- **Package Manager:** uv
- **LLM Abstraction:** OpenAI-compatible (Ollama → OpenRouter)
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

| Method | Path                      | Description              |
| ------ | ------------------------- | ------------------------ |
| GET    | `/`                       | Root                     |
| GET    | `/api/health`             | Health check + uptime    |
| POST   | `/api/chat`               | Chat with the AI (v1)    |
| POST   | `/api/conversations`      | Create new conversation  |
| GET    | `/api/conversations/{id}` | Get conversation history |

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
└── FastAPI route handlers

Core Layer
├── Prompt builder (data/* → system prompt)
├── LLM abstraction (swappable providers)
├── Conversation store (in-memory → external DB)
└── Conversation logger (structured JSON)

```

## Environment Variables

| Variable                      | Description                                | Default                     |
| ----------------------------- | ------------------------------------------ | --------------------------- |
| `LLM_PROVIDER`                | LLM provider: ollama, openrouter | `ollama`                    |
| `OLLAMA_BASE_URL`             | Ollama API base URL                        | `http://localhost:11434/v1` |
| `OLLAMA_MODEL`                | Ollama model name                          | `llama3.2`                  |
| `OLLAMA_API_KEY`              | Ollama API key                             | —                           |
| `RATE_LIMIT_PER_IP`           | Requests per IP                            | `10/minute`                 |
| `RATE_LIMIT_PER_CONVERSATION` | Requests per conversation                  | `30/5minutes`               |
| `CORS_ORIGINS`                | Allowed CORS origins                       | `http://localhost:3000`     |
| `LOG_LEVEL`                   | Log level                                  | `info`                      |

## Phases

| Phase  | What                                                                                       | Hosting |
| ------ | ------------------------------------------------------------------------------------------ | ------- |
| **v1** | Dump context into prompt. LLM abstraction. Rate limiting. In-memory conversation store.    | Render  |
| **v2** | RAG + vector DB. Replace in-memory conversation store with external DB (PostgreSQL/Redis). | Oracle  |

### Conversation Store

The server manages conversation history server-side, keyed by `x-conversation-id`.

- **Phase 1 (current):** `src/conversation_store.py` stores conversations in an in-memory `dict`. This is ephemeral — data is lost on restart.
- **Phase 2 (planned):** Replace `src/conversation_store.py` with a database-backed implementation (e.g. PostgreSQL via SQLAlchemy, or Redis). The public API (`create_conversation`, `get_history`, `append_messages`) stays the same, so the swap is a drop-in replacement.

The client no longer sends `history` in the request body. Instead:

1. The client sends `x-conversation-id` header (or omits it for a new conversation).
2. The server retrieves the full history from the store.
3. After generating a response, the server appends the user message + assistant response to the store.
4. The response includes the `conversation_id` so the client can persist it for subsequent requests.
