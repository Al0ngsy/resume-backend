# Graph Report - resume-backend  (2026-07-26)

## Corpus Check
- 38 files · ~9,725 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 334 nodes · 549 edges · 21 communities (15 shown, 6 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 26 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e0f39600`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Config & LLM Provider Abstraction
- Conversation Store & Models
- Resume Content & Architecture Docs
- Guard Layer (Safety & PII)
- App Setup & Middleware
- System Prompt Builder
- Candidate Profile & Tech Stack
- Chat Endpoint Integration Tests
- pipeline.py
- Health Endpoint Tests
- LLM Chat Interface
- Project Package Root
- Chat API Endpoint
- Conversations API Endpoints
- Health API Endpoint
- Guard Layer Module
- Router Layer Module

## God Nodes (most connected - your core abstractions)
1. `Resume Backend` - 21 edges
2. `_ensure_engine()` - 16 edges
3. `chat()` - 13 edges
4. `LLMProvider` - 12 edges
5. `Le Quoc Anh Tran` - 12 edges
6. `Settings` - 11 edges
7. `build_system_prompt()` - 11 edges
8. `reindex_all()` - 11 edges
9. `reindex_source()` - 11 edges
10. `create_conversation()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `RAG + Vector DB (Phase v2 planned)` --semantically_similar_to--> `AI Microservice (NestJS + LangChain + RAG)`  [INFERRED] [semantically similar]
  README.md → data/resume.md
- `LLM Abstraction (swappable providers)` --semantically_similar_to--> `LangChain`  [INFERRED] [semantically similar]
  README.md → data/resume.md
- `Resume Backend` --references--> `Le Quoc Anh Tran`  [INFERRED]
  README.md → data/resume.md
- `graphify` --references--> `Resume Backend`  [INFERRED]
  AGENTS.md → README.md
- `AI Microservice (NestJS + LangChain + RAG)` --semantically_similar_to--> `AI Microservice (NestJS + LangChain + RAG)`  [INFERRED] [semantically similar]
  data/resume.md → data/extra-context.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Backend Architecture Layers** — readme_middleware_layer, readme_guard_layer, readme_router_layer, readme_core_layer [EXTRACTED 1.00]

## Communities (21 total, 6 thin omitted)

### Community 0 - "Config & LLM Provider Abstraction"
Cohesion: 0.09
Nodes (21): ABC, AsyncOpenAI, BaseSettings, Settings, LLMProvider, ChatCompletionMessageParam, Send a chat request and return the response text., Stream a chat response token by token.          Yields content deltas as they ar (+13 more)

### Community 1 - "Conversation Store & Models"
Cohesion: 0.09
Nodes (38): do_run_migrations(), Alembic environment configuration for async SQLAlchemy.  Reads the database URL, Run migrations in 'offline' mode (emit SQL to a script)., Run migrations in 'online' mode using an async engine., run_migrations_offline(), run_migrations_online(), AsyncEngine, AsyncSession (+30 more)

### Community 2 - "Resume Content & Architecture Docs"
Cohesion: 0.06
Nodes (31): graphify, graphify explain command, graphify path command, graphify query command, GRAPH_REPORT.md, graphify update command, graphify-out/wiki/index.md, API Endpoints (+23 more)

### Community 3 - "Guard Layer (Safety & PII)"
Cohesion: 0.08
Nodes (41): BaseModel, create_conversation(), Create a new empty conversation and return its ID (UUID string)., _build_allowlist(), check_content_safety(), check_pii_leak(), check_prompt_injection(), Check user input for prompt injection attempts.     Returns (True, "") if the te (+33 more)

### Community 4 - "App Setup & Middleware"
Cohesion: 0.11
Nodes (19): BaseHTTPMiddleware, BoundLogger, get_bound_logger(), Get a logger with request context pre-bound.       Every log call from this logg, Configure structlog to output JSON to stdout.     To be called ONCE at app start, setup_logging(), api_key_auth(), bind_logger_middleware() (+11 more)

### Community 5 - "System Prompt Builder"
Cohesion: 0.14
Nodes (19): _build_safety_preamble(), build_system_prompt(), count_tokens_approx(), Prompt builder: assembles the system prompt for the LLM., Replace special Unicode characters with ASCII equivalents., Build the safety preamble using personal info from config/env vars., Assemble the full system prompt for the LLM.      The prompt always starts with, Count tokens using tiktoken's cl100k_base encoding.     cl100k_base is the encod (+11 more)

### Community 6 - "Candidate Profile & Tech Stack"
Cohesion: 0.05
Nodes (43): Additional context about Le Quoc Anh Tran — projects, hobbies, philosophy, AI Microservice (NestJS + LangChain + RAG), B2B SaaS VOD Platform, Background, Hobbies & Interests, Le Quoc Anh Tran (extra context profile), Options Trading Prototype (Alpaca API), PostgreSQL Migration Framework (+35 more)

### Community 7 - "Chat Endpoint Integration Tests"
Cohesion: 0.27
Nodes (9): AsyncClient, Empty message → 422 validation error., Prompt injection → blocked by guard., When no X-Conversation-ID header, server creates one., Full pipeline: guard → prompt → LLM → response with mock provider., test_chat_creates_conversation_id(), test_chat_endpoint_returns_answer(), test_chat_rejects_empty_message() (+1 more)

### Community 8 - "pipeline.py"
Cohesion: 0.12
Nodes (27): Any, Path, Document, chunk_qa_pairs(), chunk_text(), Text chunking for documents and Q&A pairs., Split text into overlapping chunks of CHUNK_SIZE_TOKENS tokens.      Returns a l, Convert Q&A pairs into one chunk each.      Each qa_data item should have 'quest (+19 more)

### Community 9 - "Health Endpoint Tests"
Cohesion: 0.50
Nodes (3): AsyncClient, GET /api/health returns ok status., test_health_endpoint()

### Community 10 - "LLM Chat Interface"
Cohesion: 0.11
Nodes (14): clear_db_if_configured(), client(), _db_available(), _FakeStore, mock_llm_provider(), _patch_store(), _Patcher, Patch the conversation store names imported by the route modules.      Patches c (+6 more)

## Knowledge Gaps
- **49 isolated node(s):** `resume-backend`, `Tech Stack`, `Getting Started`, `Testing`, `API Endpoints` (+44 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_llm_provider()` connect `Config & LLM Provider Abstraction` to `Guard Layer (Safety & PII)`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `build_system_prompt()` connect `System Prompt Builder` to `Guard Layer (Safety & PII)`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Resume Backend` (e.g. with `graphify` and `Le Quoc Anh Tran`) actually correct?**
  _`Resume Backend` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `LLMProvider` (e.g. with `OllamaProvider` and `OpenRouterProvider`) actually correct?**
  _`LLMProvider` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Le Quoc Anh Tran` (e.g. with `Work Philosophy` and `Le Quoc Anh Tran (extra context profile)`) actually correct?**
  _`Le Quoc Anh Tran` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `resume-backend`, `Tech Stack`, `Getting Started` to the rest of the system?**
  _49 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Config & LLM Provider Abstraction` be split into smaller, more focused modules?**
  _Cohesion score 0.0859465737514518 - nodes in this community are weakly interconnected._