from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.location import Location


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        Index("uq_employees_code_lower", text("lower(employee_code)"), unique=True),
        Index("ix_employees_name_lower", text("lower(name)")),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_code: Mapped[str] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(120))
    mobile: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(Text)
    pincode: Mapped[str] = mapped_column(String(12))
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
    is_active: Mapped[bool] = mapped_column(default=True, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    location: Mapped[Location] = relationship()
