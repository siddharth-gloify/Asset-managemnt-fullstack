from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.deps import current_user
from app.core.htmx import toast
from app.core.templating import render, templates
from app.db import get_db
from app.models import User
from app.services import asset_types as svc
from app.services.common import FormError

router = APIRouter(prefix="/asset-types", tags=["asset-types"])


# --- inline "add new asset type" used from the add/edit device form --------------------------
@router.get("/inline-form", response_class=HTMLResponse)
def inline_form(request: Request, user: User = Depends(current_user)):
    return render(request, "assets/_asset_type_inline_form.html", {"values": {}, "errors": {}})


@router.post("/inline", response_class=HTMLResponse)
async def inline_create(
    request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    data = await request.form()
    label = str(data.get("label") or "")
    try:
        asset_type = svc.create_type(db, user, label)
        db.commit()
        html = templates.get_template("assets/_asset_type_inline_result.html").render(
            request=request, options=svc.type_options(db), selected=asset_type.key
        )
        return toast(HTMLResponse(html), f"Asset type '{asset_type.label}' added.")
    except FormError as exc:
        db.rollback()
        response = render(
            request, "assets/_asset_type_inline_form.html",
            {"values": dict(data), "errors": exc.errors}, status=422,
        )  # fmt: skip
        response.headers["HX-Retarget"] = "#inline-slot"
        response.headers["HX-Reswap"] = "innerHTML"
        return response
