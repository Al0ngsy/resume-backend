# Graph Report - resume-backend  (2026-07-16)

## Corpus Check
- 28 files · ~6,386 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 242 nodes · 353 edges · 19 communities (13 shown, 6 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 17 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c8e7eefb`
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
2. `chat()` - 13 edges
3. `LLMProvider` - 12 edges
4. `Le Quoc Anh Tran` - 12 edges
5. `Settings` - 11 edges
6. `build_system_prompt()` - 11 edges
7. `OllamaProvider` - 10 edges
8. `OpenRouterProvider` - 10 edges
9. `check_prompt_injection()` - 9 edges
10. `check_pii_leak()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `RAG + Vector DB (Phase v2 planned)` --semantically_similar_to--> `AI Microservice (NestJS + LangChain + RAG)`  [INFERRED] [semantically similar]
  README.md → data/resume.md
- `LLM Abstraction (swappable providers)` --semantically_similar_to--> `LangChain`  [INFERRED] [semantically similar]
  README.md → data/resume.md
- `Resume Backend` --references--> `Le Quoc Anh Tran`  [INFERRED]
  README.md → data/resume.md
- `test_off_topic_blocked()` --calls--> `check_content_safety()`  [EXTRACTED]
  tests/test_guard.py → src/guard.py
- `graphify` --references--> `Resume Backend`  [INFERRED]
  AGENTS.md → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Backend Architecture Layers** — readme_middleware_layer, readme_guard_layer, readme_router_layer, readme_core_layer [EXTRACTED 1.00]
- **Conversation Management Flow** — readme_conversation_store, readme_api_conversations, readme_api_chat, readme_conversation_logger [INFERRED 0.85]

## Communities (19 total, 6 thin omitted)

### Community 0 - "Config & LLM Provider Abstraction"
Cohesion: 0.09
Nodes (19): ABC, BaseSettings, Settings, LLMProvider, ChatCompletionMessageParam, Send a chat request and return the response text., Stream a chat response token by token.          Yields content deltas as they ar, Return the model identifier (e.g. 'llama3.2', 'deepseek-chat'). (+11 more)

### Community 1 - "Conversation Store & Models"
Cohesion: 0.16
Nodes (15): append_message(), clear(), create_conversation(), get_history(), ChatCompletionMessageParam, In-memory conversation store.  Phase 1: Stores conversations in a dict (in-memor, Create a new empty conversation and return its ID., Retrieve the full message history for a conversation.     Returns an empty list (+7 more)

### Community 2 - "Resume Content & Architecture Docs"
Cohesion: 0.07
Nodes (26): graphify, graphify explain command, graphify path command, graphify query command, GRAPH_REPORT.md, graphify update command, graphify-out/wiki/index.md, API Endpoints (+18 more)

### Community 3 - "Guard Layer (Safety & PII)"
Cohesion: 0.13
Nodes (20): _build_allowlist(), check_pii_leak(), check_prompt_injection(), Check user input for prompt injection attempts.     Returns (True, "") if the te, Parse comma-separated allowed emails/phones from settings., Redact potential PII from LLM output before sending to frontend.     Returns the, ignore your instructions' → blocked, What are his skills?' → passes (+12 more)

### Community 4 - "App Setup & Middleware"
Cohesion: 0.09
Nodes (23): BaseHTTPMiddleware, BoundLogger, get_bound_logger(), Get a logger with request context pre-bound.       Every log call from this logg, Configure structlog to output JSON to stdout.     To be called ONCE at app start, setup_logging(), api_key_auth(), bind_logger_middleware() (+15 more)

### Community 5 - "System Prompt Builder"
Cohesion: 0.08
Nodes (36): BaseModel, append_messages(), Append multiple messages to a conversation's history atomically.     Creates the, check_content_safety(), Check if the question is on-topic for a resume chatbot.     Returns (True, "") i, ChatRequest, ChatResponse, ConversationCreateResponse (+28 more)

### Community 6 - "Candidate Profile & Tech Stack"
Cohesion: 0.10
Nodes (25): Additional context about Le Quoc Anh Tran — projects, hobbies, philosophy, AI Microservice (NestJS + LangChain + RAG), B2B SaaS VOD Platform, Background, Hobbies & Interests, Options Trading Prototype (Alpaca API), PostgreSQL Migration Framework, Projects (+17 more)

### Community 7 - "Chat Endpoint Integration Tests"
Cohesion: 0.27
Nodes (9): AsyncClient, Empty message → 422 validation error., Prompt injection → blocked by guard., When no X-Conversation-ID header, server creates one., Full pipeline: guard → prompt → LLM → response with mock provider., test_chat_creates_conversation_id(), test_chat_endpoint_returns_answer(), test_chat_rejects_empty_message() (+1 more)

### Community 9 - "Health Endpoint Tests"
Cohesion: 0.50
Nodes (3): AsyncClient, GET /api/health returns ok status., test_health_endpoint()

### Community 10 - "LLM Chat Interface"
Cohesion: 0.11
Nodes (18): Le Quoc Anh Tran (extra context profile), B.Sc. Medieninformatik — TU Berlin, Education, Interests & Hobbies, Languages, Le Quoc Anh Tran, M.Sc. Media Informatics — TU Berlin, Professional Summary (+10 more)

## Knowledge Gaps
- **43 isolated node(s):** `resume-backend`, `Tech Stack`, `Getting Started`, `Testing`, `API Endpoints` (+38 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_llm_provider()` connect `Config & LLM Provider Abstraction` to `System Prompt Builder`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `Resume Backend` connect `Resume Content & Architecture Docs` to `LLM Chat Interface`, `Candidate Profile & Tech Stack`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Resume Backend` (e.g. with `graphify` and `Le Quoc Anh Tran`) actually correct?**
  _`Resume Backend` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `LLMProvider` (e.g. with `OllamaProvider` and `OpenRouterProvider`) actually correct?**
  _`LLMProvider` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Le Quoc Anh Tran` (e.g. with `Work Philosophy` and `Le Quoc Anh Tran (extra context profile)`) actually correct?**
  _`Le Quoc Anh Tran` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Settings` (e.g. with `OllamaProvider` and `OpenRouterProvider`) actually correct?**
  _`Settings` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `resume-backend`, `Tech Stack`, `Getting Started` to the rest of the system?**
  _43 weakly-connected nodes found - possible documentation gaps or missing edges._