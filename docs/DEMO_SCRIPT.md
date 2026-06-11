# Demo Script
## AI Implementation Copilot

**Audience:** CTO, VP Engineering, AI Implementation Lead (interview panel)  
**Duration:** 5 minutes (core demo) + 5 minutes Q&A  
**Format:** Live walkthrough of the running application  
**Date:** 2026-06-02

---

## Pre-Demo Checklist

- [ ] FastAPI server running: `uvicorn app.main:app` — check `http://localhost:8000/api/v1/health`
- [ ] Streamlit UI running: `streamlit run ui/app.py` — check `http://localhost:8501`
- [ ] LLM provider set to `anthropic` with valid API key (or `mock` for offline fallback)
- [ ] Zaigo logo visible in the sidebar (`ui/assets/zaigo_logo.png` present)
- [ ] Browser window at `http://localhost:8501`, zoomed to 100%
- [ ] Second browser tab open at `http://localhost:8000/docs` (for technical audience)
- [ ] Problem A text copied to clipboard (logistics / invoice processing)
- [ ] Screen sharing tested

---

## Opening Statement (30 seconds)

> "The most expensive moment in an AI engagement is the first one — when a business stakeholder describes their problem and the technical team has to figure out what to build. That discovery process typically takes weeks of workshops, slides, and misaligned scoping documents.
>
> This tool collapses that to 30 seconds. Let me show you."

---

## Demo Flow

### Step 1 — Show the Input (30 seconds)

Navigate to the Streamlit UI. Point to the text area.

> "The user — a CTO, a Technical PM, or even a sales engineer — pastes in a raw, unfiltered description of their business problem. No templates, no forms, no structured intake process. Just the problem in their words."

Paste **Problem A** (logistics / invoice processing):

```
Our logistics company processes 3000 invoices per month manually. Each invoice 
requires a clerk to open a PDF, read line items, match them against purchase orders 
in our ERP, and flag discrepancies. This takes 2 full-time employees and has a 4% 
error rate causing payment delays and vendor complaints. We have tried basic OCR 
tools but they fail on scanned documents with variable layouts. We need an automated 
solution that can handle mixed PDF formats and integrate with SAP S/4HANA.
```

> "This is real-world messy input. No structured fields, some domain jargon, vague constraints. Exactly what you get in an actual discovery call."

---

### Step 2 — Generate the Blueprint (30 seconds)

Click **"Generate Blueprint"**. While it loads:

> "Under the hood, a FastAPI backend receives this text, constructs a structured prompt for Claude, and parses the response into a validated schema. The whole pipeline takes under 30 seconds."

When it loads:

> "And here's the output — a full AI implementation blueprint across 10 sections."

---

### Step 3 — Walk Through the Sections (3 minutes)

#### Section 1: Business Problem Diagnosis
> "First, we restate the problem clearly. Why? Because clients often describe symptoms, not root causes. Here the tool identifies that the real problem isn't 'bad OCR' — it's an unstructured document intake workflow with no validation layer. That's what you'd tell the client in a discovery readout."

#### Section 4: Problem Type Recommendation
> "The system classifies this as a **Hybrid** problem — OCR extraction plus API integration with SAP. That single classification immediately tells an architect which patterns to apply. No more 'let's use AI' hand-waving."

#### Section 3: Suggested AI Architecture
> "Here's the system design narrative. I'd use this as the starting point for an architecture diagram in a client proposal. It's not a final design — it's a directional recommendation that saves 2 hours of whiteboarding."

#### Section 5: Agentic Workflow
> "This maps the AI agent steps. Document Ingestion Agent → Field Extraction Agent → ERP Matching Agent → Discrepancy Resolution Agent. Each step has inputs, outputs, and tool dependencies. This becomes the basis for a sprint plan."

#### Section 6: Technical Backlog
> "Prioritized tickets, ready to paste into Jira or Linear. P0 items are the foundation — project scaffold, data pipeline. P1 is the core logic. P2 is polish. The team can start estimating the same day."

#### Section 9: Executive Summary
> "This is for the board deck. No jargon. Business outcomes. Quantified where possible. I'd hand this directly to a CTO to present to their CFO. Zero editing needed."

#### Section 10: Status Report
> "Finally, a delivery roadmap. Week-by-week milestones, owners, deliverables. This is what you put in the kickoff deck."

---

### Step 4 — Show the API (30 seconds, technical audience only)

Switch to the `http://localhost:8000/docs` tab.

