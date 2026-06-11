# AI Implementation Copilot — Prompt Playbook

This document summarizes the main prompts used to build the **AI Implementation Copilot** using a spec-driven, AI-assisted development workflow with Claude Code.

The purpose of this file is to document not only the final product, but also the engineering process used to guide the AI coding agent in a controlled, incremental, and testable way.

---

## Project Context

**Project name:** AI Implementation Copilot  
**Alternative name:** Ops-to-AI Blueprint Generator

The application receives a messy operational business problem and generates a structured AI implementation blueprint, including:

- Business problem diagnosis
- AI opportunity classification
- Recommended AI architecture
- Indication of whether the problem is RAG, agentic workflow, automation, forecasting, OCR/document extraction, API integration, human-in-the-loop, or hybrid
- Agentic workflow
- Technical backlog
- Risks and assumptions
- Testing plan
- Executive summary
- Delivery status report

The project was designed as a one-week MVP to demonstrate:

- Fast learning
- AI-assisted software development
- Spec-driven development
- Technical product thinking
- Delivery leadership
- Testing discipline
- Git/GitHub workflow
- CI/CD readiness
- Cloud deployment readiness

---

## Development Strategy

The project follows this sequence:

```text
1. Spec first
2. Architecture second
3. Tests third
4. Implementation fourth
5. UI fifth
6. CI/CD sixth
7. Refactor and demo seventh
```

The goal is to avoid random vibe coding and instead use Claude Code as a controlled implementation partner.

---

# Prompt 1 — Create Product Specification

## Objective

Create the initial product and technical documentation before writing code.

## Prompt

```text
You are a senior AI product architect and technical implementation lead.

I want to build a one-week MVP called "AI Implementation Copilot".

Context:
This project is for a CTO interview for an AI Implementation Lead / Technical PM role. The role requires the ability to take messy business problems, translate them into practical AI architectures, organize engineering work, manage delivery, and communicate clearly with non-technical executives.

The application should receive a messy operational business problem and generate an AI implementation blueprint.

The output must include:
1. Business problem diagnosis
2. AI opportunity classification
3. Suggested AI architecture
4. Recommendation on whether this is a RAG, agentic workflow, automation, forecasting, OCR/document extraction, API integration, or hybrid problem
5. Agentic workflow
6. Technical backlog
7. Risks and assumptions
8. Testing plan
9. Executive summary for the client
10. Status report for delivery follow-up

Before writing any code, create the following documentation files:

- docs/PRD.md
- docs/SPEC.md
- docs/ARCHITECTURE.md
- docs/API_SPEC.md
- docs/TEST_PLAN.md
- docs/AI_ASSISTED_WORKFLOW.md
- docs/DEPLOYMENT_NOTES.md
- docs/DEMO_SCRIPT.md

Keep the MVP small, realistic, and demo-ready in one week.

Important principles:
- Do not overengineer.
- Prioritize clarity, testability, and demo value.
- Use FastAPI for the backend.
- Use Streamlit for the demo UI.
- Use pytest for tests.
- Use a mock LLM provider first so tests are deterministic.
- Add an optional real LLM provider later through environment variables.
- Make the project GitHub-ready with CI/CD.
- Make it Docker-ready for future cloud deployment.

Start by creating only the documentation files and a proposed implementation plan. Do not implement code yet.
```

## Expected Output

- Product requirements
- Technical specification
- Initial architecture
- API contract
- Test plan
- Demo script
- Deployment notes

---

# Prompt 2 — Create CLAUDE.md

## Objective

Create project-level instructions for Claude Code to follow during the entire development process.

## Prompt

```text
Create a CLAUDE.md file at the root of the repository.

This file should guide Claude Code during future development sessions.

Include:
- Project purpose
- Architecture principles
- Coding standards
- Testing rules
- Git workflow rules
- Prompting discipline
- What not to do
- Commands to run after changes
- How to handle environment variables and secrets

Important:
- Always prefer small incremental changes.
- Always keep tests deterministic.
- Never commit API keys or secrets.
- Never replace working code with a complex rewrite unless explicitly requested.
- Run pytest after backend changes.
- Update documentation when behavior changes.
```

## Expected Output

A `CLAUDE.md` file that keeps the AI coding agent aligned with the project goals, constraints, and quality expectations.

