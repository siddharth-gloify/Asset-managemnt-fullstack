from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.deps import current_user
from app.core.htmx import is_htmx, redirect
from app.core.logging import get_logger
from app.core.templating import render
from app.db import get_db
from app.models import Asset, User
from app.schemas.common import validate_form
from app.schemas.forms import AssetForm
from app.services import assets as svc
from app.services.common import FormError

router = APIRouter(prefix="/assets", tags=["assets"])
log = get_logger("assets")

FORM_FIELDS = [
    "asset_tag_id", "asset_type", "description", "status", "brand", "model", "serial_number",
    "os", "os_version", "memory", "hard_disk", "processor", "purchase_date", "warranty_expiry",
]  # fmt: skip


def _values_from_asset(asset: Asset) -> dict:
    values = {name: getattr(asset, name) for name in FORM_FIELDS}
    return {k: ("" if v is None else v) for k, v in values.items()}


async def _read_photo(data) -> tuple[str, bytes] | None:
    upload = data.get("photo")
    if upload is None or not getattr(upload, "filename", ""):
        return None
    content = await upload.read()
    return (upload.filename, content) if content else None


def view_context(db: Session, asset: Asset) -> dict:
    from app.services.assignments import assignment_context

    history = svc.assignment_history(db, asset.id)
    names = svc.user_names(
        db, {h.checked_out_by for h in history if h.checked_out_by}
        | {h.checked_in_by for h in history if h.checked_in_by}
    )  # fmt: skip
    ctx = assignment_context(db, asset)
    last_checkin = svc.last_checkins(db, [asset.id]).get(asset.id)
    return {
        "asset": asset,
        "history": history,
        "user_names": names,
        "last_checkin": last_checkin,
        "has_password": bool(asset.last_password_enc),
        **ctx,
    }


@router.get("")
def list_assets(
    request: Request,
    q: str = "",
    status: str = "",
    page: int = 1,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    result = svc.search_assets(db, q, status or None, page)
    ctx = {
        "page": result,
        "q": q,
        "status": status,
        "last_checkins": svc.last_checkins(db, [a.id for a in result.items]),
        "base_url": "/assets",
        "active": "assets",
    }
    if is_htmx(request):
        return render(request, "assets/_rows.html", ctx)
    ctx["counts"] = svc.status_counts(db)
    return render(request, "assets/list.html", ctx)


def _form_page(request, db, *, asset=None, values=None, errors=None, status=200):
    editing = asset is not None
    return render(
        request,
        "assets/form.html",
        {
            "asset": asset,
            "values": values if values is not None else (_values_from_asset(asset) if asset else {}),
            "errors": errors or {},
            "editing": editing,
            "active": "assets" if editing else "add_device",
        },
        status=status,
    )


@router.get("/new")
def new_form(request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return _form_page(request, db, values={"asset_type": "laptop", "status": "available"})


@router.post("/new")
async def create(
    request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    data = await request.form()
    form, errors = validate_form(AssetForm, data)
    if form:
        try:
            asset = svc.create_asset(db, user, form, await _read_photo(data))
            db.commit()
            log.info("asset_created", asset_id=asset.id, user_id=user.id)
            return redirect(request, "/assets", f"Device {asset.asset_tag_id} added.")
        except FormError as exc:
            db.rollback()
            errors = exc.errors
    return _form_page(request, db, values=dict(data), errors=errors, status=422)


@router.get("/{asset_id:int}/edit")
def edit_form(
    asset_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    return _form_page(request, db, asset=svc.get_asset(db, asset_id))


@router.post("/{asset_id:int}/edit")
async def update(
    asset_id: int,
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    asset = svc.get_asset(db, asset_id)
    data = await request.form()
    # Status changes go through dedicated actions (maintenance/retire/check-out), never this form.
    form, errors = validate_form(AssetForm, {**data, "status": "available"})
    if form:
        try:
            svc.update_asset(db, user, asset_id, form, await _read_photo(data))
            db.commit()
            return redirect(request, "/assets", f"Device {asset.asset_tag_id} updated.")
        except FormError as exc:
            db.rollback()
            errors = exc.errors
    return _form_page(request, db, asset=asset, values=dict(data), errors=errors, status=422)


@router.get("/{asset_id:int}")
def view(
    asset_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    asset = svc.get_asset(db, asset_id)
    return render(request, "assets/_view.html", view_context(db, asset))


def _action(request, db, user, fn, asset_id, success):
    try:
        asset = fn(db, user, asset_id)
        db.commit()
        log.info("asset_action", action=fn.__name__, asset_id=asset_id, user_id=user.id)
        return redirect(request, request.headers.get("hx-current-url") or "/assets", success(asset))
    except FormError as exc:
        db.rollback()
        return redirect(request, "/assets", exc.errors["_"], "error")


@router.post("/{asset_id:int}/retire")
def retire(
    asset_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    return _action(request, db, user, svc.retire_asset, asset_id, lambda a: f"{a.asset_tag_id} retired.")


@router.post("/{asset_id:int}/delete")
def delete(
    asset_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    return _action(request, db, user, svc.delete_asset, asset_id, lambda a: f"{a.asset_tag_id} deleted.")


@router.post("/{asset_id:int}/maintenance")
def maintenance(
    asset_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    return _action(
        request, db, user, svc.toggle_maintenance, asset_id,
        lambda a: f"{a.asset_tag_id} is now {a.status.replace('_', ' ')}.",
    )  # fmt: skip


@router.post("/{asset_id:int}/reveal-password", response_class=HTMLResponse)
def reveal_password(
    asset_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    value = svc.reveal_password(db, user, asset_id)
    db.commit()
    log.info("password_revealed", asset_id=asset_id, user_id=user.id)
    return render(request, "assets/_password.html", {"value": value, "asset_id": asset_id})
