# Technical Specification
## AI Implementation Copilot

**Version:** 1.0  
**Date:** 2026-06-02  
**Status:** Approved for MVP

---

## 1. System Overview

The AI Implementation Copilot is a Python-based web service with three layers:

1. **API Layer** — FastAPI application exposing REST endpoints.
2. **Service Layer** — `BlueprintGenerator` orchestrates the LLM call and parses the response into a validated Pydantic model.
3. **LLM Provider Layer** — Swappable providers behind an abstract interface (`MockLLMProvider` or `AnthropicLLMProvider`).

The Streamlit UI calls the FastAPI backend over HTTP, keeping the UI and business logic fully decoupled.

### Data Flow

```
User (Streamlit UI)
    │  POST /api/v1/blueprint  {problem_description, context}
    ▼
FastAPI Route (blueprint.py)
    │  calls
    ▼
BlueprintGenerator.generate(request: BlueprintRequest)
    │  builds prompt via prompt_templates.py
    │  calls
    ▼
LLMProvider.complete(prompt: str) → raw JSON string
    │
    ▼
Pydantic model_validate(json.loads(raw)) → BlueprintOutput
    │
    ▼
FastAPI returns 200 JSON response
    │
    ▼
Streamlit renders blueprint sections
```

---

## 2. Data Models

All models live in `app/models/schemas.py`.

### 2.1 Request Models

```python
class BlueprintRequest(BaseModel):
    problem_description: str  # 100–5000 chars
    context: Optional[str] = None  # optional domain context, max 2000 chars

    @field_validator("problem_description")
    def validate_length(cls, v):
        if len(v.strip()) < 100:
            raise ValueError("problem_description must be at least 100 characters")
        if len(v) > 5000:
            raise ValueError("problem_description must not exceed 5000 characters")
        return v.strip()
```

### 2.2 Output Sub-models

```python
class ProblemTypEnum(str, Enum):
    RAG = "RAG"
    AGENTIC = "AGENTIC"
    AUTOMATION = "AUTOMATION"
    FORECASTING = "FORECASTING"
    OCR = "OCR"
    API_INTEGRATION = "API_INTEGRATION"
    HYBRID = "HYBRID"

class AIOpportunity(BaseModel):
    title: str
    description: str
    impact: str  # HIGH / MEDIUM / LOW
    feasibility: str  # HIGH / MEDIUM / LOW

class AgenticStep(BaseModel):
    step_number: int
    agent_name: str
    action: str
    input: str
    output: str
    tools_used: List[str]

class BacklogTicket(BaseModel):
    id: str  # e.g. "TICKET-001"
    title: str
    description: str
    priority: str  # P0 / P1 / P2 / P3
    effort: str  # XS / S / M / L / XL
    phase: str  # Foundation / Core / Polish / Future

class RiskItem(BaseModel):
    id: str  # e.g. "RISK-001"
    category: str  # Technical / Data / Organizational / Timeline
    description: str
    likelihood: str  # HIGH / MEDIUM / LOW
    impact: str  # HIGH / MEDIUM / LOW
    mitigation: str

class TestCase(BaseModel):
    id: str
    type: str  # Unit / Integration / E2E / Manual
    description: str
    expected_outcome: str

class DataRequirement(BaseModel):
    source: str
    description: str
    availability: str  # HIGH / MEDIUM / LOW
    notes: str

class IntegrationPoint(BaseModel):
    system: str
    integration_type: str  # API / File / Database / Webhook / Manual
    description: str
    complexity: str  # HIGH / MEDIUM / LOW

class Milestone(BaseModel):
    week: int
    title: str
    deliverables: List[str]
    owner: str

class TeamRole(BaseModel):
    role: str
    count: int
    seniority: str  # Junior / Mid / Senior / Lead
    allocation: str  # e.g. "Full-time", "50%"
    responsibilities: str
    reports_to: str  # manager's role name; top role reports to "AI Division Director"

class FulfillmentAction(BaseModel):
    week: int  # aligned with delivery_status_report weeks
    role: str
    action: str  # HIRE / INTERNAL_ALLOCATION / CONTRACTOR
    notes: str

class DeliveryTeam(BaseModel):
    roles: List[TeamRole]
    fulfillment_plan: List[FulfillmentAction]
```

### 2.3 Primary Output Model