---

# Prompt 3 — Create Initial Project Skeleton

## Objective

Create the initial working structure of the application.

## Prompt

```text
Now create the initial project structure for the AI Implementation Copilot.

Use:
- FastAPI backend
- Streamlit demo UI
- pytest
- Pydantic models
- service-oriented architecture
- mock LLM provider
- sample cases
- Dockerfile
- docker-compose.yml
- .env.example
- .gitignore
- pyproject.toml
- requirements.txt

Implement only the minimal working skeleton:

Backend endpoints:
- GET /health
- POST /generate-blueprint

The /generate-blueprint endpoint should accept:
{
  "company_context": "optional string",
  "business_problem": "required string",
  "industry": "optional string"
}

It should return a structured JSON blueprint with:
- business_problem_summary
- ai_opportunity_classification
- recommended_solution_type
- suggested_architecture
- agentic_workflow
- engineering_backlog
- risks_and_assumptions
- testing_plan
- executive_summary
- delivery_status_report

For now, use a deterministic mock LLM provider so tests can run without external API calls.

Do not add authentication, database, billing, or multi-tenancy yet.
Keep the code clean, simple, and readable.
```

## Expected Output

- FastAPI backend
- Streamlit demo UI structure
- Mock LLM provider
- Pydantic models
- Minimal working API
- Initial project configuration

---

# Prompt 4 — Create Test Bench

## Objective

Create deterministic automated tests for the MVP.

## Prompt

```text
Create a complete pytest test bench for the current MVP.

Add tests for:
1. GET /health returns 200 and expected payload
2. POST /generate-blueprint rejects empty business_problem
3. POST /generate-blueprint returns all required blueprint sections
4. The classification service correctly identifies likely solution types:
   - RAG
   - agentic workflow
   - workflow automation
   - forecasting
   - OCR/document extraction
   - API integration
   - hybrid
5. The blueprint service works with the mock LLM provider
6. The status report section contains:
   - current_phase
   - next_steps
   - open_risks
   - owner_recommendation
7. Sample cases from app/sample_cases produce valid outputs

Also add:
- tests/conftest.py if useful
- clear fixtures
- readable test names
- no dependency on real external LLM calls
```

## Expected Output

- Unit tests
- API tests
- Contract tests
- Sample case tests
- Deterministic test structure

---

# Prompt 5 — Improve Classification Logic

## Objective

Improve the business logic responsible for identifying the correct AI implementation pattern.

## Prompt

```text
Improve the AI opportunity classification logic.

Create a classification service that uses simple deterministic heuristics to identify likely implementation patterns from the business problem text.

Classification categories:
- RAG
- Agentic Workflow
- Workflow Automation
- Forecasting / Predictive Analytics
- OCR / Document Extraction
- API Integration
- Human-in-the-loop Review
- Hybrid

The service should return:
- primary_solution_type
- secondary_solution_types
- confidence_score from 0 to 1
- rationale in plain English

Keep the logic simple and explainable. Do not use external LLM calls for this classifier yet.

Update tests accordingly.
```

## Expected Output

An explainable classifier that acts like a junior AI implementation architect, not a simple keyword detector.

---

# Prompt 6 — Create Blueprint Prompt Template

## Objective

Create the internal prompt that will later be used by a real LLM provider.

## Prompt

```text
Create app/prompts/blueprint_prompt.md.

This prompt will be used later by a real LLM provider to generate an AI implementation blueprint.

The prompt should instruct the model to act as a senior AI implementation architect and technical delivery lead.

It must produce structured JSON with:
- business_problem_summary
- operational_pain_points
- ai_opportunity_classification
- recommended_solution_type
- suggested_architecture
- agentic_workflow
- data_requirements
- integration_points
- engineering_backlog
- risks_and_assumptions
- testing_plan
- executive_summary
- delivery_status_report

The language should be clear, concise, and suitable for non-technical executives.

Also create a test that validates that the prompt file exists and contains the required output fields.
```

## Expected Output

- Prompt template
- Prompt contract test
- Better separation between prompt engineering and application logic

---

# Prompt 7 — Create Streamlit UI

## Objective

Create a simple demo interface for the application.

## Prompt

