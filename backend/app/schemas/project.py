import uuid
from datetime import date, datetime

from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: str
    dot_number: str | None = None
    route: str | None = None
    county: str | None = None
    state: str | None = "DE"
    status: str = "active"
    start_date: date | None = None
    end_date: date | None = None
    budget: float = 0
    spent: float = 0
    description: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    status: str | None = None
    budget: float | None = None
    spent: float | None = None
    description: str | None = None


class ProjectOut(ProjectBase):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
