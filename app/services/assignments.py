from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Asset, AssetAssignment, Employee, Location, User
from app.models.asset import STATUS_AVAILABLE, STATUS_CHECKED_OUT
from app.schemas.forms import CheckinForm, CheckoutForm
from app.services import audit
from app.services.assets import current_assignment, get_asset
from app.services.common import FormError, now_utc
from app.services.notifications import notify


def checkout(db: Session, user: User, asset_id: int, form: CheckoutForm) -> AssetAssignment:
    # Row lock serialises concurrent check-outs of the same asset; the partial unique index
    # on open assignments is the database-level backstop.
    asset = get_asset(db, asset_id, for_update=True)
    if asset.status != STATUS_AVAILABLE:
        raise FormError("This asset is no longer available for check-out.")
    employee = db.get(Employee, form.employee_id)
    location = db.get(Location, form.location_id)
    errors = {}
    if employee is None or not employee.is_active:
        errors["employee_id"] = "Select a valid person."
    if location is None:
        errors["location_id"] = "Select a valid location."
    if errors:
        raise FormError(errors)

    assignment = AssetAssignment(
        asset_id=asset.id,
        employee_id=employee.id,
        location_id=location.id,
        department=form.department,
        checkout_at=now_utc(),
        checkout_notes=form.notes,
        checked_out_by=user.id,
    )
    asset.status = STATUS_CHECKED_OUT
    asset.department = form.department
    asset.current_location_id = location.id
    db.add(assignment)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise FormError("This asset already has an open assignment.") from exc
    audit.log(
        db, user, "Check-Out", "checkout", entity_type="asset", entity_id=asset.id,
        asset_id=asset.id, employee_id=employee.id, location_id=location.id,
        remarks=form.notes or f"Checked out to {employee.name}",
        details={"department": form.department, "assignment_id": assignment.id},
    )  # fmt: skip
    notify(
        db, "device_checked_out", f"{asset.asset_tag_id} checked out to {employee.name}.",
        f"/assets?q={asset.asset_tag_id}",
    )  # fmt: skip
    return assignment


def checkin(db: Session, user: User, asset_id: int, form: CheckinForm) -> AssetAssignment:
    asset = get_asset(db, asset_id, for_update=True)
    if asset.status != STATUS_CHECKED_OUT:
        raise FormError("Only checked-out assets can be checked in.")
    assignment = current_assignment(db, asset.id)
    if assignment is None:
        raise FormError("No open assignment was found for this asset.")
    employee = db.get(Employee, assignment.employee_id)
    assignment.checkin_at = now_utc()
    assignment.checkin_notes = form.notes
    assignment.checked_in_by = user.id
    asset.status = STATUS_AVAILABLE
    asset.last_used_by = employee.name
    asset.department = None
    db.flush()
    audit.log(
        db, user, "Check-In", "checkin", entity_type="asset", entity_id=asset.id,
        asset_id=asset.id, employee_id=employee.id, location_id=assignment.location_id,
        remarks=form.notes or f"Returned by {employee.name}",
        details={"assignment_id": assignment.id},
    )  # fmt: skip
    return assignment


def assignment_context(db: Session, asset: Asset) -> dict:
    assignment = current_assignment(db, asset.id)
    return {
        "assignment": assignment,
        "employee": assignment.employee if assignment else None,
        "location": assignment.location if assignment else None,
    }


def all_people(db: Session) -> list[Employee]:
    return list(
        db.scalars(select(Employee).where(Employee.is_active.is_(True)).order_by(Employee.name))
    )


def all_locations(db: Session) -> list[Location]:
    return list(db.scalars(select(Location).order_by(Location.name)))
