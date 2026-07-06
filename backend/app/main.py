from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import (
    assistant,
    auth,
    bridges,
    design_review,
    documents,
    inspections,
    pm,
    projects,
    reports,
    users,
)
from app.api.v1.routers.dashboards import router as dashboards_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(documents.router)
app.include_router(assistant.router)
app.include_router(inspections.router)
app.include_router(design_review.router)
app.include_router(dashboards_router)
app.include_router(bridges.router)
app.include_router(reports.router)
for r in pm.all_pm_routers:
    app.include_router(r)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}
