from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    LargeBinary,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, deferred, mapped_column, relationship

from app.db import Base
from app.models.location import Location

ASSET_TYPES = ["laptop", "desktop", "monitor", "mobile", "tablet", "printer", "network"]
ASSET_TYPE_LABELS = {
    "laptop": "Laptop",
    "desktop": "Desktop",
    "monitor": "Monitor",
    "mobile": "Mobile Phone",
    "tablet": "Tablet",
    "printer": "Printer",
    "network": "Network Device",
}

STATUS_AVAILABLE = "available"
STATUS_CHECKED_OUT = "checked_out"
STATUS_MAINTENANCE = "under_maintenance"
STATUS_RETIRED = "retired"
ASSET_STATUSES = [STATUS_AVAILABLE, STATUS_CHECKED_OUT, STATUS_MAINTENANCE, STATUS_RETIRED]
STATUS_LABELS = {
    STATUS_AVAILABLE: "Available",
    STATUS_CHECKED_OUT: "Checked Out",
    STATUS_MAINTENANCE: "Under Maintenance",
    STATUS_RETIRED: "Retired",
}


class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = (
        Index("uq_assets_tag_lower", text("lower(asset_tag_id)"), unique=True),
        Index("uq_assets_serial_lower", text("lower(serial_number)"), unique=True),
        Index("ix_assets_status", "status"),
        Index("ix_assets_brand_lower", text("lower(brand)")),
        Index("ix_assets_model_lower", text("lower(model)")),
        Index("ix_assets_warranty_expiry", "warranty_expiry"),
        CheckConstraint("warranty_expiry >= purchase_date", name="ck_assets_warranty_after_purchase"),
        CheckConstraint(
            "status in ('available','checked_out','under_maintenance','retired')",
            name="ck_assets_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_tag_id: Mapped[str] = mapped_column(String(60))
    asset_type: Mapped[str] = mapped_column(String(20), default="laptop", server_default="laptop")
    description: Mapped[str] = mapped_column(String(300))
    status: Mapped[str] = mapped_column(String(20), default=STATUS_AVAILABLE)
    brand: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(100))
    serial_number: Mapped[str] = mapped_column(String(100))
    os: Mapped[str | None] = mapped_column(String(100))
    os_version: Mapped[str | None] = mapped_column(String(100))
    memory: Mapped[str | None] = mapped_column(String(60))
    hard_disk: Mapped[str | None] = mapped_column(String(60))
    processor: Mapped[str | None] = mapped_column(String(120))
    purchase_date: Mapped[date] = mapped_column(Date)
    warranty_expiry: Mapped[date] = mapped_column(Date)
    photo_name: Mapped[str | None] = mapped_column(String(80))
    photo_mime: Mapped[str | None] = mapped_column(String(30))
    photo_data: Mapped[bytes | None] = deferred(mapped_column(LargeBinary))
    last_password_enc: Mapped[str | None] = mapped_column(Text)
    last_used_by: Mapped[str | None] = mapped_column(String(120))
    department: Mapped[str | None] = mapped_column(String(120))
    current_location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    current_location: Mapped[Location | None] = relationship()
