from __future__ import annotations

from urllib.parse import quote

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core import deps
from app.core.deps import current_user
from app.core.htmx import redirect
from app.core.logging import get_logger
from app.core.templating import render
from app.db import get_db
from app.models import User
from app.schemas.common import validate_form
from app.schemas.forms import LoginForm
from app.services import audit
from app.services.users import authenticate

router = APIRouter()
log = get_logger("auth")


def _safe_next(value: str | None) -> str:
    if value and value.startswith("/") and not value.startswith("//") and "\\" not in value:
        return value
    return "/assets"


@router.get("/login")
def login_page(request: Request, next: str | None = None, expired: int = 0):
    if request.session.get("user_id"):
        return redirect(request, _safe_next(next))
    return render(request, "auth/login.html", {"next": next or "", "expired": bool(expired)})


@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    data = await request.form()
    next_url = _safe_next(data.get("next"))
    form, errors = validate_form(LoginForm, data)
    user = authenticate(db, form.email, form.password) if form else None
    if user is None:
        email = (data.get("email") or "").strip().lower()
        log.warning("login_failed", email=email)
        audit.log(db, None, "Login Failed", "auth", remarks=email or None)
        db.commit()
        return render(
            request,
            "auth/login.html",
            {"next": data.get("next", ""), "error": "Invalid email or password.", "email": email},
            status=401,
        )
    request.session.clear()
    request.session["user_id"] = user.id
    request.session["last_seen"] = deps._now()
    audit.log(db, user, "Login", "auth", entity_type="user", entity_id=user.id)
    db.commit()
    log.info("login_ok", user_id=user.id)
    return redirect(request, next_url)


@router.post("/logout")
def logout(request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    audit.log(db, user, "Logout", "auth", entity_type="user", entity_id=user.id)
    db.commit()
    log.info("logout", user_id=user.id)
    request.session.clear()
    return redirect(request, "/login")


def login_redirect_url(request: Request, expired: bool) -> str:
    url = "/login"
    params = []
    if request.method == "GET" and request.url.path not in ("/", "/login"):
        path = request.url.path + (f"?{request.url.query}" if request.url.query else "")
        params.append(f"next={quote(path, safe='')}")
    if expired:
        params.append("expired=1")
    return url + ("?" + "&".join(params) if params else "")
