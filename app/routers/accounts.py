"""Profile and user management."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import current_user, require_admin
from app.core.htmx import redirect
from app.core.logging import get_logger
from app.core.templating import render
from app.db import get_db
from app.models import User
from app.schemas.common import validate_form
from app.schemas.forms import ChangePasswordForm, PasswordResetForm, ProfileForm, UserCreateForm
from app.services import users as svc
from app.services.common import FormError

profile_router = APIRouter(prefix="/profile", tags=["profile"])
users_router = APIRouter(prefix="/users", tags=["users"])
log = get_logger("accounts")


# --- profile ---------------------------------------------------------------------------------
@profile_router.get("")
def profile(request: Request, user: User = Depends(current_user)):
    return render(request, "profile/view.html", {"active": "profile"})


@profile_router.get("/edit")
def edit_form(request: Request, user: User = Depends(current_user)):
    return render(
        request,
        "profile/edit.html",
        {"values": {"name": user.name, "email": user.email}, "errors": {}, "active": "profile"},
    )


@profile_router.post("/edit")
async def edit(
    request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    data = await request.form()
    form, errors = validate_form(ProfileForm, data)
    if form:
        try:
            svc.update_profile(db, user, form)
            db.commit()
            return redirect(request, "/profile", "Profile updated.")
        except FormError as exc:
            db.rollback()
            errors = exc.errors
    return render(
        request,
        "profile/edit.html",
        {"values": dict(data), "errors": errors, "active": "profile"},
        status=422,
    )


@profile_router.get("/password")
def password_form(request: Request, user: User = Depends(current_user)):
    return render(request, "profile/password.html", {"errors": {}, "active": "profile"})


@profile_router.post("/password")
async def password(
    request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    data = await request.form()
    form, errors = validate_form(ChangePasswordForm, data)
    if form:
        try:
            svc.change_password(db, user, form)
            db.commit()
            log.info("password_changed", user_id=user.id)
            return redirect(request, "/profile", "Password changed.")
        except FormError as exc:
            db.rollback()
            errors = exc.errors
    return render(
        request, "profile/password.html", {"errors": errors, "active": "profile"}, status=422
    )


# --- users (admin) ---------------------------------------------------------------------------
@users_router.get("")
def list_users(
    request: Request, user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    from app.config import MAX_ACTIVE_USERS

    return render(
        request,
        "users/list.html",
        {
            "users": svc.list_users(db),
            "active_count": svc.active_count(db),
            "max_users": MAX_ACTIVE_USERS,
            "active": "users",
        },
    )


@users_router.get("/new")
def new_form(request: Request, user: User = Depends(require_admin)):
    return render(request, "users/form.html", {"values": {}, "errors": {}, "active": "users"})


@users_router.post("/new")
async def create(
    request: Request, user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    data = await request.form()
    form, errors = validate_form(UserCreateForm, data)
    if form:
        try:
            created = svc.create_user(db, user, form)
            db.commit()
            log.info("user_created", target_user_id=created.id, user_id=user.id)
            return redirect(request, "/users", f"User {created.name} created.")
        except FormError as exc:
            db.rollback()
            errors = exc.errors
    return render(
        request,
        "users/form.html",
        {"values": {k: v for k, v in data.items() if k != "password"}, "errors": errors,
         "active": "users"},
        status=422,
    )  # fmt: skip


def _simple_action(request, db, user, fn, user_id, message):
    try:
        target = fn(db, user, user_id)
        db.commit()
        log.info("user_changed", action=fn.__name__, target_user_id=user_id, user_id=user.id)
        return redirect(request, "/users", message(target))
    except FormError as exc:
        db.rollback()
        return redirect(request, "/users", exc.errors["_"], "error")


@users_router.post("/{user_id:int}/deactivate")
def deactivate(
    user_id: int, request: Request, user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    return _simple_action(
        request, db, user, svc.deactivate_user, user_id, lambda u: f"{u.name} deactivated."
    )


@users_router.post("/{user_id:int}/activate")
def activate(
    user_id: int, request: Request, user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    return _simple_action(
        request, db, user, svc.activate_user, user_id, lambda u: f"{u.name} activated."
    )


@users_router.get("/{user_id:int}/reset-password")
def reset_form(
    user_id: int, request: Request, user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    return render(
        request,
        "users/reset.html",
        {"target": svc.get_user(db, user_id), "errors": {}, "active": "users"},
    )


@users_router.post("/{user_id:int}/reset-password")
async def reset(
    user_id: int, request: Request, user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    target = svc.get_user(db, user_id)
    data = await request.form()
    form, errors = validate_form(PasswordResetForm, data)
    if form:
        svc.reset_password(db, user, user_id, form.password)
        db.commit()
        log.info("password_reset", target_user_id=user_id, user_id=user.id)
        return redirect(request, "/users", f"Password reset for {target.name}.")
    return render(
        request,
        "users/reset.html",
        {"target": target, "errors": errors, "active": "users"},
        status=422,
    )
