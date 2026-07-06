import uuid

from pydantic import BaseModel

from app.models.enums import BridgeConditionEnum


class BridgeOut(BaseModel):
    id: uuid.UUID
    nbi_structure_number: str
    state: str
    county: str | None
    facility_carried: str | None
    feature_intersected: str | None
    year_built: int | None
    adt: int | None
    latitude: float | None
    longitude: float | None
    deck_condition: int | None
    superstructure_condition: int | None
    substructure_condition: int | None
    structural_evaluation: int | None
    owner: str | None
    material_type: str | None
    design_type: str | None
    condition: BridgeConditionEnum

    model_config = {"from_attributes": True}


class CrashRecordOut(BaseModel):
    id: uuid.UUID
    state: str
    county: str | None
    case_year: int | None
    fatalities: int
    route: str | None
    latitude: float | None
    longitude: float | None

    model_config = {"from_attributes": True}


class PavementSegmentOut(BaseModel):
    id: uuid.UUID
    state: str
    route: str | None
    county: str | None
    iri: float | None
    psr: float | None
    surface_type: str | None
    aadt: int | None
    latitude: float | None
    longitude: float | None

    model_config = {"from_attributes": True}


class BridgeDashboardSummary(BaseModel):
    total_bridges: int
    good_count: int
    fair_count: int
    poor_count: int
    unknown_count: int
    average_year_built: float | None
    total_crashes: int
    total_fatalities: int
    average_iri: float | None
    counties: list[str]
