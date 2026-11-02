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
from app.schemas.forms import PersonForm
from app.services import assignments as assign_svc
from app.services import people as svc
from app.services.common import FormError

router = APIRouter(prefix="/people", tags=["people"])
log = get_logger("people")

FIELDS = ["name", "employee_code", "mobile", "email", "address", "pincode", "location_id"]


def _form_page(request, db, *, person=None, values=None, errors=None, status=200):
    if values is None:
        values = {f: getattr(person, f) for f in FIELDS} if person else {}
    return render(
        request,
        "people/form.html",
        {
            "person": person,
            "values": values,
            "errors": errors or {},
            "locations": assign_svc.all_locations(db),
            "active": "add_people" if person is None else "people",
        },
        status=status,
    )


@router.get("")
def list_people(
    request: Request,
    q: str = "",
    page: int = 1,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    ctx = {
        "page": svc.search_people(db, q, page),
        "q": q,
        "base_url": "/people",
        "active": "people",
    }
    return render(request, "people/_rows.html" if is_htmx(request) else "people/list.html", ctx)


@router.get("/new")
def new_form(request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return _form_page(request, db)


@router.post("/new")
async def create(
    request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    data = await request.form()
    form, errors = validate_form(PersonForm, data)
    if form:
        try:
            person = svc.create_person(db, user, form)
            db.commit()
            log.info("person_created", person_id=person.id, user_id=user.id)
            return redirect(request, "/people", f"{person.name} added.")
        except FormError as exc:
            db.rollback()
            errors = exc.errors
    return _form_page(request, db, values=dict(data), errors=errors, status=422)


@router.get("/{person_id:int}/edit")
def edit_form(
    person_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    return _form_page(request, db, person=svc.get_person(db, person_id))


@router.post("/{person_id:int}/edit")
async def update(
    person_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    person = svc.get_person(db, person_id)
    data = await request.form()
    form, errors = validate_form(PersonForm, data)
    if form:
        try:
            svc.update_person(db, user, person_id, form)
            db.commit()
            return redirect(request, "/people", f"{form.name} updated.")
        except FormError as exc:
            db.rollback()
            errors = exc.errors
    return _form_page(request, db, person=person, values=dict(data), errors=errors, status=422)


# --- inline "add new person" used from the check-out popup -----------------------------------
@router.get("/inline-form", response_class=HTMLResponse)
def inline_form(request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return render(
        request,
        "people/_inline_form.html",
        {"values": {}, "errors": {}, "locations": assign_svc.all_locations(db)},
    )


@router.post("/inline", response_class=HTMLResponse)
async def inline_create(
    request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    data = await request.form()
    form, errors = validate_form(PersonForm, data)
    if form:
        try:
            person = svc.create_person(db, user, form)
            db.commit()
            html = templates.get_template("people/_inline_result.html").render(
                request=request, people=assign_svc.all_people(db), selected=person.id
            )
            response = HTMLResponse(html)
            return toast(response, f"{person.name} added.")
        except FormError as exc:
            db.rollback()
            errors = exc.errors
    response = render(
        request,
        "people/_inline_form.html",
        {"values": dict(data), "errors": errors, "locations": assign_svc.all_locations(db)},
        status=422,
    )
    return hx_trigger_retarget(response)


def hx_trigger_retarget(response):
    response.headers["HX-Retarget"] = "#inline-slot"
    response.headers["HX-Reswap"] = "innerHTML"
    return response
