from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.employee import Employee
from app.models.location import Location


class AssetAssignment(Base):
    __tablename__ = "asset_assignments"
    __table_args__ = (
        # One open assignment per asset, enforced by the database.
        Index(
            "uq_assignments_one_open_per_asset",
            "asset_id",
            unique=True,
            postgresql_where=text("checkin_at IS NULL"),
        ),
        Index("ix_assignments_asset_checkout", "asset_id", "checkout_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
    department: Mapped[str] = mapped_column(String(120))
    checkout_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    checkin_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    checkout_notes: Mapped[str | None] = mapped_column(Text)
    checkin_notes: Mapped[str | None] = mapped_column(Text)
    checked_out_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    checked_in_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    employee: Mapped[Employee] = relationship()
    location: Mapped[Location] = relationship()
