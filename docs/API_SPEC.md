# API Specification
## AI Implementation Copilot

**Version:** 1.0  
**Base URL:** `http://localhost:8000`  
**API Prefix:** `/api/v1`  
**Date:** 2026-06-02

> Full interactive docs available at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc` (ReDoc) when the server is running.

---

## Endpoints Summary

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/providers` | List available LLM providers |
| `POST` | `/api/v1/blueprint` | Generate AI implementation blueprint |

---

## 1. Health Check

### `GET /api/v1/health`

Returns server status and active LLM provider.

**Response — 200 OK**
```json
{
  "status": "ok",
  "provider": "mock",
  "version": "1.0.0"
}
```

**Example**
```bash
curl http://localhost:8000/api/v1/health
```

---

## 2. List Providers

### `GET /api/v1/providers`

Returns the list of available LLM providers and which one is active.

**Response — 200 OK**
```json
{
  "active": "mock",
  "available": ["mock", "anthropic"]
}
```

**Example**
```bash
curl http://localhost:8000/api/v1/providers
```

---

## 3. Generate Blueprint

### `POST /api/v1/blueprint`

Receives a business problem description and returns a structured AI implementation blueprint.

**Request Headers**
```
Content-Type: application/json
```

**Request Body**
```json
{
  "problem_description": "string (100–5000 chars, required)",
  "context": "string (optional, max 2000 chars)"
}
```

**Field Descriptions**

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `problem_description` | string | Yes | 100–5000 chars | Free-form description of the business problem |
| `context` | string | No | max 2000 chars | Additional domain context (industry, tech stack, constraints) |

---

### Response — 200 OK (Success)

```json
{
  "success": true,
  "data": {
    "business_problem_diagnosis": "string — restated problem with root cause analysis",

    "ai_opportunity_classification": [
      {
        "title": "Automated Invoice Processing",
        "description": "Use OCR + LLM to extract fields from PDF invoices...",
        "impact": "HIGH",
        "feasibility": "HIGH"
      }
    ],

    "suggested_ai_architecture": "string — narrative description of the recommended system design",

    "problem_type_recommendation": "HYBRID",

    "agentic_workflow": [
      {
        "step_number": 1,
        "agent_name": "Document Ingestion Agent",
        "action": "Extract text from uploaded PDF invoices",
        "input": "Raw PDF files from S3 bucket",
        "output": "Structured text content per page",
        "tools_used": ["PyMuPDF", "AWS S3 SDK"]
      }
    ],

    "technical_backlog": [
      {
        "id": "TICKET-001",
        "title": "Set up FastAPI project scaffold",
        "description": "Initialize repository, install dependencies, configure CI",
        "priority": "P0",
        "effort": "S",
        "phase": "Foundation"
      }
    ],

    "risks_and_assumptions": [
      {
        "id": "RISK-001",
        "category": "Data",
        "description": "Invoice PDFs may have inconsistent formatting across vendors",
        "likelihood": "HIGH",
        "impact": "MEDIUM",
        "mitigation": "Build vendor-specific extraction templates; human-in-the-loop review for low-confidence extractions"
      }
    ],

    "testing_plan": [
      {
        "id": "TEST-001",
        "type": "Unit",
        "description": "Test OCR extraction on 10 known invoice samples",
        "expected_outcome": "Field extraction accuracy ≥ 95%"
      }
    ],

    "executive_summary": "string — non-technical narrative suitable for CTO presentation",

    "status_report": [
      {
        "week": 1,
        "title": "Foundation",
        "deliverables": [
          "Project repository initialized",
          "Development environment configured",
          "Core schemas defined"
        ],
        "owner": "Engineering Lead"
      }
    ],

    "delivery_team": {
      "roles": [
        {
          "role": "AI Engineering Lead",
          "count": 1,
          "seniority": "Lead",
          "allocation": "Full-time",
          "responsibilities": "Owns technical delivery, architecture decisions, and weekly status reporting",
          "reports_to": "AI Division Director"
        }
      ],
      "fulfillment_plan": [
        {
          "week": 1,
          "role": "AI Engineering Lead",
          "action": "INTERNAL_ALLOCATION",
          "notes": "Allocated from the AI division bench at project kickoff"
        }
      ]
    },

    "generated_at": "2026-06-02T14:30:00Z",
    "provider_used": "anthropic",
    "model_id": "claude-sonnet-4-6"
  },
  "error": null
}
```

