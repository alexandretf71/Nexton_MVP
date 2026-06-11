# System Architecture
## AI Implementation Copilot

**Version:** 1.0  
**Date:** 2026-06-02

---

## 1. C4 Context Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        System Context                           │
│                                                                 │
│   ┌──────────────┐          ┌─────────────────────────────┐    │
│   │     User      │ pastes  │   AI Implementation Copilot │    │
│   │ (CTO / Tech   │────────▶│   (This system)             │    │
│   │  PM / Arch)   │         │                             │    │
│   └──────────────┘         │   Receives messy business   │    │
│                             │   problem, returns structured│    │
│                             │   AI blueprint              │    │
│                             └──────────────┬──────────────┘    │
│                                            │                    │
│                                            │ API call (HTTPS)   │
│                                            ▼                    │
│                              ┌─────────────────────────┐       │
│                              │   LLM Provider           │       │
│                              │   (Anthropic Claude API  │       │
│                              │    or Mock in tests)     │       │
│                              └─────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. C4 Container Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          AI Implementation Copilot                       │
│                                                                          │
│   ┌─────────────────────┐    HTTP POST       ┌──────────────────────┐  │
│   │   Streamlit UI       │ /api/v1/blueprint  │   FastAPI Backend    │  │
│   │   (ui/app.py)        │───────────────────▶│   (app/main.py)      │  │
│   │                      │◀───────────────────│                      │  │
│   │   - Problem input    │  BlueprintOutput   │   - Route handlers   │  │
│   │   - Blueprint render │  (JSON)            │   - Input validation │  │
│   │   - Section tabs     │                    │   - Error handling   │  │
│   │                      │                    └──────────┬───────────┘  │
│   │   Port: 8501         │                               │              │
│   └─────────────────────┘                               │ calls        │
│                                                          ▼              │
│                                              ┌──────────────────────┐  │
│                                              │  BlueprintGenerator  │  │
│                                              │  (services/)         │  │
│                                              │                      │  │
│                                              │  - Build prompts     │  │
│                                              │  - Call LLM provider │  │
│                                              │  - Parse & validate  │  │
│                                              └──────────┬───────────┘  │
│                                                         │              │
│                                              ┌──────────▼───────────┐  │
│                                              │   LLM Provider Layer │  │
│                                              │   (services/llm/)    │  │
│                                              │                      │  │
│                                              │   LLMProvider (ABC)  │  │
│                                              │   ├── MockLLMProvider│  │
│                                              │   └── AnthropicLLM   │  │
│                                              └──────────┬───────────┘  │
│                                                         │              │
└─────────────────────────────────────────────────────────┼─────────────┘
                                                          │ HTTPS (real)
                                                          │ in-process (mock)
                                                          ▼
                                              ┌──────────────────────┐
                                              │  Anthropic Claude API│
                                              │  (external service)  │
                                              └──────────────────────┘
