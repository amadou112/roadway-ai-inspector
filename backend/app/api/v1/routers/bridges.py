from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.enums import BridgeConditionEnum
from app.models.opendata import Bridge, CrashRecord, PavementSegment
from app.models.user import User
from app.schemas.opendata import (
    BridgeDashboardSummary,
    BridgeOut,
    CrashRecordOut,
    PavementSegmentOut,
)

router = APIRouter(prefix="/api/v1/open-data", tags=["open-data"])


@router.get("/bridges", response_model=list[BridgeOut])
def list_bridges(county: str | None = None, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    query = db.query(Bridge)
    if county:
        query = query.filter(Bridge.county == county)
    return query.all()


@router.get("/crashes", response_model=list[CrashRecordOut])
def list_crashes(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(CrashRecord).all()


@router.get("/pavement", response_model=list[PavementSegmentOut])
def list_pavement(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(PavementSegment).all()


@router.get("/summary", response_model=BridgeDashboardSummary)
def summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    condition_counts = dict(db.query(Bridge.condition, func.count(Bridge.id)).group_by(Bridge.condition).all())
    avg_year = db.query(func.avg(Bridge.year_built)).scalar()
    total_crashes = db.query(func.count(CrashRecord.id)).scalar() or 0
    total_fatalities = db.query(func.coalesce(func.sum(CrashRecord.fatalities), 0)).scalar() or 0
    avg_iri = db.query(func.avg(PavementSegment.iri)).scalar()
    counties = [c[0] for c in db.query(Bridge.county).distinct().all() if c[0]]

    return BridgeDashboardSummary(
        total_bridges=sum(condition_counts.values()),
        good_count=condition_counts.get(BridgeConditionEnum.good, 0),
        fair_count=condition_counts.get(BridgeConditionEnum.fair, 0),
        poor_count=condition_counts.get(BridgeConditionEnum.poor, 0),
        unknown_count=condition_counts.get(BridgeConditionEnum.unknown, 0),
        average_year_built=float(avg_year) if avg_year else None,
        total_crashes=total_crashes,
        total_fatalities=int(total_fatalities),
        average_iri=float(avg_iri) if avg_iri else None,
        counties=counties,
    )
