from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class AssetType(Base):
    """User-extensible catalogue of asset types (seeded with the original built-in set)."""

    __tablename__ = "asset_types"
    __table_args__ = (Index("uq_asset_types_key_lower", text("lower(key)"), unique=True),)

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(40))
    label: Mapped[str] = mapped_column(String(60))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
