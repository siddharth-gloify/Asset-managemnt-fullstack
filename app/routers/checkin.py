from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import current_user
from app.core.htmx import is_htmx, redirect
from app.core.logging import get_logger
from app.core.templating import render
from app.db import get_db
from app.models import User
from app.schemas.common import validate_form
from app.schemas.forms import CheckinForm
from app.services import assets as asset_svc
from app.services import assignments as svc
from app.services.common import FormError

router = APIRouter(prefix="/checkin", tags=["checkin"])
log = get_logger("checkin")


@router.get("")
def checkin_list(
    request: Request,
    q: str = "",
    page: int = 1,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    result = asset_svc.search_assets(db, q, "checked_out", page)
    ctx = {
        "page": result,
        "q": q,
        "base_url": "/checkin",
        "active": "checkin",
        "last_checkins": {},
    }
    return render(request, "checkin/_rows.html" if is_htmx(request) else "checkin/list.html", ctx)


def _form_ctx(db, asset, values=None, errors=None):
    return {
        "asset": asset,
        "values": values or {},
        "errors": errors or {},
        "has_password": bool(asset.last_password_enc),
        **svc.assignment_context(db, asset),
    }


@router.get("/{asset_id:int}/form")
def checkin_form(
    asset_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    asset = asset_svc.get_asset(db, asset_id)
    return render(request, "checkin/_form.html", _form_ctx(db, asset))


@router.post("/{asset_id:int}")
async def checkin_submit(
    asset_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    asset = asset_svc.get_asset(db, asset_id)
    data = await request.form()
    form, errors = validate_form(CheckinForm, data)
    if form:
        try:
            svc.checkin(db, user, asset_id, form)
            db.commit()
            log.info("checkin", asset_id=asset_id, user_id=user.id)
            return redirect(request, "/checkin", f"{asset.asset_tag_id} checked in.")
        except FormError as exc:
            db.rollback()
            errors = exc.errors
    asset = asset_svc.get_asset(db, asset_id)
    return render(
        request, "checkin/_form.html", _form_ctx(db, asset, dict(data), errors), status=422
    )
