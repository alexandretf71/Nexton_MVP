# CLAUDE.md — AI Implementation Copilot

This file guides Claude Code during all development sessions on this project.
Read it fully before making any changes.

---

## Project Purpose

**AI Implementation Copilot** is a FastAPI + Streamlit application that receives a messy
business problem description and returns a structured AI implementation blueprint across
10 sections (diagnosis, architecture, backlog, executive summary, and more).

Built as a one-week MVP for a CTO interview demonstrating AI Implementation Lead skills.
The design goal is demo-ready, not production-complete.

Full documentation lives in `docs/`. Start with `docs/PRD.md` for context,
`docs/ARCHITECTURE.md` for system design, and `docs/API_SPEC.md` for endpoint contracts.

---

## Repository Layout

```
app/                    # FastAPI application
  api/routes/           # Route handlers (blueprint.py, health endpoint)
  core/                 # config.py (settings), prompt_templates.py
  models/schemas.py     # All Pydantic models — single source of truth for data shapes
  services/
    llm/                # LLM provider layer: base.py, mock.py, anthropic.py
    blueprint_generator.py   # Orchestrates prompt → LLM → validated output
ui/app.py               # Streamlit demo interface
tests/                  # pytest test suite
  fixtures/             # mock_blueprint.json, sample_problems.py
docs/                   # All 8 documentation files
Dockerfile
docker-compose.yml
requirements.txt        # Production dependencies only
requirements-dev.txt    # Includes test + lint tools
```

---

## Architecture Principles

- **LLM providers are swappable.** All LLM calls go through the `LLMProvider` abstract
  interface in `app/services/llm/base.py`. Never call the Anthropic SDK directly from a
  route or generator — always go through the interface.

- **Pydantic is the validation boundary.** Every LLM response must pass through
  `BlueprintOutput.model_validate()` before it touches the API response. Never return
  unvalidated LLM output to the caller.

- **UI and API are decoupled.** Streamlit calls FastAPI over HTTP. No shared state,
  no direct imports between `ui/` and `app/`. The API must work standalone (curl, Postman).

- **No persistent storage.** Blueprints are ephemeral per request. Do not add a database
  without an explicit request and discussion.

- **Single LLM call for MVP.** The entire 10-section blueprint comes from one API call.
  Multi-step agentic pipelines are a future enhancement, not current scope.

- **Small, incremental changes.** Make the smallest change that satisfies the requirement.
  Do not refactor surrounding code unless it is directly in the way.

---

## Coding Standards

- **Python 3.11+.** Use modern syntax: `match`, `tomllib`, `X | Y` union types.
- **Pydantic v2.** Use `model_validate`, `field_validator`, `model_config`. Not v1 patterns.
- **Async throughout the API layer.** Route handlers and `LLMProvider.complete()` are `async`.
- **Type annotations on all function signatures.** No bare `Any` unless truly unavoidable.
- **No comments explaining what code does.** Only comment when the *why* is non-obvious
  (a workaround, a hidden constraint, a subtle invariant).
- **No docstrings on obvious functions.** A one-line docstring on a helper that parses JSON
  is noise. Reserve docstrings for public interfaces that need behavioral contracts.
- **No premature abstractions.** Three similar lines is better than a helper that will
  only ever be called in those three places.
- **Error messages must be actionable.** "LLM unavailable" is better than "error 503".
  Include what to check or retry.

### Naming Conventions

| Thing | Convention | Example |
|---|---|---|
| Files | `snake_case.py` | `blueprint_generator.py` |
| Classes | `PascalCase` | `AnthropicLLMProvider` |
| Functions / methods | `snake_case` | `build_user_prompt` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_MODEL_ID` |
| Env vars | `UPPER_SNAKE_CASE` | `ANTHROPIC_API_KEY` |
| Pydantic models | `PascalCase` | `BlueprintRequest` |

---

## Testing Rules

- **All automated tests use `MockLLMProvider`.** No test ever calls the Anthropic API.
  Tests must pass with no network access and no API key set.

- **Tests are deterministic.** If a test could flake (timing, randomness, external call),
  fix it before committing. Non-deterministic tests are worse than no tests.

- **Never mock what you own.** Mock external dependencies (Anthropic SDK); test internal
  logic with real objects. Do not mock `BlueprintGenerator` in API tests — use the real
  generator with a mock provider.

- **Coverage target: ≥ 80% of `app/`.** Check with:
  ```
  pytest tests/ --cov=app --cov-report=term-missing
  ```

- **Run the full suite after every backend change:**
  ```
  pytest tests/ -v
  ```

- **Test file layout mirrors source layout:**
  - `tests/test_api.py` → tests for `app/api/`
  - `tests/test_blueprint_generator.py` → tests for `app/services/`
  - `tests/test_schemas.py` → tests for `app/models/`

- **Fixtures live in `tests/conftest.py`.** Shared objects (test client, mock provider,
  sample requests) go there. Do not repeat fixture setup inside test functions.

---

## Environment Variables and Secrets

**Never commit secrets.** The `.env` file is in `.gitignore`. Never add it to version control.
Never hardcode an API key, even in a comment.

| Variable | Default | Notes |
|---|---|---|
| `LLM_PROVIDER` | `mock` | Set to `anthropic` to use real LLM |
| `ANTHROPIC_API_KEY` | *(empty)* | Required when `LLM_PROVIDER=anthropic` |
| `MODEL_ID` | `claude-sonnet-4-6` | Anthropic model identifier |
| `API_HOST` | `0.0.0.0` | FastAPI bind host |
| `API_PORT` | `8000` | FastAPI bind port |
| `UI_API_BASE_URL` | `http://localhost:8000` | Used by Streamlit to call the API |