```text
Create a simple Streamlit UI for the AI Implementation Copilot.

File:
ui/streamlit_app.py

The UI should allow the user to:
- enter company context
- enter industry
- paste a messy business problem
- click a button to generate the AI implementation blueprint
- display the result in organized sections

Sections to display:
1. Business Problem Summary
2. AI Opportunity Classification
3. Recommended Solution Type
4. Suggested Architecture
5. Agentic Workflow
6. Engineering Backlog
7. Risks and Assumptions
8. Testing Plan
9. Executive Summary
10. Delivery Status Report

The UI should call the FastAPI backend endpoint.

Keep the design simple and demo-friendly.
Add instructions in README on how to run the backend and frontend locally.
```

## Expected Output

- Functional Streamlit UI
- Clear demo flow
- Backend integration
- README instructions

---

# Prompt 8 — Add Optional Real LLM Provider

## Objective

Prepare the architecture for a real Anthropic provider while keeping tests deterministic.

## Prompt

```text
Add an optional real LLM provider architecture without breaking deterministic tests.

Requirements:
- Keep MockLLMProvider as the default for tests.
- Add AnthropicLLMProvider as optional.
- Select provider through environment variable:
  LLM_PROVIDER=mock or anthropic
- Read ANTHROPIC_API_KEY from environment only.
- Never hardcode secrets.
- Update .env.example.
- Update README.
- Add tests ensuring that mock provider remains default in test mode.
- Do not make tests depend on real API calls.
```

## Expected Output

- Provider abstraction
- Mock provider
- Optional Anthropic provider
- Environment variable configuration
- No secrets in code
- Tests that remain stable

---

# Prompt 9 — Add GitHub Actions CI

## Objective

Add a simple CI pipeline to validate the project automatically.

## Prompt

```text
Create a GitHub Actions workflow for CI.

File:
.github/workflows/ci.yml

The workflow should run on:
- push
- pull_request

It should:
1. Check out the repository
2. Set up Python
3. Install dependencies
4. Run pytest
5. Optionally run a basic lint or formatting check if configured
6. Build the Docker image to validate cloud readiness, but do not push it anywhere

Keep it simple and reliable.

Update README with a CI/CD section explaining the workflow.
```

## Expected Output

- `.github/workflows/ci.yml`
- Automated tests on push and pull request
- Docker build validation
- CI/CD section in README

---

# Prompt 10 — Docker and Cloud Readiness

## Objective

Improve containerization and document future cloud deployment options.

## Prompt

```text
Review and improve the Dockerfile and docker-compose.yml for cloud readiness.

Requirements:
- FastAPI backend should run in a container
- Streamlit UI can run locally or through docker-compose if simple enough
- Use environment variables
- Do not include secrets
- Add .dockerignore
- Update docs/DEPLOYMENT_NOTES.md with future deployment options:
  - OCI Container Instances or OCI Kubernetes
  - AWS ECS/Fargate
  - Azure Container Apps
  - Google Cloud Run
  - Render/Railway for quick demo deployment

Do not actually deploy yet. The goal is to make the repo deployment-ready.
```

## Expected Output

- Improved Dockerfile
- docker-compose.yml
- .dockerignore
- Cloud deployment notes
- Deployment-ready project structure

---

# Prompt 11 — Rewrite CTO-Facing README

## Objective

Create a professional README suitable for a CTO review.

## Prompt

```text
Rewrite README.md as a professional CTO-facing README.

It should include:

1. Project title
2. One-line summary
3. Why this project exists
4. How it maps to an AI Implementation Lead role
5. Features
6. Architecture overview
7. Tech stack
8. Local setup
9. How to run tests
10. API example
11. Streamlit UI instructions
12. CI/CD explanation
13. Docker/cloud readiness
14. AI-assisted development workflow
15. Future roadmap
16. Known limitations

Tone:
Clear, practical, senior, not overhyped.

Important:
Make it obvious that this was built as a one-week MVP with production-minded foundations.
```

## Expected Output

A README that explains the project clearly from a technical, business, and delivery perspective.

---

# Prompt 12 — CTO Review

## Objective

Ask Claude Code to review the project from the perspective of a skeptical CTO.

## Prompt

```text
Act as a skeptical CTO evaluating this repository for a senior AI Implementation Lead / Technical PM candidate.

Review the entire project and identify:
1. What looks strong
2. What looks weak
3. What could break during the demo
4. What is overengineered
5. What is underexplained
6. What tests are missing
7. What documentation should be improved
8. What I should say in the interview to explain the project clearly

Do not change code yet. First produce a review report in docs/CTO_REVIEW.md.
```

