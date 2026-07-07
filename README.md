# Resume Backend

AI-powered resume chatbot backend for Le Quoc Anh Tran, Backend Software Engineer.

## Tech Stack

- **Framework:** FastAPI
- **Language:** Python 3.11+
- **Package Manager:** uv
- **LLM Abstraction:** OpenAI-compatible (Ollama → DeepSeek → OpenRouter)
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
uv run uvicorn resume_backend.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000). Health check at `/api/health`.

## Testing

```bash
uv run pytest
```

## API Endpoints

| Method | Path                      | Description              |
| ------ | ------------------------- | ------------------------ |
| GET    | `/`                       | Root                     |
| GET    | `/api/health`             | Health check + uptime    |
| POST   | `/api/chat`               | Chat with the AI (v1)    |
| POST   | `/api/conversations`      | Create new conversation  |
| GET    | `/api/conversations/{id}` | Get conversation history |

## Architecture

```
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
  └── Conversation logger (structured JSON)
```

## Environment Variables

| Variable                      | Description                                | Default                     |
| ----------------------------- | ------------------------------------------ | --------------------------- |
| `LLM_PROVIDER`                | LLM provider: ollama, deepseek, openrouter | `ollama`                    |
| `OLLAMA_BASE_URL`             | Ollama API base URL                        | `http://localhost:11434/v1` |
| `OLLAMA_MODEL`                | Ollama model name                          | `llama3.2`                  |
| `OLLAMA_API_KEY`              | Ollama API key                             | —                           |
| `RATE_LIMIT_PER_IP`           | Requests per IP                            | `10/minute`                 |
| `RATE_LIMIT_PER_CONVERSATION` | Requests per conversation                  | `30/5minutes`               |
| `CORS_ORIGINS`                | Allowed CORS origins                       | `http://localhost:3000`     |
| `LOG_LEVEL`                   | Log level                                  | `info`                      |

## Phases

| Phase  | What                                                      | Hosting |
| ------ | --------------------------------------------------------- | ------- |
| **v1** | Dump context into prompt. LLM abstraction. Rate limiting. | Render  |
| **v2** | RAG + vector DB + SQL persistence.                        | Oracle  |
