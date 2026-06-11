# Test Plan
## AI Implementation Copilot

**Version:** 1.0  
**Date:** 2026-06-02

---

## 1. Testing Philosophy

**Mock-first, deterministic by default.**

All automated tests run against `MockLLMProvider`. No test ever calls the Anthropic API. This ensures:
- Tests are fast (< 60s total suite)
- Tests are free (no API tokens consumed)
- Tests are stable (no flakiness from network or model behavior)
- CI works without secrets

Real LLM behavior is validated manually during demo prep using the canonical test problems defined in Section 6.

---

## 2. Test Pyramid

```
         ┌─────────────────┐
         │   Manual E2E    │  ~10% — demo walkthrough with real LLM
         │  (Demo Day QA)  │
         ├─────────────────┤
         │   Integration   │  ~20% — FastAPI routes via TestClient
         │     Tests       │
         ├─────────────────┤
         │   Unit Tests    │  ~70% — schemas, prompts, generator, providers
         └─────────────────┘
```

---

## 3. Unit Tests

**Location:** `tests/test_schemas.py`, `tests/test_blueprint_generator.py`

**Run command:** `pytest tests/ -v -k "unit"`

### 3.1 Schema Validation (`tests/test_schemas.py`)

| Test ID | Test Name | Input | Expected |
|---|---|---|---|
| UT-01 | Valid minimum request | 100-char description | No validation error |
| UT-02 | Valid maximum request | 5000-char description + context | No validation error |
| UT-03 | Description too short | 50-char description | `ValueError`: too short |
| UT-04 | Description too long | 5001-char description | `ValueError`: too long |
| UT-05 | Missing required field | No `problem_description` | `ValidationError` |
| UT-06 | Context is optional | No `context` field | Defaults to `None` |
| UT-07 | Description is stripped | Leading/trailing whitespace | Whitespace removed |
| UT-08 | Valid `ProblemTypeEnum` values | Each of 7 enum values | Accepted |
| UT-09 | Invalid enum value | `"UNKNOWN_TYPE"` | `ValidationError` |
| UT-10 | Valid `BlueprintOutput` | Full fixture dict | Model instantiation succeeds |
| UT-11 | Missing required section | Fixture without `executive_summary` | `ValidationError` |
| UT-12 | Backlog ticket priorities | `"P0"`, `"P1"`, `"P2"`, `"P3"` | All accepted |
| UT-13 | Effort values | `"XS"`, `"S"`, `"M"`, `"L"`, `"XL"` | All accepted |

### 3.2 Prompt Templates (`tests/test_blueprint_generator.py`)

| Test ID | Test Name | Assertion |
|---|---|---|
| UT-14 | System prompt is non-empty | `len(system_prompt) > 100` |
| UT-15 | User prompt contains problem description | `problem_description in user_prompt` |
| UT-16 | User prompt contains context when provided | `context in user_prompt` |
| UT-17 | User prompt omits context block when absent | No `None` or `"null"` in prompt |

### 3.3 MockLLMProvider (`tests/test_blueprint_generator.py`)

| Test ID | Test Name | Assertion |
|---|---|---|
| UT-18 | Mock returns valid JSON string | `json.loads(response)` succeeds |
| UT-19 | Mock response validates as BlueprintOutput | `BlueprintOutput.model_validate(...)` succeeds |
| UT-20 | Mock provider name | `provider.provider_name == "mock"` |
| UT-21 | Mock ignores prompt content | Same response regardless of input |

### 3.4 BlueprintGenerator (`tests/test_blueprint_generator.py`)

| Test ID | Test Name | Assertion |
|---|---|---|
| UT-22 | Generator returns BlueprintOutput | `isinstance(result, BlueprintOutput)` |
| UT-23 | Generator injects timestamp | `result.generated_at` is set and recent |
| UT-24 | Generator injects provider name | `result.provider_used == "mock"` |
| UT-25 | All 10 sections populated | None of the required fields are empty |
| UT-26 | Parse error propagates correctly | Malformed JSON → `BlueprintParseError` raised |

---

## 4. Integration Tests

**Location:** `tests/test_api.py`

**Run command:** `pytest tests/ -v -k "integration"`

Uses FastAPI `TestClient` — no real HTTP server required.

