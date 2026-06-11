# Deployment Notes
## AI Implementation Copilot

**Version:** 1.0  
**Date:** 2026-06-02

---

## 1. Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11+ | Required for `tomllib`, `match` statements |
| pip | 23+ | For `pyproject.toml` editable installs |
| Docker | 24+ | Optional — for containerized deployment |
| Docker Compose | v2 | Optional — included with Docker Desktop |
| Git | 2.40+ | For CI/CD and version control |

---

## 2. Environment Variables

| Variable | Default | Required | Description |
|---|---|---|---|
| `LLM_PROVIDER` | `mock` | No | LLM backend: `mock` or `anthropic` |
| `ANTHROPIC_API_KEY` | `""` | When `LLM_PROVIDER=anthropic` | Anthropic API secret key |
| `MODEL_ID` | `claude-sonnet-4-6` | No | Anthropic model identifier |
| `API_HOST` | `0.0.0.0` | No | FastAPI bind host |
| `API_PORT` | `8000` | No | FastAPI bind port |
| `API_RELOAD` | `false` | No | Enable uvicorn auto-reload (dev only) |
| `UI_API_BASE_URL` | `http://localhost:8000` | No | FastAPI URL used by Streamlit |

Create a `.env` file in the project root for local development. The `.gitignore` excludes `.env` from version control.

### API Key Management — Two Options

**Option A: UI-based (recommended for demos and interactive use)**

No `.env` changes needed. Open the Streamlit sidebar → *LLM Settings*:
1. Select **Anthropic Claude** from the provider dropdown.
2. Paste your `sk-ant-...` key into the password field.
3. The key is stored only in the browser session (`st.session_state`). It is transmitted to the FastAPI backend as an HTTP header (`X-API-Key`) and used for that request only. It is never written to disk, never logged, and never committed to version control.

**Option B: Environment variable (recommended for Docker / headless use)**

Set in `.env` or as an environment variable before starting the API:
```
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

The API key set via the UI header always takes precedence over the environment variable for that request.

---

## 3. Local Development Setup

### 3.1 Clone and Install

```bash
git clone https://github.com/alexandretf71/Nexton_MVP.git
cd Nexton_MVP

# Create virtual environment
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
# .\.venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dev dependencies
pip install -r requirements-dev.txt
```

### 3.2 Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env — set LLM_PROVIDER and optionally ANTHROPIC_API_KEY
```

### 3.3 Run Tests

```bash
# All tests (mock provider, no API key needed)
pytest tests/ -v --cov=app --cov-report=term-missing

# Quick smoke test
pytest tests/ -x -q
```

### 3.4 Start the API Server

```bash
# Development mode (auto-reload on file change)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API is available at:
- `http://localhost:8000/api/v1/health`
- `http://localhost:8000/docs` (Swagger UI)
- `http://localhost:8000/redoc` (ReDoc)

### 3.5 Start the Streamlit UI

In a second terminal:

```bash
# Ensure the virtual environment is activated
streamlit run ui/app.py
```

UI is available at `http://localhost:8501`.

---

## 4. Docker Deployment

### 4.1 Build the API Image

```bash
docker build -t ai-copilot-api .
```

### 4.2 Run with Docker Compose

```bash
# Start both FastAPI and Streamlit
docker compose up

# Run in background
docker compose up -d

# Stop
docker compose down
```

Services:
- FastAPI: `http://localhost:8000`
- Streamlit: `http://localhost:8501`

### 4.3 Docker Compose with Real LLM

```bash
ANTHROPIC_API_KEY=sk-ant-... docker compose up
```

Or set `ANTHROPIC_API_KEY` in a `.env` file — Docker Compose reads it automatically.

### 4.4 Dockerfile Overview

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
COPY ui/ ./ui/
EXPOSE 8000 8501
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

The Streamlit service is defined as a separate container in `docker-compose.yml` to allow independent scaling.

---

## 5. CI/CD Pipeline

### GitHub Actions Workflow (`.github/workflows/ci.yml`)

Triggers: push to any branch, pull request to `main`.

**Jobs:**

```
lint ──────────────────────────┐
                               ├── test (requires lint pass)
type-check ────────────────────┘
                               │
                               ▼
                         docker-build (on main branch only)
```

**lint job:**
```bash
ruff check app/ tests/
```

