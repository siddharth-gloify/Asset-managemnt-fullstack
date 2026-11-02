from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Employee, Location, User
from app.schemas.forms import PersonForm
from app.services import audit
from app.services.common import FormError, NotFound, Page, escape_like, paginate
from app.services.notifications import notify


def get_person(db: Session, person_id: int) -> Employee:
    person = db.get(Employee, person_id)
    if person is None:
        raise NotFound(f"Person {person_id} not found")
    return person


def _validate(db: Session, form: PersonForm, exclude_id: int | None = None) -> None:
    errors: dict[str, str] = {}
    stmt = select(Employee.id).where(func.lower(Employee.employee_code) == form.employee_code.lower())
    if exclude_id:
        stmt = stmt.where(Employee.id != exclude_id)
    if db.scalar(stmt) is not None:
        errors["employee_code"] = "Employee ID already exists."
    if db.get(Location, form.location_id) is None:
        errors["location_id"] = "Select a valid location."
    if errors:
        raise FormError(errors)


def create_person(db: Session, user: User, form: PersonForm) -> Employee:
    _validate(db, form)
    person = Employee(**form.model_dump())
    db.add(person)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise FormError({"employee_code": "Employee ID already exists."}) from exc
    audit.log(
        db, user, "Person Added", "people", entity_type="employee", entity_id=person.id,
        employee_id=person.id, location_id=person.location_id,
        remarks=f"{person.name} ({person.employee_code})",
    )  # fmt: skip
    notify(db, "employee_added", f"New employee {person.name} added.", "/people")
    return person


def update_person(db: Session, user: User, person_id: int, form: PersonForm) -> Employee:
    person = get_person(db, person_id)
    _validate(db, form, exclude_id=person.id)
    changes = {}
    for name, new in form.model_dump().items():
        old = getattr(person, name)
        if old != new:
            changes[name] = {"from": old, "to": new}
            setattr(person, name, new)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise FormError({"employee_code": "Employee ID already exists."}) from exc
    if changes:
        audit.log(
            db, user, "Person Updated", "people", entity_type="employee", entity_id=person.id,
            employee_id=person.id, remarks=person.name, details={"changes": changes},
        )  # fmt: skip
    return person


def search_people(db: Session, q: str | None, page: int) -> Page:
    stmt = select(Employee).order_by(Employee.name)
    if q and q.strip():
        like = f"%{escape_like(q.strip())}%"
        stmt = stmt.where(
            Employee.name.ilike(like, escape="\\")
            | Employee.employee_code.ilike(like, escape="\\")
            | Employee.email.ilike(like, escape="\\")
            | Employee.mobile.ilike(like, escape="\\")
        )
    return paginate(db, stmt, page)
