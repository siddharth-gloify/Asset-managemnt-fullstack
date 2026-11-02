from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import decrypt_field, encrypt_field
from app.models import Asset, AssetAssignment, Employee, User
from app.models.asset import (
    ASSET_STATUSES,
    STATUS_AVAILABLE,
    STATUS_CHECKED_OUT,
    STATUS_LABELS,
    STATUS_MAINTENANCE,
    STATUS_RETIRED,
)
from app.schemas.forms import AssetForm
from app.services import audit
from app.services.common import FormError, NotFound, Page, escape_like, now_utc, paginate
from app.services.notifications import notify
from app.services.photos import process_photo

DIFF_FIELDS = [
    "asset_tag_id", "asset_type", "description", "brand", "model", "serial_number", "os",
    "os_version", "memory", "hard_disk", "processor", "purchase_date", "warranty_expiry",
]  # fmt: skip


def get_asset(db: Session, asset_id: int, for_update: bool = False) -> Asset:
    stmt = select(Asset).where(Asset.id == asset_id, Asset.deleted_at.is_(None))
    if for_update:
        stmt = stmt.with_for_update()
    asset = db.execute(stmt).scalar_one_or_none()
    if asset is None:
        raise NotFound(f"Asset {asset_id} not found")
    return asset


def _active_filter():
    return Asset.deleted_at.is_(None)


def search_assets(
    db: Session, q: str | None = None, status: str | None = None, page: int = 1
) -> Page:
    stmt = select(Asset).where(_active_filter()).order_by(Asset.created_at.desc(), Asset.id.desc())
    if status in ASSET_STATUSES:
        stmt = stmt.where(Asset.status == status)
    if q and q.strip():
        like = f"%{escape_like(q.strip())}%"
        by_employee = (
            select(AssetAssignment.asset_id)
            .join(Employee, Employee.id == AssetAssignment.employee_id)
            .where(AssetAssignment.checkin_at.is_(None), Employee.name.ilike(like, escape="\\"))
        )
        stmt = stmt.where(
            Asset.asset_tag_id.ilike(like, escape="\\")
            | Asset.serial_number.ilike(like, escape="\\")
            | Asset.brand.ilike(like, escape="\\")
            | Asset.model.ilike(like, escape="\\")
            | func.replace(Asset.status, "_", " ").ilike(like, escape="\\")
            | Asset.id.in_(by_employee)
        )
    return paginate(db, stmt, page)


def status_counts(db: Session) -> dict[str, int]:
    rows = db.execute(
        select(Asset.status, func.count()).where(_active_filter()).group_by(Asset.status)
    ).all()
    counts = {s: 0 for s in ASSET_STATUSES}
    counts.update({s: n for s, n in rows})
    counts["all"] = sum(counts[s] for s in ASSET_STATUSES)
    return counts


def last_checkins(db: Session, asset_ids: list[int]) -> dict[int, object]:
    if not asset_ids:
        return {}
    rows = db.execute(
        select(AssetAssignment.asset_id, func.max(AssetAssignment.checkin_at))
        .where(AssetAssignment.asset_id.in_(asset_ids))
        .group_by(AssetAssignment.asset_id)
    ).all()
    return {a: t for a, t in rows}


def current_assignment(db: Session, asset_id: int) -> AssetAssignment | None:
    return db.execute(
        select(AssetAssignment).where(
            AssetAssignment.asset_id == asset_id, AssetAssignment.checkin_at.is_(None)
        )
    ).scalar_one_or_none()


def assignment_history(db: Session, asset_id: int) -> list[AssetAssignment]:
    return list(
        db.scalars(
            select(AssetAssignment)
            .where(AssetAssignment.asset_id == asset_id)
            .order_by(AssetAssignment.checkout_at.desc(), AssetAssignment.id.desc())
        )
    )


def user_names(db: Session, user_ids: set[int]) -> dict[int, str]:
    if not user_ids:
        return {}
    return dict(db.execute(select(User.id, User.name).where(User.id.in_(user_ids))).all())


def distinct_departments(db: Session) -> list[str]:
    asset_depts = select(Asset.department).where(Asset.department.is_not(None))
    assign_depts = select(AssetAssignment.department)
    union = asset_depts.union(assign_depts).subquery()
    return list(db.scalars(select(union.c[0]).where(union.c[0] != "").order_by(union.c[0])))


def _map_integrity(exc: IntegrityError) -> FormError:
    text_ = str(exc.orig).lower()
    if "uq_assets_tag_lower" in text_:
        return FormError({"asset_tag_id": "Asset Tag ID already exists."})
    if "uq_assets_serial_lower" in text_:
        return FormError({"serial_number": "Serial number already exists."})
    if "ck_assets_warranty" in text_:
        return FormError({"warranty_expiry": "Warranty expiry cannot be before the purchase date."})
    return FormError("Could not save the asset because of conflicting data.")


