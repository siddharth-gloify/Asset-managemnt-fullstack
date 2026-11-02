from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.user import User


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_created_desc", text("created_at DESC")),
        Index("ix_audit_asset", "asset_id"),
        Index("ix_audit_module", "module"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    operation_type: Mapped[str] = mapped_column(String(40))
    module: Mapped[str] = mapped_column(String(40))
    entity_type: Mapped[str | None] = mapped_column(String(40))
    entity_id: Mapped[int | None]
    asset_id: Mapped[int | None] = mapped_column(ForeignKey("assets.id"))
    employee_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"))
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    remarks: Mapped[str | None] = mapped_column(Text)
    details: Mapped[dict | None] = mapped_column(JSONB)
    ip: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User | None] = relationship()