```python
class BlueprintOutput(BaseModel):
    # Section 1
    business_problem_summary: str

    # Section 2
    operational_pain_points: list[str]

    # Section 3
    ai_opportunity_classification: List[AIOpportunity]

    # Section 4
    recommended_solution_type: SolutionType

    # Section 5
    suggested_architecture: str

    # Section 6
    agentic_workflow: List[AgenticStep]

    # Section 7
    data_requirements: List[DataRequirement]

    # Section 8
    integration_points: List[IntegrationPoint]

    # Section 9
    engineering_backlog: List[BacklogItem]

    # Section 10
    risks_and_assumptions: List[RiskItem]

    # Section 11
    testing_plan: List[TestCase]

    # Section 12
    executive_summary: str

    # Section 13
    delivery_status_report: List[Milestone]

    # Section 14
    delivery_team: DeliveryTeam

    # Metadata
    generated_at: datetime
    provider_used: str  # "mock" | "anthropic" | "openai"
    model_id: Optional[str] = None
```

### 2.4 API Response Envelope

```python
class BlueprintResponse(BaseModel):
    success: bool
    data: Optional[BlueprintOutput] = None
    error: Optional[ErrorDetail] = None

class ErrorDetail(BaseModel):
    code: str
    message: str
    raw_llm_output: Optional[str] = None  # populated on parse failure
```

---

## 3. LLM Provider Interface

Lives in `app/services/llm/base.py`.

```python
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Send prompts to the LLM and return the raw string response."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier."""
        ...
```

### 3.1 MockLLMProvider (`app/services/llm/mock.py`)

- Returns a hard-coded, schema-valid JSON string.
- Response is deterministic — does not vary by input.
- Used by default in all tests and when `LLM_PROVIDER=mock`.
- Simulates network latency via configurable `delay_ms` (default: 0).

### 3.2 AnthropicLLMProvider (`app/services/llm/anthropic.py`)

- Calls `anthropic.AsyncAnthropic` client.
- Uses `messages.create()` with JSON mode enforcement via system prompt instruction.
- Supports prompt caching: system prompt is marked with `cache_control: {"type": "ephemeral"}`.
- Model configured via `MODEL_ID` env var (default: `claude-sonnet-4-6`).
- Raises `LLMProviderError` on API errors; caller handles gracefully.

---

## 4. Configuration

Lives in `app/core/config.py` using `pydantic-settings`.

```python
class Settings(BaseSettings):
    # LLM
    LLM_PROVIDER: str = "mock"          # "mock" | "anthropic"
    ANTHROPIC_API_KEY: str = ""
    MODEL_ID: str = "claude-sonnet-4-6"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = False

    # UI
    UI_API_BASE_URL: str = "http://localhost:8000"

    model_config = SettingsConfig(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
```

---

## 5. Prompt Design

Lives in `app/core/prompt_templates.py`.

### System Prompt (cached)
Frames the LLM as a senior AI implementation architect and technical delivery lead. Instructs it to:
- Return only valid JSON matching the `BlueprintOutput` schema (13 LLM-produced sections).
- Never include prose outside the JSON.
- Ground analysis in the specific problem — never generic AI advice.
- Quantify outcomes (time saved, error rate, ROI) wherever possible.
- Apply per-section depth guidance: root-cause diagnosis, specific pain points, measurable test criteria,
  concrete mitigations, and board-level executive language with zero technical jargon.

### User Prompt
Injects the user's `problem_description` and optional `context` field. Includes the full JSON schema as a reminder to enforce correct structure.

---

## 6. Error Handling Strategy

| Scenario | Behavior |
|---|---|
| Input validation failure | HTTP 422 with Pydantic error details |
| LLM API error (timeout, rate limit) | HTTP 503 with `code: LLM_UNAVAILABLE` |
| LLM returns invalid JSON | HTTP 502 with `code: PARSE_ERROR` + `raw_llm_output` |
| Unexpected server error | HTTP 500 with `code: INTERNAL_ERROR` |
| Missing API key when using real provider | HTTP 500 with `code: CONFIGURATION_ERROR` at startup |

---

## 7. Non-Functional Requirements

| Requirement | Target |
|---|---|
| Mock provider latency | < 100ms end-to-end |
| Real provider latency | < 30s (Anthropic API) |
| Test suite runtime | < 60s (all unit + integration) |
| Python version | 3.11+ |
| No persistent state | Blueprints are not stored anywhere |
| No authentication | MVP only — noted as future work |