Copy `.env.example` to `.env` for local development. The example file contains no real values.

If a new env var is added:
1. Add it to `app/core/config.py` with a safe default.
2. Add it to `.env.example` with a placeholder value and a comment.
3. Document it in the table above and in `docs/DEPLOYMENT_NOTES.md`.

---

## Git Workflow Rules

- **Remote repository:** `https://github.com/alexandretf71/Nexton_MVP`
- **Branch from `main`.** Branch names: `feat/short-description`, `fix/short-description`,
  `docs/short-description`, `chore/short-description`.
- **One logical change per commit.** Do not bundle a feature and a refactor in one commit.
- **Commit messages:** imperative mood, present tense, under 72 characters.
  - Good: `Add AnthropicLLMProvider with prompt caching`
  - Bad: `Added some changes to the llm stuff`
- **Never force-push `main`.** All merges to main go through a PR.
- **Never commit with `--no-verify`.** If a hook fails, fix the underlying issue.
- **Update docs in the same commit as the behavior change.** If a schema field is renamed,
  update `docs/SPEC.md` and `docs/API_SPEC.md` in the same commit.

---

## Commands to Run After Changes

| Situation | Command |
|---|---|
| After any `app/` change | `pytest tests/ -v` |
| After schema changes | `pytest tests/test_schemas.py -v` |
| After route changes | `pytest tests/test_api.py -v` |
| Before committing | `ruff check app/ tests/` |
| To check types | `mypy app/ --ignore-missing-imports` |
| To start the API | `uvicorn app.main:app --reload` |
| To start the UI | `streamlit run ui/app.py` |
| To run everything via Docker | `docker compose up` |
| Full CI simulation | `ruff check app/ tests/ && mypy app/ --ignore-missing-imports && pytest tests/ -v --cov=app --cov-fail-under=80` |

---

## Prompting Discipline

When the LLM system prompt or user prompt templates change:

1. Edit `app/core/prompt_templates.py`.
2. Check that the system prompt still instructs the LLM to return only JSON (no prose).
3. Check that the output schema injected in the system prompt matches the current
   `BlueprintOutput` model in `app/models/schemas.py`.
4. Run the full test suite — mock tests validate structure, not content.
5. Manually test with one real problem using `LLM_PROVIDER=anthropic` before merging.
6. If the change affects token usage significantly, update the budget estimate in
   `docs/AI_ASSISTED_WORKFLOW.md`.

The system prompt is a module-level constant to enable Anthropic prompt caching.
Do not move it inside a function without updating the caching configuration in
`app/services/llm/anthropic.py`.

---

## What Not To Do

- **Do not add features beyond the current task.** If you notice something unrelated
  that could be improved, flag it as a suggestion — do not implement it.

- **Do not replace working code with a complex rewrite** unless the user explicitly
  requests a rewrite. Incremental improvements only.

- **Do not add error handling for scenarios that cannot happen.** Trust Pydantic
  validation at the boundary. Do not defensively re-validate already-validated data.

- **Do not add logging statements unless asked.** The codebase will have structured
  logging added in a later phase. Ad-hoc `print()` statements create noise.

- **Do not add `Optional` wrappers to fields that are always required.** Keep the
  schema strict. Nullable fields hide bugs.

- **Do not skip tests to save time.** If a change is too complex to test, break it
  into smaller changes.

- **Do not add backwards-compatibility shims** for removed code. If something is
  deleted, delete it completely.

- **Do not use `Any` type hints in `app/models/schemas.py`.** Every field in a
  Pydantic model must have a concrete type.

- **Do not call `os.environ` directly.** Always use the `settings` object from
  `app/core/config.py`.

---

## UI Branding

The Streamlit interface uses Nexton (nexton.dev) brand assets. Follow these rules when working on `ui/app.py`:

- **Logo files:** `ui/assets/nexton_logo.svg` (blue "N" mark) and `ui/assets/nexton_logo_white.svg`
  (white version for dark backgrounds). The sidebar renders the blue mark inline next to the
  lowercase "nexton" wordmark.
- **Fonts (Google Fonts):** K2D for headings and the wordmark, Inter for body text.
- **Brand colors** (for custom CSS injected via `st.markdown`):

  | Token           | Hex       | Usage                             |
  |-----------------|-----------|-----------------------------------|
  | Primary blue    | `#337BFF` | Buttons, highlights, accents      |
  | Hover blue      | `#0051E5` | Button hover state                |
  | Deep navy       | `#172344` | Headings, wordmark                |
  | Page background | `#F9FAFB` | App background                    |
  | Pale blue       | `#F1F6FF` | Subtle tinted surfaces            |
  | Accent green    | `#38A75D` | Positive / success accents        |

- If the logo file is missing at runtime, Streamlit should fall back gracefully and render the
  text "Nexton" in its place — never crash the UI over a missing asset.
- Do not alter the logo (no filters, no overlays, no recoloring) in code.

---

## Documentation Rules

- Update `docs/SPEC.md` when a Pydantic schema changes.
- Update `docs/API_SPEC.md` when an endpoint contract changes (path, request, response).
- Update `docs/DEPLOYMENT_NOTES.md` when dependencies or env vars change.
- Update `docs/TEST_PLAN.md` when new test categories are added.
- Do not create new documentation files for individual features — update existing docs.
- Do not create planning, analysis, or decision documents as files. Use the conversation.
