from datetime import date

from sqlalchemy import Date, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Project(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    dot_number: Mapped[str] = mapped_column(String(64), nullable=True)
    route: Mapped[str] = mapped_column(String(64), nullable=True)
    county: Mapped[str] = mapped_column(String(128), nullable=True)
    state: Mapped[str] = mapped_column(String(2), nullable=True, default="DE")
    status: Mapped[str] = mapped_column(String(32), default="active")
    start_date: Mapped[date] = mapped_column(Date, nullable=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=True)
    budget: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    spent: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    description: Mapped[str] = mapped_column(Text, nullable=True)