def _check_duplicates(db: Session, form: AssetForm, exclude_id: int | None = None) -> None:
    errors: dict[str, str] = {}
    for column, field_name, message in (
        (Asset.asset_tag_id, "asset_tag_id", "Asset Tag ID already exists."),
        (Asset.serial_number, "serial_number", "Serial number already exists."),
    ):
        stmt = select(Asset.id).where(func.lower(column) == getattr(form, field_name).lower())
        if exclude_id:
            stmt = stmt.where(Asset.id != exclude_id)
        if db.scalar(stmt) is not None:
            errors[field_name] = message
    if errors:
        raise FormError(errors)


def create_asset(
    db: Session, user: User, form: AssetForm, photo: tuple[str, bytes] | None = None
) -> Asset:
    _check_duplicates(db, form)
    asset = Asset(
        **form.model_dump(exclude={"last_password"}),
        last_password_enc=encrypt_field(form.last_password) if form.last_password else None,
    )
    if photo:
        asset.photo_name, asset.photo_mime, asset.photo_data = process_photo(*photo)
    db.add(asset)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise _map_integrity(exc) from exc
    audit.log(
        db, user, "Device Added", "assets", entity_type="asset", entity_id=asset.id,
        asset_id=asset.id, remarks=f"{asset.asset_tag_id} ({asset.brand} {asset.model})",
    )  # fmt: skip
    notify(db, "device_added", f"Device {asset.asset_tag_id} added.", f"/assets?q={asset.asset_tag_id}")
    return asset


def update_asset(
    db: Session, user: User, asset_id: int, form: AssetForm, photo: tuple[str, bytes] | None = None
) -> Asset:
    asset = get_asset(db, asset_id, for_update=True)
    _check_duplicates(db, form, exclude_id=asset.id)
    changes: dict[str, dict] = {}
    for name in DIFF_FIELDS:
        old, new = getattr(asset, name), getattr(form, name)
        if old != new:
            changes[name] = {"from": old, "to": new}
            setattr(asset, name, new)
    if form.last_password:
        asset.last_password_enc = encrypt_field(form.last_password)
        changes["last_password"] = {"from": "***", "to": "*** (changed)"}
    if photo:
        asset.photo_name, asset.photo_mime, asset.photo_data = process_photo(*photo)
        changes["photo"] = {"from": None, "to": "replaced"}
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise _map_integrity(exc) from exc
    if changes:
        audit.log(
            db, user, "Device Updated", "assets", entity_type="asset", entity_id=asset.id,
            asset_id=asset.id, remarks=asset.asset_tag_id, details={"changes": changes},
        )  # fmt: skip
        notify(db, "device_updated", f"Device {asset.asset_tag_id} updated.", f"/assets?q={asset.asset_tag_id}")
    return asset


def toggle_maintenance(db: Session, user: User, asset_id: int) -> Asset:
    asset = get_asset(db, asset_id, for_update=True)
    if asset.status == STATUS_AVAILABLE:
        new = STATUS_MAINTENANCE
    elif asset.status == STATUS_MAINTENANCE:
        new = STATUS_AVAILABLE
    else:
        raise FormError(
            f"Maintenance can only be toggled for available assets (this one is "
            f"{STATUS_LABELS[asset.status].lower()})."
        )
    old, asset.status = asset.status, new
    audit.log(
        db, user, "Device Updated", "assets", entity_type="asset", entity_id=asset.id,
        asset_id=asset.id, remarks=asset.asset_tag_id,
        details={"changes": {"status": {"from": old, "to": new}}},
    )  # fmt: skip
    return asset


def retire_asset(db: Session, user: User, asset_id: int) -> Asset:
    asset = get_asset(db, asset_id, for_update=True)
    if asset.status == STATUS_CHECKED_OUT:
        raise FormError("A checked-out asset cannot be retired. Check it in first.")
    if asset.status == STATUS_RETIRED:
        raise FormError("This asset is already retired.")
    asset.status = STATUS_RETIRED
    audit.log(
        db, user, "Asset Retired", "assets", entity_type="asset", entity_id=asset.id,
        asset_id=asset.id, remarks=asset.asset_tag_id,
    )  # fmt: skip
    notify(db, "device_retired", f"Device {asset.asset_tag_id} retired.", "/assets?status=retired")
    return asset


def delete_asset(db: Session, user: User, asset_id: int) -> Asset:
    asset = get_asset(db, asset_id, for_update=True)
    if asset.status == STATUS_CHECKED_OUT:
        raise FormError("A checked-out asset cannot be deleted. Check it in first.")
    asset.deleted_at = now_utc()
    audit.log(
        db, user, "Asset Deleted", "assets", entity_type="asset", entity_id=asset.id,
        asset_id=asset.id, remarks=asset.asset_tag_id,
    )  # fmt: skip
    notify(db, "device_deleted", f"Device {asset.asset_tag_id} deleted.")
    return asset


def reveal_password(db: Session, user: User, asset_id: int) -> str | None:
    asset = get_asset(db, asset_id)
    if not asset.last_password_enc:
        return None
    audit.log(
        db, user, "Password Revealed", "assets", entity_type="asset", entity_id=asset.id,
        asset_id=asset.id, remarks=f"Last password revealed for {asset.asset_tag_id}",
    )  # fmt: skip
    return decrypt_field(asset.last_password_enc)