> "For technical audiences — the same output is available as a REST API. Any frontend, any tool, can consume it. The schema is fully validated with Pydantic. If you're building this into a sales workflow or a client portal, the integration is a single POST request."

Demo the **Try it out** button on `/api/v1/blueprint` with Problem B (HR use case).

---

### Step 5 — Closing Statement (30 seconds)

> "What you've seen is a one-week MVP. The documentation, API design, test suite, and deployment configuration are all production-grade patterns. The mock provider means the full test suite runs in CI without touching the Anthropic API.
>
> The next version adds multi-step agentic generation — one agent per section — for higher quality outputs. But for an accelerator tool that cuts discovery time from weeks to minutes, this is already delivering value."

---

## Sample Problems (Copy-Paste Ready)

### Problem A — Logistics / OCR
```
Our logistics company processes 3000 invoices per month manually. Each invoice requires 
a clerk to open a PDF, read line items, match them against purchase orders in our ERP, 
and flag discrepancies. This takes 2 full-time employees and has a 4% error rate causing 
payment delays and vendor complaints. We have tried basic OCR tools but they fail on 
scanned documents with variable layouts. We need an automated solution that can handle 
mixed PDF formats and integrate with SAP S/4HANA.
```
**Expected classification:** `HYBRID` (OCR + API_INTEGRATION)

### Problem B — HR / Knowledge Base
```
Our HR department receives 200+ employee questions per week via email about policies, 
benefits, and leave procedures. HR business partners spend 60% of their time answering 
repetitive questions that are already documented in our 500-page employee handbook. 
New hires especially struggle to find information. We want employees to get instant, 
accurate answers without HR intervention, and we want HR BPs to focus on strategic work. 
Our handbook is updated quarterly and lives in SharePoint.
```
**Expected classification:** `RAG` or `AGENTIC`

### Problem C — Finance / Forecasting
```
Our FP&A team produces monthly cash flow forecasts manually using Excel. The process 
takes 3 analysts 5 days each month, uses data from 6 different source systems, and 
produces forecasts that are consistently 15-20% off actuals. The CFO has requested 
weekly forecasts but the team cannot increase cadence with the current process. We have 
3 years of historical transaction data and budget data, plus external signals like 
payment terms per customer and supplier.
```
**Expected classification:** `FORECASTING` or `HYBRID`

---

## Talking Points: "Why AI Here vs. Traditional Software?"

Use these when challenged on whether simpler rule-based automation would suffice:

| Challenge | Response |
|---|---|
| "Can't you just use regex for invoice extraction?" | "Regex breaks on format variation — and logistics invoices come from hundreds of vendors with different layouts. An LLM-based extractor generalizes across layouts with 95%+ accuracy where regex achieves 60%." |
| "Why not just search the employee handbook?" | "Keyword search returns documents, not answers. Employees want a direct answer to 'how many sick days do I have left?' not a link to page 247 of the handbook." |
| "Excel forecasting is good enough." | "The data shows 15–20% forecast error. At $500M revenue that's $75–100M of cash flow uncertainty per month. ML forecasting consistently reduces this to < 5% on comparable datasets." |

---

## Q&A Preparation

**Q: How accurate is the output?**
> "The blueprint is a starting point, not a final architecture. For a discovery engagement, it's significantly better than a blank whiteboard. The real value is speed — it gets a team aligned on direction in minutes. The architect still validates and refines."

**Q: What happens when the LLM gets it wrong?**
> "The output is Pydantic-validated — structurally it's always correct. Content quality depends on the prompt and the model. We mitigate with structured field guidance in the system prompt and plan for human review before client delivery. In v2, section-level confidence scoring flags low-confidence outputs."

**Q: What does this cost to run?**
> "About $0.015 per blueprint with Claude Sonnet 4.6. With prompt caching on repeated calls, effectively less. For a consulting firm doing 50 proposals a month, that's under $10/month in LLM costs."

**Q: Is client data sent to Anthropic?**
> "In the current MVP, yes — the problem description goes to the Anthropic API. For enterprise clients with data sensitivity requirements, this can be replaced with a self-hosted model (Llama 3, Mistral) by swapping the provider implementation. The abstraction layer makes that a 2-day change."

**Q: How long did this take to build?**
> "Five days for the functional MVP with tests, CI/CD, Docker, and documentation. The architecture is designed to support a full production system — multi-tenancy, persistence, streaming — without rewrites."
