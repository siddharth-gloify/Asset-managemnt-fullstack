from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.deps import current_user
from app.core.htmx import is_htmx, redirect, toast
from app.core.logging import get_logger
from app.core.templating import render, templates
from app.db import get_db
from app.models import User
from app.schemas.common import validate_form
from app.schemas.forms import LocationForm
from app.services import assignments as assign_svc
from app.services import locations as svc
from app.services.common import FormError

router = APIRouter(prefix="/locations", tags=["locations"])
log = get_logger("locations")

FIELDS = ["name", "floor", "building_name", "area", "pincode", "district", "state"]


def _form_page(request, *, location=None, values=None, errors=None, status=200):
    if values is None:
        values = {f: getattr(location, f) for f in FIELDS} if location else {}
    return render(
        request,
        "locations/form.html",
        {
            "location": location,
            "values": values,
            "errors": errors or {},
            "active": "add_location" if location is None else "locations",
        },
        status=status,
    )


@router.get("")
def list_locations(
    request: Request,
    q: str = "",
    page: int = 1,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    ctx = {
        "page": svc.search_locations(db, q, page),
        "q": q,
        "base_url": "/locations",
        "active": "locations",
    }
    return render(
        request, "locations/_rows.html" if is_htmx(request) else "locations/list.html", ctx
    )


@router.get("/new")
def new_form(request: Request, user: User = Depends(current_user)):
    return _form_page(request)


@router.post("/new")
async def create(
    request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    data = await request.form()
    form, errors = validate_form(LocationForm, data)
    if form:
        try:
            location = svc.create_location(db, user, form)
            db.commit()
            log.info("location_created", location_id=location.id, user_id=user.id)
            return redirect(request, "/locations", f"{location.name} added.")
        except FormError as exc:
            db.rollback()
            errors = exc.errors
    return _form_page(request, values=dict(data), errors=errors, status=422)


@router.get("/{location_id:int}/edit")
def edit_form(
    location_id: int,
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return _form_page(request, location=svc.get_location(db, location_id))


@router.post("/{location_id:int}/edit")
async def update(
    location_id: int,
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    location = svc.get_location(db, location_id)
    data = await request.form()
    form, errors = validate_form(LocationForm, data)
    if form:
        try:
            svc.update_location(db, user, location_id, form)
            db.commit()
            return redirect(request, "/locations", f"{form.name} updated.")
        except FormError as exc:
            db.rollback()
            errors = exc.errors
    return _form_page(request, location=location, values=dict(data), errors=errors, status=422)


# --- inline "add new location" used from the check-out popup ---------------------------------
@router.get("/inline-form", response_class=HTMLResponse)
def inline_form(request: Request, user: User = Depends(current_user)):
    return render(request, "locations/_inline_form.html", {"values": {}, "errors": {}})


@router.post("/inline", response_class=HTMLResponse)
async def inline_create(
    request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    data = await request.form()
    form, errors = validate_form(LocationForm, data)
    if form:
        try:
            location = svc.create_location(db, user, form)
            db.commit()
            html = templates.get_template("locations/_inline_result.html").render(
                request=request, locations=assign_svc.all_locations(db), selected=location.id
            )
            return toast(HTMLResponse(html), f"{location.name} added.")
        except FormError as exc:
            db.rollback()
            errors = exc.errors
    response = render(
        request, "locations/_inline_form.html", {"values": dict(data), "errors": errors}, status=422
    )
    response.headers["HX-Retarget"] = "#inline-slot"
    response.headers["HX-Reswap"] = "innerHTML"
    return response
