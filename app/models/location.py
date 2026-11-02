from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Location(Base):
    __tablename__ = "locations"
    __table_args__ = (Index("uq_locations_name_lower", text("lower(name)"), unique=True),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    floor: Mapped[str] = mapped_column(String(40))
    building_name: Mapped[str] = mapped_column(String(160))
    area: Mapped[str] = mapped_column(String(160))
    district: Mapped[str] = mapped_column(String(120))
    state: Mapped[str] = mapped_column(String(120))
    pincode: Mapped[str] = mapped_column(String(12))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
