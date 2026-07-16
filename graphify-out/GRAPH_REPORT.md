# Graph Report - resume-backend  (2026-07-16)

## Corpus Check
- 28 files · ~5,697 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 234 nodes · 339 edges · 20 communities (14 shown, 6 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 17 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `18f25ebe`
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
- Test Fixtures (conftest)
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
3. `Le Quoc Anh Tran` - 12 edges
4. `Settings` - 11 edges
5. `LLMProvider` - 11 edges
6. `build_system_prompt()` - 11 edges
7. `check_prompt_injection()` - 9 edges
8. `OllamaProvider` - 9 edges
9. `OpenRouterProvider` - 9 edges
10. `check_pii_leak()` - 8 edges

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
- **RAG Pipeline Participants** — readme_rag, readme_phase_v2, data_resume_ai_microservice, data_resume_langchain, data_resume_pgvector [INFERRED 0.85]
- **Backend Architecture Layers** — readme_middleware_layer, readme_guard_layer, readme_router_layer, readme_core_layer [EXTRACTED 1.00]
- **Conversation Management Flow** — readme_conversation_store, readme_api_conversations, readme_api_chat, readme_conversation_logger [INFERRED 0.85]

## Communities (20 total, 6 thin omitted)

### Community 0 - "Config & LLM Provider Abstraction"
Cohesion: 0.10
Nodes (18): ABC, BaseSettings, Settings, LLMProvider, ChatCompletionMessageParam, Send a chat request and return the response text., Return the model identifier (e.g. 'llama3.2', 'deepseek-chat')., Every LLM provider must implement this. (+10 more)

### Community 1 - "Conversation Store & Models"
Cohesion: 0.12
Nodes (26): BaseModel, append_message(), append_messages(), clear(), create_conversation(), get_history(), ChatCompletionMessageParam, In-memory conversation store.  Phase 1: Stores conversations in a dict (in-memor (+18 more)

### Community 2 - "Resume Content & Architecture Docs"
Cohesion: 0.07
Nodes (26): graphify, graphify explain command, graphify path command, graphify query command, GRAPH_REPORT.md, graphify update command, graphify-out/wiki/index.md, API Endpoints (+18 more)

### Community 3 - "Guard Layer (Safety & PII)"
Cohesion: 0.12
Nodes (22): _build_allowlist(), check_content_safety(), check_pii_leak(), check_prompt_injection(), Check user input for prompt injection attempts.     Returns (True, "") if the te, Check if the question is on-topic for a resume chatbot.     Returns (True, "") i, Parse comma-separated allowed emails/phones from settings., Redact potential PII from LLM output before sending to frontend.     Returns the (+14 more)

### Community 4 - "App Setup & Middleware"
Cohesion: 0.11
Nodes (19): BaseHTTPMiddleware, BoundLogger, get_bound_logger(), Get a logger with request context pre-bound.       Every log call from this logg, Configure structlog to output JSON to stdout.     To be called ONCE at app start, setup_logging(), api_key_auth(), bind_logger_middleware() (+11 more)

### Community 5 - "System Prompt Builder"
Cohesion: 0.14
Nodes (19): _build_safety_preamble(), build_system_prompt(), count_tokens_approx(), Prompt builder: reads data files (resume.md, mock-qa.json, extra-context.md) and, Count tokens using tiktoken's cl100k_base encoding.     cl100k_base is the encod, Replace special Unicode characters with ASCII equivalents., Build the safety preamble using personal info from config/env vars., Read data files and assemble the full system prompt for the LLM.     Returns a s (+11 more)

### Community 6 - "Candidate Profile & Tech Stack"
Cohesion: 0.10
Nodes (25): Additional context about Le Quoc Anh Tran — projects, hobbies, philosophy, AI Microservice (NestJS + LangChain + RAG), B2B SaaS VOD Platform, Background, Hobbies & Interests, Options Trading Prototype (Alpaca API), PostgreSQL Migration Framework, Projects (+17 more)

### Community 7 - "Chat Endpoint Integration Tests"
Cohesion: 0.27
Nodes (9): AsyncClient, Empty message → 422 validation error., Prompt injection → blocked by guard., When no X-Conversation-ID header, server creates one., Full pipeline: guard → prompt → LLM → response with mock provider., test_chat_creates_conversation_id(), test_chat_endpoint_returns_answer(), test_chat_rejects_empty_message() (+1 more)

### Community 8 - "Test Fixtures (conftest)"
Cohesion: 0.40
Nodes (4): client(), mock_llm_provider(), A fake LLM provider that returns canned responses., An async HTTP client that talks to the app directly (no network).      Auth is d

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

- **Why does `get_llm_provider()` connect `Config & LLM Provider Abstraction` to `Conversation Store & Models`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `Resume Backend` connect `Resume Content & Architecture Docs` to `LLM Chat Interface`, `Candidate Profile & Tech Stack`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `Le Quoc Anh Tran` connect `LLM Chat Interface` to `Resume Content & Architecture Docs`, `Candidate Profile & Tech Stack`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Resume Backend` (e.g. with `graphify` and `Le Quoc Anh Tran`) actually correct?**
  _`Resume Backend` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Le Quoc Anh Tran` (e.g. with `Work Philosophy` and `Le Quoc Anh Tran (extra context profile)`) actually correct?**
  _`Le Quoc Anh Tran` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Settings` (e.g. with `OllamaProvider` and `OpenRouterProvider`) actually correct?**
  _`Settings` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `LLMProvider` (e.g. with `OllamaProvider` and `OpenRouterProvider`) actually correct?**
  _`LLMProvider` has 2 INFERRED edges - model-reasoned connections that need verification._