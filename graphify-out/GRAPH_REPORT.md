# Graph Report - resume-backend  (2026-08-07)

## Corpus Check
- 34 files · ~8,736 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 269 nodes · 433 edges · 22 communities (16 shown, 6 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 11 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ff235e12`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Config & LLM Provider Abstraction
- Conversation Store & Models
- Resume Content & Architecture Docs
- Guard Layer (Safety & PII)
- App Setup & Middleware
- build_system_prompt
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
1. `Resume Backend` - 20 edges
2. `chat()` - 14 edges
3. `_ensure_engine()` - 12 edges
4. `reindex_source()` - 12 edges
5. `build_system_prompt()` - 11 edges
6. `OpenAICompatProvider` - 10 edges
7. `create_conversation()` - 9 edges
8. `get_history()` - 9 edges
9. `check_prompt_injection()` - 9 edges
10. `getLogger()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `graphify` --references--> `Resume Backend`  [INFERRED]
  AGENTS.md → README.md
- `Document` --uses--> `Base`  [INFERRED]
  src/db/models.py → src/db/database.py
- `test_empty_input()` --calls--> `check_prompt_injection()`  [EXTRACTED]
  tests/test_guard.py → src/guard.py
- `test_injection_blocked()` --calls--> `check_prompt_injection()`  [EXTRACTED]
  tests/test_guard.py → src/guard.py
- `test_normal_question_passes()` --calls--> `check_prompt_injection()`  [EXTRACTED]
  tests/test_guard.py → src/guard.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Backend Architecture Layers** — readme_middleware_layer, readme_guard_layer, readme_router_layer, readme_core_layer [EXTRACTED 1.00]

## Communities (22 total, 6 thin omitted)

### Community 0 - "Config & LLM Provider Abstraction"
Cohesion: 0.17
Nodes (9): AsyncOpenAI, BaseSettings, Settings, get_llm_provider(), Build the OpenAI-compatible client for the configured provider., OpenAICompatProvider, Any, ChatCompletionMessageParam (+1 more)

### Community 1 - "Conversation Store & Models"
Cohesion: 0.09
Nodes (35): do_run_migrations(), Alembic environment configuration for async SQLAlchemy.  Reads the database URL, Run migrations in 'offline' mode (emit SQL to a script)., Run migrations in 'online' mode using an async engine., run_migrations_offline(), run_migrations_online(), AsyncEngine, Connection (+27 more)

### Community 2 - "Resume Content & Architecture Docs"
Cohesion: 0.06
Nodes (33): graphify, graphify explain command, graphify path command, graphify query command, GRAPH_REPORT.md, graphify update command, graphify-out/wiki/index.md, API Endpoints (+25 more)

### Community 3 - "Guard Layer (Safety & PII)"
Cohesion: 0.08
Nodes (40): BaseModel, _build_allowlist(), check_content_safety(), check_pii_leak(), check_prompt_injection(), Check user input for prompt injection attempts.     Returns (True, "") if the te, Check if the question is on-topic for a resume chatbot.     Returns (True, "") i, Parse comma-separated allowed emails/phones from settings. (+32 more)

### Community 4 - "App Setup & Middleware"
Cohesion: 0.14
Nodes (16): BoundLogger, FastAPI, One OpenAI-compatible LLM provider for ollama, openrouter, and opencode.  All th, get_bound_logger(), getLogger(), Get a structlog logger. Pass __name__ to get a module-scoped logger., Get a logger with request context pre-bound.       Every log call from this logg, Configure structlog to output JSON to stdout.     To be called ONCE at app start (+8 more)

### Community 5 - "build_system_prompt"
Cohesion: 0.14
Nodes (19): _build_safety_preamble(), build_system_prompt(), count_tokens_approx(), Prompt builder: assembles the system prompt for the LLM., Assemble the full system prompt for the LLM.      The prompt always starts with, Count tokens using tiktoken's cl100k_base encoding.     cl100k_base is the encod, Replace special Unicode characters with ASCII equivalents., Build the safety preamble using personal info from config/env vars. (+11 more)

### Community 6 - "Candidate Profile & Tech Stack"
Cohesion: 0.33
Nodes (6): Conversation Logger (structured JSON), Core Layer, LLM Abstraction (swappable providers), Ollama LLM Provider, OpenRouter LLM Provider, Prompt Builder (data/* to system prompt)

### Community 7 - "Chat Endpoint Integration Tests"
Cohesion: 0.27
Nodes (9): AsyncClient, Empty message → 422 validation error., Prompt injection → blocked by guard., When no X-Conversation-ID header, server creates one., Full pipeline: guard → prompt → LLM → response with mock provider., test_chat_creates_conversation_id(), test_chat_endpoint_returns_answer(), test_chat_rejects_empty_message() (+1 more)

### Community 8 - "pipeline.py"
Cohesion: 0.11
Nodes (27): Path, Document, chunk_qa_pairs(), chunk_text(), Any, Text chunking for documents and Q&A pairs., Split text into overlapping chunks of CHUNK_SIZE_TOKENS tokens.      Returns a l, Convert Q&A pairs into one chunk each.      Each qa_data item should have 'quest (+19 more)

### Community 9 - "Health Endpoint Tests"
Cohesion: 0.50
Nodes (3): AsyncClient, GET /api/health returns ok status., test_health_endpoint()

### Community 10 - "LLM Chat Interface"
Cohesion: 0.11
Nodes (14): clear_db_if_configured(), client(), _db_available(), _FakeStore, mock_llm_provider(), _patch_store(), _Patcher, Patch the conversation store names imported by the route modules.      Patches c (+6 more)

## Knowledge Gaps
- **37 isolated node(s):** `resume-backend`, `Tech Stack`, `Getting Started`, `Testing`, `API Endpoints` (+32 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_system_prompt()` connect `build_system_prompt` to `Guard Layer (Safety & PII)`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `OpenAICompatProvider` connect `Config & LLM Provider Abstraction` to `App Setup & Middleware`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `chat()` (e.g. with `check_content_safety()` and `check_prompt_injection()`) actually correct?**
  _`chat()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `resume-backend`, `Tech Stack`, `Getting Started` to the rest of the system?**
  _37 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Conversation Store & Models` be split into smaller, more focused modules?**
  _Cohesion score 0.09102564102564102 - nodes in this community are weakly interconnected._
- **Should `Resume Content & Architecture Docs` be split into smaller, more focused modules?**
  _Cohesion score 0.05714285714285714 - nodes in this community are weakly interconnected._
- **Should `Guard Layer (Safety & PII)` be split into smaller, more focused modules?**
  _Cohesion score 0.07505285412262157 - nodes in this community are weakly interconnected._