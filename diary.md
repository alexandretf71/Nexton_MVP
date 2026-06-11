# Development Diary
## AI Implementation Copilot — Zaigo MVP

This diary tracks the major decisions, milestones, and pivots taken during the development of this MVP.
It is intended as a transparent record of the build process for the CTO demo.

---

## 02/Jun/2026

**~21:00 — First prompt: context and specifications received**
Received the full product brief for the AI Implementation Copilot. Scope defined as:
a one-week MVP for a CTO interview demonstrating AI Implementation Lead skills.
The tool must receive a messy business problem and return a structured 10-section AI blueprint.
Stack decided: FastAPI + Streamlit + pytest + Pydantic v2 + Anthropic Claude (mock-first).

**~21:15 — Architecture decisions locked**
Key decisions made before writing a single line of code:
- Single LLM call for the full blueprint (MVP simplicity over multi-agent quality)
- Strategy pattern for the LLM provider layer (MockLLMProvider by default, swappable to Anthropic)
- Pydantic as the validation boundary — LLM output never reaches the API response unvalidated
- No database, no auth, no persistence — demo-ready, not production-complete
- All tests must be deterministic and run without any API key or network access

**21:45 — Documentation phase complete (8 files)**
Created the full `docs/` folder before any application code:
`PRD.md`, `SPEC.md`, `ARCHITECTURE.md`, `API_SPEC.md`, `TEST_PLAN.md`,
`AI_ASSISTED_WORKFLOW.md`, `DEPLOYMENT_NOTES.md`, `DEMO_SCRIPT.md`.
Rationale: documentation-first forces architectural clarity and avoids mid-build pivots.

**21:52 — `CLAUDE.md` created at project root**
Wrote the AI coding guidelines file that governs all future Claude Code sessions on this project.
Covers: architecture principles, coding standards, testing rules, git workflow, prompting discipline,
environment variable handling, and a "What Not To Do" section.

**~22:00 — Zaigo brand assets integrated**
Zaigo company logo (`zaigo_logo.jfif`) received and placed at `ui/assets/`.
Brand color tokens defined: background `#1A1A1A`, primary red `#E8412E`, white `#FFFFFF`.
CLAUDE.md and DEMO_SCRIPT.md updated with logo path and fallback rules.
GitHub profile confirmed: `https://github.com/alexandretf71`

**22:37 — Backend skeleton implemented**
`app/models/schemas.py` — all Pydantic models for the 10-section blueprint output.
`app/core/config.py` — env-var settings with pydantic-settings.
`app/core/prompt_templates.py` — cached system prompt + parameterised user prompt builder.
`app/services/llm/base.py` — abstract `LLMProvider` interface.
`app/services/llm/mock.py` — deterministic mock reading from `tests/fixtures/mock_blueprint.json`.
`app/services/llm/anthropic.py` — real Anthropic provider with prompt caching.
`app/services/blueprint_generator.py` — orchestrates prompt → LLM → validated `BlueprintOutput`.

**22:38 — API routes wired**
`GET /health` and `POST /generate-blueprint` endpoints registered.
FastAPI lifespan event selects the correct LLM provider at startup via `LLM_PROVIDER` env var.
CORS configured for Streamlit origin (`localhost:8501`).

**22:47 — Tests written and passing: 34/34**
Three test files covering schemas, generator, and API integration.
Three canonical sample problems defined (logistics/OCR, HR/RAG, finance/forecasting).
One bug fixed during the run: `datetime` object not JSON-serialisable in error path of the generator.
All 34 tests pass in 1.03s with zero external calls.

**22:54 — Streamlit UI complete**
`ui/app.py` built with Zaigo dark-mode branding, sidebar logo, problem input form,
and 10 tabbed sections rendering the full blueprint output.
Graceful error handling for missing logo file and API connectivity issues.

**22:56 — First commit pushed to GitHub**
Repository: `https://github.com/alexandretf71/Zaigo-MVP---AI-Implementation-Copilot`
Branch: `main`
47 files — 3411 insertions.
Commit: `965332c` — "Initial commit: AI Implementation Copilot MVP skeleton"
GitHub Actions CI triggered automatically on push.

---

## 03/Jun/2026

