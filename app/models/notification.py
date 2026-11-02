from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index(
            "uq_notifications_user_dedupe",
            "user_id",
            "dedupe_key",
            unique=True,
            postgresql_where=text("dedupe_key IS NOT NULL"),
        ),
        Index("ix_notifications_user_unread", "user_id", "is_read", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(40))
    message: Mapped[str] = mapped_column(String(500))
    link: Mapped[str | None] = mapped_column(String(300))
    dedupe_key: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_read: Mapped[bool] = mapped_column(default=False, server_default=text("false"))
