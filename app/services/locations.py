from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Location, User
from app.schemas.forms import LocationForm
from app.services import audit
from app.services.common import FormError, NotFound, Page, escape_like, paginate
from app.services.notifications import notify


def get_location(db: Session, location_id: int) -> Location:
    location = db.get(Location, location_id)
    if location is None:
        raise NotFound(f"Location {location_id} not found")
    return location


def _check_name(db: Session, name: str, exclude_id: int | None = None) -> None:
    stmt = select(Location.id).where(func.lower(Location.name) == name.lower())
    if exclude_id:
        stmt = stmt.where(Location.id != exclude_id)
    if db.scalar(stmt) is not None:
        raise FormError({"name": "A location with this name already exists."})


def create_location(db: Session, user: User, form: LocationForm) -> Location:
    _check_name(db, form.name)
    location = Location(**form.model_dump())
    db.add(location)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise FormError({"name": "A location with this name already exists."}) from exc
    audit.log(
        db, user, "Location Added", "locations", entity_type="location", entity_id=location.id,
        location_id=location.id, remarks=location.name,
    )  # fmt: skip
    notify(db, "location_added", f"New location {location.name} added.", "/locations")
    return location


def update_location(db: Session, user: User, location_id: int, form: LocationForm) -> Location:
    location = get_location(db, location_id)
    _check_name(db, form.name, exclude_id=location.id)
    changes = {}
    for name, new in form.model_dump().items():
        old = getattr(location, name)
        if old != new:
            changes[name] = {"from": old, "to": new}
            setattr(location, name, new)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise FormError({"name": "A location with this name already exists."}) from exc
    if changes:
        audit.log(
            db, user, "Location Updated", "locations", entity_type="location",
            entity_id=location.id, location_id=location.id, remarks=location.name,
            details={"changes": changes},
        )  # fmt: skip
    return location


def search_locations(db: Session, q: str | None, page: int) -> Page:
    stmt = select(Location).order_by(Location.name)
    if q and q.strip():
        like = f"%{escape_like(q.strip())}%"
        stmt = stmt.where(
            Location.name.ilike(like, escape="\\")
            | Location.building_name.ilike(like, escape="\\")
            | Location.area.ilike(like, escape="\\")
            | Location.district.ilike(like, escape="\\")
        )
    return paginate(db, stmt, page)