```

---

## 3. Component Descriptions

### 3.1 Streamlit UI (`ui/app.py`)
- Single-page interface with a problem input text area and a "Generate Blueprint" button.
- Makes a synchronous HTTP POST to the FastAPI backend.
- Renders the `BlueprintOutput` response across 10 labeled sections using `st.tabs()` and `st.expander()`.
- Displays provider metadata (provider name, model ID, generation time) in the sidebar.
- No state persistence — each generation is independent.

### 3.2 FastAPI Backend (`app/`)
- **`main.py`** — Creates the FastAPI app, registers routers, configures CORS (allows Streamlit origin), and sets up lifespan events (provider initialization).
- **`api/routes/blueprint.py`** — Defines `POST /api/v1/blueprint`, `GET /api/v1/health`, and `GET /api/v1/providers` endpoints.
- **`core/config.py`** — Pydantic Settings model; reads environment variables and `.env` file.
- **`core/prompt_templates.py`** — Builds system and user prompts. System prompt is a constant (for caching); user prompt is parameterized per request.
- **`models/schemas.py`** — All Pydantic request/response models including `BlueprintRequest`, `BlueprintOutput`, and all sub-models.

### 3.3 BlueprintGenerator (`app/services/blueprint_generator.py`)
- Receives a `BlueprintRequest` and the active `LLMProvider` instance.
- Calls `prompt_templates.build_system_prompt()` and `prompt_templates.build_user_prompt(request)`.
- Calls `provider.complete(system_prompt, user_prompt)` to get a raw JSON string.
- Parses and validates the response with `BlueprintOutput.model_validate(json.loads(raw))`.
- On parse failure: raises `BlueprintParseError` with the raw output attached.
- Injects `generated_at`, `provider_used`, and `model_id` into the output.

### 3.4 LLM Provider Layer (`app/services/llm/`)
- **`base.py`** — Abstract `LLMProvider` class with `complete()` and `provider_name` interface.
- **`mock.py`** — `MockLLMProvider`: returns a hardcoded, schema-valid JSON fixture. The fixture covers all 10 output sections with realistic-looking content about a fictional logistics company. A `delay_ms` parameter allows simulating latency in UI tests.
- **`anthropic.py`** — `AnthropicLLMProvider`: wraps `anthropic.AsyncAnthropic`. Sends the system prompt with `cache_control` for repeated-call efficiency. Parses the text content from the first message block.

---

## 4. LLM Provider Abstraction (Strategy Pattern)

The provider is selected at application startup based on the `LLM_PROVIDER` environment variable:

```
LLM_PROVIDER=mock      → MockLLMProvider()       (default)
LLM_PROVIDER=anthropic → AnthropicLLMProvider()  (requires ANTHROPIC_API_KEY)
```

The `BlueprintGenerator` depends only on the `LLMProvider` abstract interface. Swapping providers requires zero changes to business logic — only the startup configuration changes.

This enables:
- **Full test isolation** — tests always use `MockLLMProvider`, never call external APIs.
- **Easy demo mode** — switch with a single env var.
- **Future extensibility** — add `OpenAILLMProvider` without touching existing code.

---

## 5. Request Lifecycle

```
1.  User submits problem text in Streamlit UI
2.  Streamlit sends POST /api/v1/blueprint to FastAPI
3.  FastAPI validates BlueprintRequest (Pydantic, 422 on failure)
4.  Route calls BlueprintGenerator.generate(request, provider)
5.  Generator calls prompt_templates.build_system_prompt()
6.  Generator calls prompt_templates.build_user_prompt(request)
7.  Generator calls provider.complete(system_prompt, user_prompt)
    └── Mock: returns JSON fixture immediately
    └── Anthropic: sends API call, waits for response (< 30s)
8.  Generator parses raw JSON → BlueprintOutput (502 on parse failure)
9.  Generator injects metadata (timestamp, provider, model)
10. FastAPI returns 200 BlueprintResponse
11. Streamlit renders blueprint sections
```

---

## 6. Architecture Decision Records

### ADR-001: Single LLM Call for MVP
**Decision:** Use one LLM call to produce all 10 output sections.  
**Rationale:** Multi-step agentic pipelines (one call per section) would improve quality but increase latency, complexity, and cost for a one-week demo MVP.  
**Consequence:** Blueprint quality depends heavily on prompt design. Multi-call pipeline is the primary v2 enhancement.

### ADR-002: FastAPI + Streamlit Over a Unified Framework
**Decision:** Keep backend (FastAPI) and UI (Streamlit) as separate processes.  
**Rationale:** Separation allows the API to be consumed by tools other than the Streamlit UI (curl, Postman, future web frontend). It also keeps each layer testable independently.  
**Consequence:** Two processes to start for local development. Docker Compose resolves this.

### ADR-003: Pydantic for Output Validation
**Decision:** Parse every LLM response through a Pydantic model before returning it.  
**Rationale:** LLMs can return subtly malformed JSON or omit fields. Pydantic catches these at the boundary and returns a clean error rather than passing broken data to the UI.  
**Consequence:** Parse errors surface as 502 responses with the raw LLM output attached for debugging.

### ADR-004: No Database for MVP
**Decision:** Blueprints are generated on-demand and not persisted.  
**Rationale:** Persistence adds infrastructure complexity (migrations, connection pooling, backup). For a one-week MVP the demo value is identical without it.  
**Consequence:** Blueprints cannot be retrieved after the HTTP response is consumed. History is a v1.1 feature.

---

## 7. Future Extensibility

| Enhancement | Change Required |
|---|---|
| Multi-step agentic pipeline | Add new `AgenticBlueprintGenerator` implementing same interface |
| Vector DB for RAG blueprints | New `RAGEnrichmentService` injected into generator |
| Persistent blueprint storage | Add `BlueprintRepository` + SQLite/Postgres, inject into route |
| OpenAI provider | New `OpenAILLMProvider(LLMProvider)` in `services/llm/` |
| Streaming response | Swap `complete()` for `stream()` in interface, update route to use SSE |
| PDF export | Post-process `BlueprintOutput` with `reportlab` or `weasyprint` |