## Expected Output

- CTO-style critique
- Risk list
- Demo failure points
- Suggested improvements
- Interview positioning guidance

---

# Prompt 13 — Implement High-Impact Fixes

## Objective

Apply only the most important improvements before the demo.

## Prompt

```text
Now implement only the highest-impact fixes from docs/CTO_REVIEW.md.

Prioritize:
- demo reliability
- test coverage
- README clarity
- simple architecture
- avoiding overengineering

Do not introduce new major features.
Run pytest after changes.
```

## Expected Output

- Final refinements
- Improved reliability
- Cleaner documentation
- Passing tests
- Demo-ready repository

---

# Git and GitHub Setup

## Initial Commands

```bash
mkdir ai-implementation-copilot
cd ai-implementation-copilot
git init
```

## First Commit

```bash
git add .
git commit -m "Initial spec-driven project setup"
```

## Create GitHub Repository

Using GitHub CLI:

```bash
gh auth login
gh repo create ai-implementation-copilot --public --source=. --remote=origin --push
```

If the repository should remain private:

```bash
gh repo create ai-implementation-copilot --private --source=. --remote=origin --push
```

---

# Suggested Commit History

Use small, meaningful commits:

```bash
git add .
git commit -m "Add product specs and architecture docs"

git add .
git commit -m "Add FastAPI blueprint endpoint with mock provider"

git add .
git commit -m "Add deterministic pytest test bench"

git add .
git commit -m "Add AI opportunity classification service"

git add .
git commit -m "Add Streamlit demo UI"

git add .
git commit -m "Add optional Anthropic provider architecture"

git add .
git commit -m "Add GitHub Actions CI workflow"

git add .
git commit -m "Add Docker cloud readiness"

git add .
git commit -m "Polish README and demo documentation"
```

---

# Demo Narrative

Use this positioning during the CTO interview:

```text
I built this project to demonstrate the exact workflow I would use as an AI Implementation Lead.

I started from a spec-driven process instead of jumping directly into code. The first step was defining the product requirements, API contract, architecture, testing plan, and demo flow.

Then I used Claude Code to implement the project incrementally: backend first, tests second, UI third, CI/CD and Docker readiness after that.

The application itself is intentionally small, but the structure is production-minded. It has service boundaries, a mock LLM provider for deterministic testing, optional real LLM provider architecture, pytest coverage, GitHub Actions, Docker readiness, and documentation.

The main idea is simple: a client describes a messy operational workflow, and the tool turns that into an AI implementation blueprint with architecture, agents, backlog, risks, testing plan, executive summary, and delivery status.

So the project is not just a coding demo. It reflects how I think about AI implementation: business problem first, architecture second, delivery structure third, and coding as the execution layer.
```

---

# What to Show in the Demo

Recommended sequence:

1. README.md
2. docs/SPEC.md
3. docs/ARCHITECTURE.md
4. CLAUDE.md
5. FastAPI backend
6. Classification service
7. Tests folder
8. Terminal running `pytest`
9. GitHub Actions passing
10. Streamlit UI
11. Example messy business problem
12. Generated AI implementation blueprint
13. Dockerfile and deployment notes

---

# Final Checklist

```text
[ ] GitHub repository created
[ ] README professional and CTO-facing
[ ] PRD/SPEC/Architecture docs created
[ ] CLAUDE.md created
[ ] FastAPI backend working
[ ] Streamlit UI working
[ ] Mock LLM provider working
[ ] Optional Anthropic provider prepared
[ ] Classification service implemented
[ ] Sample cases created
[ ] pytest test bench passing
[ ] GitHub Actions passing
[ ] Dockerfile created
[ ] .env.example created
[ ] Deployment notes created
[ ] Demo script created
[ ] Small and clear commits
```

---

# Final Principle

This project should not look like a random AI-generated code dump.

It should look like a controlled AI-assisted implementation process:

> Spec → Architecture → Tests → Implementation → UI → CI/CD → Review → Demo

The goal is to demonstrate not only coding ability, but also technical judgment, delivery ownership, product thinking, and implementation leadership.
