from __future__ import annotations

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import Notification, User
from app.services.common import Page, paginate

TYPE_LABELS = {
    "device_added": "Device Added",
    "device_updated": "Device Updated",
    "device_retired": "Device Retired",
    "device_deleted": "Device Deleted",
    "device_checked_out": "Device Checked Out",
    "warranty_expiring": "Warranty Expiring",
    "warranty_expired": "Warranty Expired",
    "employee_added": "New Employee",
    "location_added": "New Location",
}


def notify(
    db: Session,
    type_: str,
    message: str,
    link: str | None = None,
    dedupe_key: str | None = None,
) -> int:
    """Fan one notification out to every active user. Returns rows created.

    With a dedupe_key the (user_id, dedupe_key) unique index makes this idempotent.
    """
    user_ids = db.scalars(select(User.id).where(User.is_active.is_(True))).all()
    if not user_ids:
        return 0
    rows = [
        {"user_id": uid, "type": type_, "message": message, "link": link, "dedupe_key": dedupe_key}
        for uid in user_ids
    ]
    result = db.execute(
        insert(Notification).values(rows).on_conflict_do_nothing().returning(Notification.id)
    )
    return len(result.all())


def unread_count(db: Session, user_id: int) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        )
        or 0
    )


def list_for_user(db: Session, user_id: int, page: int) -> Page:
    stmt = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
    )
    return paginate(db, stmt, page)


def mark_read(db: Session, user_id: int, notification_id: int) -> None:
    db.execute(
        update(Notification)
        .where(Notification.id == notification_id, Notification.user_id == user_id)
        .values(is_read=True)
    )


def mark_all_read(db: Session, user_id: int) -> None:
    db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
