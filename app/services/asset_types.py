from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import AssetType, User
from app.services import audit
from app.services.common import FormError

# Seeded once, the first time the asset_types table is empty (fresh install or upgrade).
DEFAULT_TYPES = [
    ("laptop", "Laptop"),
    ("desktop", "Desktop"),
    ("monitor", "Monitor"),
    ("mobile", "Mobile Phone"),
    ("tablet", "Tablet"),
    ("printer", "Printer"),
    ("network", "Network Device"),
]


def seed_defaults(db: Session) -> None:
    if db.scalar(select(AssetType.id)) is not None:
        return
    db.add_all(AssetType(key=key, label=label) for key, label in DEFAULT_TYPES)
    db.flush()


def list_types(db: Session) -> list[AssetType]:
    return list(db.scalars(select(AssetType).order_by(AssetType.label)))


def type_options(db: Session) -> list[tuple[str, str]]:
    return [(t.key, t.label) for t in list_types(db)]


def label_map(db: Session) -> dict[str, str]:
    return {t.key: t.label for t in list_types(db)}


def is_valid_key(db: Session, key: str) -> bool:
    return db.scalar(select(AssetType.id).where(AssetType.key == key)) is not None


def _slugify(label: str) -> str:
    key = re.sub(r"[^a-z0-9]+", "_", label.strip().lower()).strip("_")
    return key[:40] or "type"


def create_type(db: Session, user: User | None, label: str) -> AssetType:
    label = (label or "").strip()
    if not label:
        raise FormError({"label": "Enter a type name."})
    if len(label) > 60:
        raise FormError({"label": "Must be at most 60 characters."})
    key = _slugify(label)
    if is_valid_key(db, key):
        raise FormError({"label": "This asset type already exists."})
    asset_type = AssetType(key=key, label=label)
    db.add(asset_type)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise FormError({"label": "This asset type already exists."}) from exc
    audit.log(
        db, user, "Asset Type Added", "assets", entity_type="asset_type", entity_id=asset_type.id,
        remarks=f"{asset_type.label} ({asset_type.key})",
    )  # fmt: skip
    return asset_type
