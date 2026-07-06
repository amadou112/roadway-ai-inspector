#!/bin/sh
set -e

alembic upgrade head
python scripts/seed_roles_users.py
python scripts/seed_demo_project.py
python scripts/ingest_open_data.py

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
