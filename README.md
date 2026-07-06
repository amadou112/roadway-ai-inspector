# Roadway AI Inspector & Design Assistant

An enterprise-grade, DOT/FHWA-style AI platform for roadway, bridge, pavement, traffic,
drainage, safety, and construction inspection workflows — built as a full-stack portfolio
project.

There are two ways to run this app, described below: a **Streamlit app** (single process,
simplest to deploy for free) and a **FastAPI + Next.js** stack (separate backend/frontend,
more "enterprise SaaS" in feel, run via Docker Compose). Both share the exact same database
models and AI service logic in `backend/app/`.

## Streamlit app (recommended — simplest to run and deploy)

One process, one free external Postgres, no Docker, no separate frontend/backend deploy.
Streamlit calls the RAG/PDF/report service functions directly in-process — same code, no
REST layer.

**Run locally:**

```sh
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create `backend/.streamlit/secrets.toml`:

```toml
DATABASE_URL = "postgresql://user:pass@host/dbname?sslmode=require"  # e.g. a free Neon.tech DB
OPENAI_API_KEY = ""  # leave blank for stub mode (no cost, canned AI text); add a real key for live AI
```

```sh
streamlit run streamlit_app.py
```

On first run it automatically applies Alembic migrations, seeds the 7 demo role accounts and
a demo project (sample RFIs/submittals/risks/NCRs/safety/schedule/cost data + 2 sample spec
documents), and ingests real Delaware NBI/HPMS open data. There's no login page — use the
**Viewing as** picker in the sidebar to switch between the 7 seeded roles.

**Deploy to Streamlit Community Cloud (free, no card):**

1. Get a free Postgres database — https://neon.tech (sign up, create a project, copy the
   connection string). No card required.
2. Go to https://share.streamlit.io → **New app** → pick this repo/branch → set
   **main file path** to `backend/streamlit_app.py`.
3. Under **Advanced settings → Secrets**, paste:
   ```toml
   DATABASE_URL = "<your Neon connection string>"
   OPENAI_API_KEY = ""
   ```
4. Deploy. The app sleeps after inactivity on the free tier (a visitor after a quiet period
   waits ~30–60s for it to wake up) and its local filesystem resets on every restart — the
   seed script re-indexes the two sample documents into the vector store on every boot
   specifically to handle this cleanly, so the AI Assistant demo keeps working across restarts.

## FastAPI + Next.js stack (alternative architecture)

Same backend service code, exposed over a REST API (`backend/app/api/`), with a separate
Next.js 16 + TypeScript + Tailwind + Recharts + Leaflet frontend. Useful if you want a more
polished, separately-deployable frontend, or to see a "real" microservice-style split — but
it's two deploy targets instead of one (see `render.yaml` for the backend, Vercel for the
frontend), which is meaningfully more setup than the Streamlit path above.

```sh
docker compose up --build
```

Starts Postgres, the FastAPI backend (migrations + seed + open-data ingestion on boot), and
the Next.js frontend.

- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs

No login page here either — every visitor is auto-authenticated as a demo account, with a
role switcher in the top bar (password `RoadwayDemo!2026`, used internally, not shown in the UI).

Running without Docker: see `backend/requirements.txt` + `alembic upgrade head` +
`uvicorn app.main:app --reload` for the backend, `npm install && npm run dev` in `frontend/`
for the frontend (set `NEXT_PUBLIC_API_URL` if the backend runs elsewhere).

## Features (both versions)

- **Document RAG**: upload DOT specs, FHWA manuals, inspection reports, RFIs, submittals,
  plan sheets, and daily reports; ask questions and get cited answers.
- **Construction inspection assistant**: generates a professional Daily Inspection Report
  (narrative + PDF) from structured field notes, quantities, weather, equipment, materials,
  and deficiencies.
- **Design review assistant**: AI review of uploaded design documents for missing items,
  conflicts, constructability issues, safety concerns, and compliance gaps — grounded against
  indexed specifications.
- **Bridge & roadway data dashboard**: real Delaware DOT open data — National Bridge
  Inventory (NBI), FARS crash records, and HPMS pavement condition — on a map with condition
  dashboards.
- **Role-based access**: Program Manager, Project Manager, Resident Engineer, Inspector,
  Designer, Contractor, and DOT Executive, each with a tailored navigation/workflow.
- **Program dashboards**: RFIs, submittals, risk register (with heat map), non-conformance
  reports, safety issues, schedule status, and cost tracking.
- **Executive reporting**: AI-generated weekly status and risk summary reports as DOT-styled
  PDFs.

## Architecture notes

- **RAG pipeline**: PDF/text extraction → chunking (LangChain text splitters) → OpenAI
  embeddings → ChromaDB (persistent, filtered by project) → grounded chat completion with
  inline citations.
- **LLM provider**: all OpenAI calls go through `app/services/llm_provider.py`, which falls
  back to deterministic stub responses when `OPENAI_API_KEY` is unset — the whole app is
  demoable without a key, at zero cost, regardless of traffic. The FastAPI version additionally
  rate-limits every LLM-calling endpoint (`app/core/rate_limit.py`, 5/min & 30/hour per IP) as
  defense-in-depth for whenever a real key is enabled.
- **Ephemeral-disk safe**: free hosting tiers (Streamlit Community Cloud, Render's free web
  service) reset the local filesystem on every restart. `scripts/seed_demo_project.py`
  re-indexes the sample documents into Chroma on every boot rather than a one-time-only seed,
  so the RAG demo doesn't silently go stale after a restart.
- **Open data**: bundled `backend/data/DE25.txt` is a real 2025 National Bridge Inventory
  extract for Delaware (FHWA). FARS crash data and HPMS pavement data are fetched live at
  seed time from NHTSA/USDOT public endpoints, with a graceful skip if those endpoints are
  unreachable from your network.
- **PDF generation**: ReportLab (pure Python, no system dependencies) generates inspection
  reports, design review reports, and executive reports with a consistent DOT-style template.
