import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.pm import RFI, CostItem, NonConformanceReport, Risk, SafetyIssue, ScheduleItem, Submittal
from app.models.user import User
from app.schemas import pm as schemas

rfi_router = APIRouter(prefix="/api/v1/projects/{project_id}/rfis", tags=["rfis"])
submittal_router = APIRouter(prefix="/api/v1/projects/{project_id}/submittals", tags=["submittals"])
risk_router = APIRouter(prefix="/api/v1/projects/{project_id}/risks", tags=["risks"])
ncr_router = APIRouter(prefix="/api/v1/projects/{project_id}/ncrs", tags=["ncrs"])
safety_router = APIRouter(prefix="/api/v1/projects/{project_id}/safety-issues", tags=["safety"])
schedule_router = APIRouter(prefix="/api/v1/projects/{project_id}/schedule-items", tags=["schedule"])
cost_router = APIRouter(prefix="/api/v1/projects/{project_id}/cost-items", tags=["cost"])


def _make_crud(router: APIRouter, model, create_schema, update_schema, out_schema):
    @router.get("", response_model=list[out_schema])
    def list_items(project_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
        return db.query(model).filter(model.project_id == project_id).order_by(model.created_at.desc()).all()

    @router.post("", response_model=out_schema)
    def create_item(
        project_id: uuid.UUID,
        payload: create_schema,
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
    ):
        item = model(project_id=project_id, **payload.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @router.patch("/{item_id}", response_model=out_schema)
    def update_item(
        project_id: uuid.UUID,
        item_id: uuid.UUID,
        payload: update_schema,
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
    ):
        item = db.get(model, item_id)
        if not item or item.project_id != project_id:
            raise HTTPException(status_code=404, detail="Not found")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        db.commit()
        db.refresh(item)
        return item

    @router.delete("/{item_id}")
    def delete_item(
        project_id: uuid.UUID,
        item_id: uuid.UUID,
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
    ):
        item = db.get(model, item_id)
        if not item or item.project_id != project_id:
            raise HTTPException(status_code=404, detail="Not found")
        db.delete(item)
        db.commit()
        return {"ok": True}


_make_crud(rfi_router, RFI, schemas.RFICreate, schemas.RFIUpdate, schemas.RFIOut)
_make_crud(submittal_router, Submittal, schemas.SubmittalCreate, schemas.SubmittalUpdate, schemas.SubmittalOut)
_make_crud(risk_router, Risk, schemas.RiskCreate, schemas.RiskUpdate, schemas.RiskOut)
_make_crud(ncr_router, NonConformanceReport, schemas.NCRCreate, schemas.NCRUpdate, schemas.NCROut)
_make_crud(safety_router, SafetyIssue, schemas.SafetyIssueCreate, schemas.SafetyIssueUpdate, schemas.SafetyIssueOut)
_make_crud(schedule_router, ScheduleItem, schemas.ScheduleItemCreate, schemas.ScheduleItemUpdate, schemas.ScheduleItemOut)
_make_crud(cost_router, CostItem, schemas.CostItemCreate, schemas.CostItemUpdate, schemas.CostItemOut)

all_pm_routers = [
    rfi_router,
    submittal_router,
    risk_router,
    ncr_router,
    safety_router,
    schedule_router,
    cost_router,
]