**type-check job:**
```bash
mypy app/ --ignore-missing-imports
```

**test job:**
```bash
pytest tests/ -v --cov=app --cov-report=xml --cov-fail-under=80
```

**docker-build job** (main branch only):
```bash
docker build -t ai-copilot-api .
```

No Docker push in MVP — cloud registry integration is a v1.1 task.

**Repository:** `https://github.com/alexandretf71/Nexton_MVP`

---

## 6. Dependencies

### `requirements.txt` (production)

```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
pydantic>=2.7.0
pydantic-settings>=2.2.0
anthropic>=0.28.0
httpx>=0.27.0
```

### `requirements-dev.txt` (development + testing)

```
-r requirements.txt
streamlit>=1.35.0
pytest>=8.2.0
pytest-asyncio>=0.23.0
pytest-cov>=5.0.0
httpx>=0.27.0
ruff>=0.4.0
mypy>=1.10.0
```

---

## 7. Project Structure Reference

```
Nexton_MVP/
├── app/                    # FastAPI application
│   ├── api/routes/         # Route handlers
│   ├── core/               # Config + prompt templates
│   ├── models/             # Pydantic schemas
│   └── services/llm/       # LLM provider layer
├── ui/                     # Streamlit UI
├── tests/                  # pytest test suite
│   └── fixtures/           # Mock JSON responses + sample problems
├── docs/                   # Documentation (this directory)
├── .github/workflows/      # GitHub Actions CI
├── .env.example            # Environment variable template
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml          # Ruff + mypy config
└── README.md
```

---

## 8. Cloud Deployment — Render.com (Recommended)

Render is the recommended free deployment target. It supports two Docker-based web services
with GitHub auto-deploy and no credit card required.

**Trade-off:** Free services spin down after 15 min of inactivity and take 30–60s to wake up
on the next request. For demos, open the URL ~1 min before the presentation to pre-warm both services.

### 8.1 One-time setup

1. Create a free account at [render.com](https://render.com) (GitHub login works).
2. On the Render dashboard: **New → Blueprint**.
3. Connect the GitHub repo `alexandretf71/Nexton_MVP`.
4. Render reads `render.yaml` from the repo root and provisions two services automatically:
   - `nexton-api` — FastAPI backend
   - `nexton-ui` — Streamlit frontend

### 8.2 Post-deploy env var wiring (required — do this once)

After the first deploy, Render assigns public URLs to both services. Wire them together:

| Service | Variable | Value to set |
|---|---|---|
| `nexton-api` | `UI_ORIGIN` | `https://nexton-ui.onrender.com` |
| `nexton-ui` | `UI_API_BASE_URL` | `https://nexton-api.onrender.com` |

Set each variable in the service's **Environment** tab on the Render dashboard.
Both services auto-redeploy when you save.

### 8.3 Verify the deployment

```
# API health check
curl https://nexton-api.onrender.com/health

# Expected: {"status":"ok","provider":"mock","version":"..."}
```

Then open `https://nexton-ui.onrender.com` in a browser — the Streamlit UI should load.

### 8.4 Auto-deploy on push

Every push to `main` triggers a new deploy on both services automatically.
No manual steps needed after the initial setup.

### 8.5 Using real LLM providers in the cloud

The deployed app runs with `LLM_PROVIDER=mock` by default (no API key needed).
Users can provide their own Anthropic or OpenAI keys via the sidebar — keys are passed as
HTTP headers and never stored server-side. No env var changes are needed on Render for this.

To switch the server default to a real provider, set in the `nexton-api` service env vars:
```
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

---

## 9. Other Cloud Deployment Targets

| Platform | Notes |
|---|---|
| **Railway** | Slightly better DX (no cold starts); $5/month free credit then paid |
| **Fly.io** | Truly always-on free tier; requires `flyctl` CLI and two `fly.toml` configs |
| **GCP Cloud Run** | Serverless; scales to zero; more setup required |
| **AWS App Runner** | Similar to Cloud Run; good if team already uses AWS |

---

## 9. No Persistent Storage

The MVP has no database. All data is ephemeral per HTTP request. There is nothing to migrate, back up, or restore. This is intentional for demo simplicity.

If persistence is added in v1.1 (blueprint history), the recommended approach is:
- SQLite for local/demo
- PostgreSQL (via SQLAlchemy + Alembic) for production
