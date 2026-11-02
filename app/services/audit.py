from __future__ import annotations

from datetime import date, datetime
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuditLog, User
from app.services.common import Page, paginate

LATEST_OPERATION_TYPES = [
    "Device Added",
    "Device Updated",
    "Check-In",
    "Check-Out",
    "Person Added",
    "Location Added",
    "Asset Retired",
    "Asset Deleted",
]

MODULES = [
    "assets",
    "checkout",
    "checkin",
    "people",
    "locations",
    "users",
    "auth",
    "profile",
    "warranty",
]


def _jsonable(value: Any):
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def log(
    db: Session,
    user: User | None,
    operation_type: str,
    module: str,
    *,
    entity_type: str | None = None,
    entity_id: int | None = None,
    asset_id: int | None = None,
    employee_id: int | None = None,
    location_id: int | None = None,
    remarks: str | None = None,
    details: dict | None = None,
) -> AuditLog:
    ip = structlog.contextvars.get_contextvars().get("client_ip")
    entry = AuditLog(
        user_id=user.id if user else None,
        operation_type=operation_type,
        module=module,
        entity_type=entity_type,
        entity_id=entity_id,
        asset_id=asset_id,
        employee_id=employee_id,
        location_id=location_id,
        remarks=remarks,
        details=_jsonable(details) if details else None,
        ip=ip,
    )
    db.add(entry)
    db.flush()
    return entry


def latest_operations(db: Session, limit: int = 100):
    from app.models import Asset, Employee, Location

    stmt = (
        select(AuditLog, Asset.asset_tag_id, Employee.name, Location.name, User.name)
        .outerjoin(Asset, Asset.id == AuditLog.asset_id)
        .outerjoin(Employee, Employee.id == AuditLog.employee_id)
        .outerjoin(Location, Location.id == AuditLog.location_id)
        .outerjoin(User, User.id == AuditLog.user_id)
        .where(AuditLog.operation_type.in_(LATEST_OPERATION_TYPES))
        .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
        .limit(limit)
    )
    return db.execute(stmt).all()


def audit_page(
    db: Session,
    page: int,
    module: str | None = None,
    user_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    tz=None,
) -> Page:
    from datetime import time, timedelta

    from app.models import Asset

    stmt = (
        select(AuditLog, User.name, Asset.asset_tag_id)
        .outerjoin(User, User.id == AuditLog.user_id)
        .outerjoin(Asset, Asset.id == AuditLog.asset_id)
        .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
    )
    if module:
        stmt = stmt.where(AuditLog.module == module)
    if user_id:
        stmt = stmt.where(AuditLog.user_id == user_id)
    if date_from:
        stmt = stmt.where(AuditLog.created_at >= datetime.combine(date_from, time.min, tzinfo=tz))
    if date_to:
        stmt = stmt.where(
            AuditLog.created_at < datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=tz)
        )
    return paginate(db, stmt, page, scalars=False)
