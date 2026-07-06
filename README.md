# Roadway AI Inspector & Design Assistant

**Live demo:** https://roadway-ai-inspector-amadou112-6455s-projects.vercel.app — no sign-in
required; every visitor is auto-authenticated as a demo account and can switch roles from the
top bar. The public deployment runs the AI features in "stub mode" (see below) so it can't
incur OpenAI cost no matter how much traffic it gets.

An enterprise-grade, DOT/FHWA-style AI platform for roadway, bridge, pavement, traffic,
drainage, safety, and construction inspection workflows — built as a full-stack portfolio
project.

**Stack:** FastAPI + PostgreSQL + ChromaDB + LangChain + OpenAI (backend) · Next.js 16 +
TypeScript + Tailwind + Recharts + Leaflet (frontend) · Docker Compose.

## Features

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

## Prerequisites

- **Docker Desktop** (required — not installed by default on this machine; install from
  https://www.docker.com/products/docker-desktop/ before continuing)
- An **OpenAI API key** (optional but recommended — without one, the app runs in "stub mode"
  with deterministic placeholder AI responses so you can still demo the full workflow)

## Setup

1. Copy the environment file and fill in your OpenAI key:

   ```sh
   cp .env.example .env
   # edit .env and set OPENAI_API_KEY=sk-...
   ```

2. Start everything:

   ```sh
   docker compose up --build
   ```

   This starts Postgres, then the backend (which runs Alembic migrations, seeds demo users,
   seeds a demo project with sample RFIs/submittals/risks/NCRs/safety/schedule/cost data and
   two sample specification documents, and ingests real Delaware bridge/crash/pavement data),
   then the frontend.

3. Open the app:

   - Frontend: http://localhost:3000
   - Backend API docs: http://localhost:8000/docs

4. There is no sign-in page — you land straight on the dashboard, auto-authenticated as the
   Program Manager demo account. Use the **Viewing as** picker in the top bar to switch
   between the 7 seeded roles with one click (no passwords):

   | Role | Email |
   |---|---|
   | Program Manager | pm@demo.gov |
   | Project Manager | projectmanager@demo.gov |
   | Resident Engineer | resident-engineer@demo.gov |
   | Inspector | inspector@demo.gov |
   | Designer | designer@demo.gov |
   | Contractor | contractor@demo.gov |
   | DOT Executive | executive@demo.gov |

   (All demo accounts share the password `RoadwayDemo!2026`, used internally by the
   auto-login/role-switcher — there's no login form to type it into.)

## Running without Docker (local dev)

**Backend** (requires a local PostgreSQL instance and Python 3.12+ — this repo was
authored on Python 3.14, which may lack prebuilt wheels for some packages; if `pip install`
fails, install Python 3.12 alongside it and create the virtualenv with that instead):

```sh
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
alembic upgrade head
python scripts/seed_roles_users.py
python scripts/seed_demo_project.py
python scripts/ingest_open_data.py
uvicorn app.main:app --reload
```

**Frontend**:

```sh
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000`) if the backend runs elsewhere.

## Architecture notes

- **RAG pipeline**: PDF/text extraction → chunking (LangChain text splitters) → OpenAI
  embeddings → ChromaDB (persistent, filtered by project) → grounded chat completion with
  inline citations.
- **LLM provider**: all OpenAI calls go through `app/services/llm_provider.py`, which falls
  back to deterministic stub responses when `OPENAI_API_KEY` is unset — the whole app is
  demoable without a key. The public deployment (`render.yaml`) leaves the key blank on
  purpose, so it always runs in stub mode and can never incur OpenAI cost; every LLM-calling
  endpoint is additionally rate-limited (`app/core/rate_limit.py`, 5/min & 30/hour per IP) as
  defense-in-depth for whenever a real key is enabled.
- **Access model**: no login page. `AuthProvider` (`frontend/lib/auth-context.tsx`) silently
  authenticates every visitor as a demo account on load; the top bar's role picker calls the
  same JWT login endpoint under the hood to switch roles with no password prompt.
- **Open data**: bundled `backend/data/DE25.txt` is a real 2025 National Bridge Inventory
  extract for Delaware (FHWA). FARS crash data and HPMS pavement data are fetched live at
  seed time from NHTSA/USDOT public endpoints, with a graceful skip if those endpoints are
  unreachable from your network.
- **PDF generation**: ReportLab (pure Python, no system dependencies) generates inspection
  reports, design review reports, and executive reports with a consistent DOT-style template.