---

### Response — 422 Unprocessable Entity (Validation Error)

Returned when `problem_description` is missing, too short, or too long.

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "problem_description must be at least 100 characters",
    "raw_llm_output": null
  }
}
```

---

### Response — 502 Bad Gateway (LLM Parse Error)

Returned when the LLM returns a response that cannot be parsed into `BlueprintOutput`.

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "PARSE_ERROR",
    "message": "LLM response could not be parsed into the expected schema",
    "raw_llm_output": "{ \"business_problem_diagnosis\": \"...\", ... (truncated malformed JSON)"
  }
}
```

---

### Response — 503 Service Unavailable (LLM Unavailable)

Returned when the LLM API is unreachable (timeout, rate limit, network error).

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "LLM_UNAVAILABLE",
    "message": "LLM provider is temporarily unavailable. Please retry.",
    "raw_llm_output": null
  }
}
```

---

### Response — 500 Internal Server Error

Returned for unexpected server errors.

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred.",
    "raw_llm_output": null
  }
}
```

---

## 4. HTTP Status Code Reference

| Code | Meaning | When Used |
|---|---|---|
| 200 | OK | Successful blueprint generation |
| 422 | Unprocessable Entity | Request validation failure |
| 500 | Internal Server Error | Unexpected server-side exception |
| 502 | Bad Gateway | LLM returned unparseable response |
| 503 | Service Unavailable | LLM API unreachable |

---

## 5. Enum Values

### `problem_type_recommendation`

| Value | Description |
|---|---|
| `RAG` | Retrieval-Augmented Generation — LLM answers grounded in a document corpus |
| `AGENTIC` | Multi-step autonomous agent workflow with tool use |
| `AUTOMATION` | Rule-based or ML-driven process automation |
| `FORECASTING` | Time-series prediction or demand forecasting |
| `OCR` | Document extraction — OCR + structured data parsing |
| `API_INTEGRATION` | Connecting existing systems via API orchestration |
| `HYBRID` | Combination of two or more of the above patterns |

### `impact` and `feasibility` (AI Opportunities)

`HIGH` | `MEDIUM` | `LOW`

### `priority` (Backlog Tickets)

`P0` (critical) | `P1` (high) | `P2` (medium) | `P3` (low)

### `effort` (Backlog Tickets)

`XS` (< 1 day) | `S` (1–2 days) | `M` (3–5 days) | `L` (1–2 weeks) | `XL` (> 2 weeks)

### `phase` (Backlog Tickets)

`Foundation` | `Core` | `Polish` | `Future`

### `category` (Risk Items)

`Technical` | `Data` | `Organizational` | `Timeline`

### `likelihood` and `impact` (Risk Items)

`HIGH` | `MEDIUM` | `LOW`

### `type` (Test Cases)

`Unit` | `Integration` | `E2E` | `Manual`

---

## 6. Example curl Commands

**Generate a blueprint (mock provider):**
```bash
curl -X POST http://localhost:8000/api/v1/blueprint \
  -H "Content-Type: application/json" \
  -d '{
    "problem_description": "Our logistics company processes 3000 invoices per month manually. Each invoice requires a clerk to open a PDF, read line items, match them against purchase orders in our ERP, and flag discrepancies. This takes 2 full-time employees and has a 4% error rate causing payment delays and vendor complaints.",
    "context": "Industry: logistics and freight. ERP: SAP S/4HANA. Invoice formats: PDF, mixed structured and scanned. Team size: 5 ops clerks."
  }'
```

**Health check:**
```bash
curl http://localhost:8000/api/v1/health
```

**Pretty-print the full blueprint with jq:**
```bash
curl -s -X POST http://localhost:8000/api/v1/blueprint \
  -H "Content-Type: application/json" \
  -d '{"problem_description": "..."}' | jq '.data.executive_summary'
```

---

## 7. Rate Limiting (Future)

Not implemented in MVP. Planned for v1.1:
- 10 requests / minute per IP (unauthenticated)
- 60 requests / minute per API key (authenticated)
- Response headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

---

## 8. CORS Configuration

The FastAPI backend allows requests from `http://localhost:8501` (default Streamlit port) during development. In production, the allowed origin should be restricted to the deployed UI domain.
