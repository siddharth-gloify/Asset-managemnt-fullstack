"""Read-mostly pages: operations, warranty, notifications, audit trail."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.deps import current_user
from app.core.htmx import redirect
from app.core.templating import render
from app.db import get_db
from app.models import User
from app.services import audit as audit_svc
from app.services import notifications as notif_svc
from app.services import warranty as warranty_svc

operations_router = APIRouter(prefix="/operations", tags=["operations"])
warranty_router = APIRouter(prefix="/warranty", tags=["warranty"])
notifications_router = APIRouter(prefix="/notifications", tags=["notifications"])
audit_router = APIRouter(prefix="/audit", tags=["audit"])


@operations_router.get("")
def operations(request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return render(
        request,
        "operations/list.html",
        {"rows": audit_svc.latest_operations(db), "active": "operations"},
    )


@warranty_router.get("")
def warranty(request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return render(
        request,
        "warranty/list.html",
        {"rows": warranty_svc.nearby_expiry(db), "active": "warranty"},
    )


@notifications_router.get("")
def notifications(
    request: Request,
    page: int = 1,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return render(
        request,
        "notifications/list.html",
        {
            "page": notif_svc.list_for_user(db, user.id, page),
            "labels": notif_svc.TYPE_LABELS,
            "base_url": "/notifications",
            "active": "notifications",
        },
    )


@notifications_router.get("/badge")
def badge(request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return render(
        request, "partials/bell.html", {"unread": notif_svc.unread_count(db, user.id)}
    )


@notifications_router.post("/read-all")
def read_all(request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    notif_svc.mark_all_read(db, user.id)
    db.commit()
    return redirect(request, "/notifications", "All notifications marked as read.")


@notifications_router.post("/{notification_id:int}/read")
def read_one(
    notification_id: int,
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    notif_svc.mark_read(db, user.id, notification_id)
    db.commit()
    return redirect(request, "/notifications")


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return None


@audit_router.get("")
def audit_trail(
    request: Request,
    page: int = 1,
    module: str = "",
    user_id: str = "",
    date_from: str = "",
    date_to: str = "",
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    result = audit_svc.audit_page(
        db,
        page,
        module=module or None,
        user_id=int(user_id) if user_id.isdigit() else None,
        date_from=_parse_date(date_from),
        date_to=_parse_date(date_to),
        tz=get_settings().tz,
    )
    users = db.execute(select(User.id, User.name).order_by(User.name)).all()
    qs = "&".join(
        f"{k}={v}"
        for k, v in (
            ("module", module),
            ("user_id", user_id),
            ("date_from", date_from),
            ("date_to", date_to),
        )
        if v
    )
    return render(
        request,
        "audit/list.html",
        {
            "page": result,
            "modules": audit_svc.MODULES,
            "users": users,
            "filters": {
                "module": module,
                "user_id": user_id,
                "date_from": date_from,
                "date_to": date_to,
            },
            "base_url": "/audit",
            "extra_qs": qs,
            "active": "audit",
        },
    )