| Test ID | Endpoint | Scenario | Expected Status | Expected Body |
|---|---|---|---|---|
| IT-01 | `GET /api/v1/health` | Server running | 200 | `{"status": "ok"}` |
| IT-02 | `GET /api/v1/providers` | Server running | 200 | `{"active": "mock", ...}` |
| IT-03 | `POST /api/v1/blueprint` | Valid request, mock provider | 200 | `success: true`, all 10 sections |
| IT-04 | `POST /api/v1/blueprint` | Description too short | 422 | `VALIDATION_ERROR` |
| IT-05 | `POST /api/v1/blueprint` | Description missing | 422 | Pydantic error detail |
| IT-06 | `POST /api/v1/blueprint` | With optional context | 200 | Blueprint generated |
| IT-07 | `POST /api/v1/blueprint` | Maximum length input | 200 | Blueprint generated |
| IT-08 | `POST /api/v1/blueprint` | Mock parse failure injected | 502 | `PARSE_ERROR` + `raw_llm_output` |
| IT-09 | `POST /api/v1/blueprint` | Mock LLM error injected | 503 | `LLM_UNAVAILABLE` |
| IT-10 | Unknown path | `GET /api/v1/unknown` | 404 | FastAPI default 404 |

---

## 5. CI Test Configuration

**GitHub Actions trigger:** On every push to any branch and every pull request to `main`.

**Command:**
```bash
pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80
```

**Coverage target:** ≥ 80% line coverage across `app/`.

**Linting:**
```bash
ruff check app/ tests/
```

**Type checking:**
```bash
mypy app/ --ignore-missing-imports
```

All three must pass for CI to be green.

---

## 6. Canonical Test Problems

These three inputs are used for manual demo validation and as fixtures in integration tests.

### Problem A — Logistics / OCR (Expected: `OCR` or `HYBRID`)
```
Our logistics company processes 3000 invoices per month manually. Each invoice requires 
a clerk to open a PDF, read line items, match them against purchase orders in our ERP, 
and flag discrepancies. This takes 2 full-time employees and has a 4% error rate causing 
payment delays and vendor complaints. We have tried basic OCR tools but they fail on 
scanned documents with variable layouts. We need an automated solution that can handle 
mixed PDF formats and integrate with SAP S/4HANA.
```

### Problem B — HR / RAG (Expected: `RAG` or `AGENTIC`)
```
Our HR department receives 200+ employee questions per week via email about policies, 
benefits, and leave procedures. HR business partners spend 60% of their time answering 
repetitive questions that are already documented in our 500-page employee handbook. 
New hires especially struggle to find information. We want employees to get instant, 
accurate answers without HR intervention, and we want HR BPs to focus on strategic work. 
Our handbook is updated quarterly and lives in SharePoint.
```

### Problem C — Finance / Forecasting (Expected: `FORECASTING` or `HYBRID`)
```
Our FP&A team produces monthly cash flow forecasts manually using Excel. The process 
takes 3 analysts 5 days each month, uses data from 6 different source systems, and 
produces forecasts that are consistently 15-20% off actuals. The CFO has requested 
weekly forecasts but the team cannot increase cadence with the current process. We have 
3 years of historical transaction data and budget data, plus external signals like 
payment terms per customer and supplier.
```

---

## 7. Manual QA Checklist (Demo Day)

Run this checklist the day before the demo using the real Anthropic provider.

- [ ] Server starts without errors: `uvicorn app.main:app`
- [ ] Streamlit UI loads at `http://localhost:8501`
- [ ] Paste Problem A → blueprint generates in < 30s
- [ ] All 10 sections are populated (no empty strings)
- [ ] Problem type recommendation is `OCR` or `HYBRID`
- [ ] Executive summary is readable by a non-technical audience
- [ ] Technical backlog has at least 5 tickets
- [ ] Paste Problem B → blueprint generates successfully
- [ ] Paste Problem C → blueprint generates successfully
- [ ] UI handles the case where the server is stopped gracefully (error message shown)
- [ ] `/docs` Swagger UI is accessible and accurate
- [ ] Docker Compose starts both services: `docker compose up`
- [ ] Blueprint generates correctly via Docker deployment

---

## 8. Test Data Location

| File | Purpose |
|---|---|
| `tests/conftest.py` | Shared fixtures: mock provider, test client, sample requests |
| `tests/fixtures/mock_blueprint.json` | The canonical mock LLM response fixture |
| `tests/fixtures/sample_problems.py` | The three canonical problem strings |
