from datetime import date

from sqlalchemy import Date, Enum, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import BridgeConditionEnum
from app.models.mixins import UUIDPKMixin


class Bridge(Base, UUIDPKMixin):
    """Subset of National Bridge Inventory (NBI) fields."""

    __tablename__ = "bridges"

    nbi_structure_number: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    state: Mapped[str] = mapped_column(String(2), default="DE")
    county: Mapped[str] = mapped_column(String(128), nullable=True)
    facility_carried: Mapped[str] = mapped_column(String(255), nullable=True)
    feature_intersected: Mapped[str] = mapped_column(String(255), nullable=True)
    year_built: Mapped[int] = mapped_column(Integer, nullable=True)
    adt: Mapped[int] = mapped_column(Integer, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    deck_condition: Mapped[int] = mapped_column(Integer, nullable=True)
    superstructure_condition: Mapped[int] = mapped_column(Integer, nullable=True)
    substructure_condition: Mapped[int] = mapped_column(Integer, nullable=True)
    structural_evaluation: Mapped[int] = mapped_column(Integer, nullable=True)
    deck_area_sqm: Mapped[float] = mapped_column(Float, nullable=True)
    owner: Mapped[str] = mapped_column(String(255), nullable=True)
    material_type: Mapped[str] = mapped_column(String(128), nullable=True)
    design_type: Mapped[str] = mapped_column(String(128), nullable=True)
    condition: Mapped[BridgeConditionEnum] = mapped_column(
        Enum(BridgeConditionEnum, name="bridge_condition_enum"), default=BridgeConditionEnum.unknown
    )


class CrashRecord(Base, UUIDPKMixin):
    """From NHTSA FARS (Fatality Analysis Reporting System)."""

    __tablename__ = "crash_records"

    state: Mapped[str] = mapped_column(String(2), default="DE")
    county: Mapped[str] = mapped_column(String(128), nullable=True)
    case_year: Mapped[int] = mapped_column(Integer, nullable=True)
    crash_date: Mapped[date] = mapped_column(Date, nullable=True)
    fatalities: Mapped[int] = mapped_column(Integer, default=0)
    route: Mapped[str] = mapped_column(String(255), nullable=True)
    weather: Mapped[str] = mapped_column(String(128), nullable=True)
    light_condition: Mapped[str] = mapped_column(String(128), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)


class PavementSegment(Base, UUIDPKMixin):
    """From FHWA HPMS (Highway Performance Monitoring System), best-effort."""

    __tablename__ = "pavement_segments"

    state: Mapped[str] = mapped_column(String(2), default="DE")
    route: Mapped[str] = mapped_column(String(255), nullable=True)
    county: Mapped[str] = mapped_column(String(128), nullable=True)
    iri: Mapped[float] = mapped_column(Float, nullable=True)
    psr: Mapped[float] = mapped_column(Float, nullable=True)
    surface_type: Mapped[str] = mapped_column(String(128), nullable=True)
    through_lanes: Mapped[int] = mapped_column(Integer, nullable=True)
    aadt: Mapped[int] = mapped_column(Integer, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