**~00:00 — `.gitattributes` added**
Added to normalize line endings (LF) across platforms and mark binary assets correctly.
Ensures consistent behaviour for contributors on Linux, macOS, and Windows.

---

**~00:30 — UI-based LLM key management added**
Requirement: the demo must support a paid Anthropic key without ever committing it to GitHub.

Design chosen: API key travels as an HTTP header (`X-API-Key`) — never in the request body,
never stored server-side, never logged, never in version control.

Changes made:
- `AnthropicLLMProvider.__init__` now accepts an optional `api_key` parameter that overrides
  the environment variable for that instantiation only.
- `POST /generate-blueprint` reads optional `X-LLM-Provider` and `X-API-Key` request headers.
  If `X-LLM-Provider: anthropic` is set without a key, the endpoint returns 400 immediately.
- Streamlit sidebar gains a "LLM Settings" section: provider dropdown + password-type API key
  field. Values live only in `st.session_state` (browser memory; gone on page refresh).
- New test `test_anthropic_provider_without_key_returns_400` covers the validation path.
- Test count: 35/35 passing in 1.29s.

The `.env` file route still works unchanged for Docker and headless deployments.

---

**~01:00 — v1.2 committed and pushed to GitHub**
Commit: `aa30483` — "v1.2: OpenAI provider, UI reskin, hero video card, key management"
18 files changed — 1333 insertions, 46 deletions.

What shipped in v1.2:
- OpenAI provider (`gpt-4o`) alongside Anthropic — both selectable from the UI sidebar
- Per-request API key override via HTTP headers; keys are ephemeral (browser session only)
- Real provider error messages surfaced (no more blank 500s)
- Full UI reskin matching zaigo.ai: cream `#F4F1EC` background, Inter 900, red pill buttons
- Zaigo-style hero video card: eagle MP4 (`Sovi_flying.mp4`), B&W filter, red-highlight headline
- Configurable Streamlit port via `UI_ORIGIN` env var
- Test count: 36/36 passing

---

---

## 04/Jun/2026

**Blueprint depth enhancement — v1.3**

Identified that the 10-section blueprint was producing superficial output. Redesigned the
entire LLM contract to produce a richer, 13-section blueprint via a specialized prompt.

**Schema additions (`app/models/schemas.py`):**
- `operational_pain_points: list[str]` — observable, countable symptom strings enumerated by the LLM
- `data_requirements: list[DataRequirement]` — new sub-model: source, description,
  availability (HIGH/MEDIUM/LOW), notes
- `integration_points: list[IntegrationPoint]` — new sub-model: system, integration_type
  (API/File/Database/Webhook/Manual), description, complexity (HIGH/MEDIUM/LOW)

**Prompt rewrite (`app/core/prompt_templates.py`):**
- Role upgraded from "senior AI solutions architect" to "senior AI implementation architect
  and technical delivery lead"
- Added per-section depth guidance covering all 13 output fields
- LLM instructed to quantify outcomes (time saved, error rate, ROI) wherever possible
- Executive summary now required to contain zero jargon and a concrete ROI signal
- Engineering backlog must cover infra, AI/ML, integrations, UI, and observability
- Risk mitigations must name a specific action with owner/timing — no platitudes
- Test cases must have measurable acceptance criteria (no vague pass/fail)

**Tests (`tests/test_schemas.py`, `tests/test_blueprint_generator.py`):**
- New `TestPromptTemplate` class — 4 tests:
  - prompt file exists on disk
  - SYSTEM_PROMPT is non-empty
  - SYSTEM_PROMPT instructs JSON-only output
  - SYSTEM_PROMPT references all 13 required output field names (catches silent schema drift)
- `test_all_sections_populated` extended with assertions for 3 new fields
- Test count: 40/40 passing · coverage 78%

**UI (`ui/app.py`):**
- 3 new tabs: 💢 Pain Points, 🗄 Data Requirements, 🔌 Integration Points
- Hero subtitle updated from "10-section" to "13-section"

**Docs:** `docs/SPEC.md` updated with new sub-models and revised `BlueprintOutput` field list.

---

*Next session: run a live demo with the 3 sample problems against the real Anthropic/OpenAI
providers, and verify the full blueprint quality end-to-end before the CTO presentation.*
