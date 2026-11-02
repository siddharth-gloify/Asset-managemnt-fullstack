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
from app.schemas.forms import CheckoutForm
from app.services import assets as asset_svc
from app.services import assignments as svc
from app.services.common import FormError

router = APIRouter(prefix="/checkout", tags=["checkout"])
log = get_logger("checkout")


@router.get("")
def checkout_list(
    request: Request,
    q: str = "",
    page: int = 1,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    result = asset_svc.search_assets(db, q, "available", page)
    ctx = {
        "page": result,
        "q": q,
        "base_url": "/checkout",
        "active": "checkout",
        "last_checkins": {},
    }
    return render(request, "checkout/_rows.html" if is_htmx(request) else "checkout/list.html", ctx)


def _form_ctx(db, asset, values=None, errors=None):
    return {
        "asset": asset,
        "people": svc.all_people(db),
        "locations": svc.all_locations(db),
        "departments": asset_svc.distinct_departments(db),
        "values": values or {},
        "errors": errors or {},
        "has_password": bool(asset.last_password_enc),
    }


@router.get("/{asset_id:int}/form")
def checkout_form(
    asset_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    asset = asset_svc.get_asset(db, asset_id)
    return render(request, "checkout/_form.html", _form_ctx(db, asset))


@router.post("/{asset_id:int}")
async def checkout_submit(
    asset_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    asset = asset_svc.get_asset(db, asset_id)
    data = await request.form()
    form, errors = validate_form(CheckoutForm, data)
    if form:
        try:
            svc.checkout(db, user, asset_id, form)
            db.commit()
            log.info("checkout", asset_id=asset_id, employee_id=form.employee_id, user_id=user.id)
            return redirect(request, "/checkout", f"{asset.asset_tag_id} checked out.")
        except FormError as exc:
            db.rollback()
            errors = exc.errors
    asset = asset_svc.get_asset(db, asset_id)
    return render(
        request, "checkout/_form.html", _form_ctx(db, asset, dict(data), errors), status=422
    )
