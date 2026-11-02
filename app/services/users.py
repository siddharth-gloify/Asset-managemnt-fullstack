from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import MAX_ACTIVE_USERS
from app.core.security import hash_password, verify_password
from app.models import User
from app.schemas.forms import ChangePasswordForm, ProfileForm, UserCreateForm
from app.services import audit
from app.services.common import FormError, NotFound, now_utc


def get_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFound(f"User {user_id} not found")
    return user


def list_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.is_active.desc(), User.name)))


def active_count(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(User).where(User.is_active.is_(True))) or 0


def _email_taken(db: Session, email: str, exclude_id: int | None = None) -> bool:
    stmt = select(User.id).where(func.lower(User.email) == email.lower())
    if exclude_id:
        stmt = stmt.where(User.id != exclude_id)
    return db.scalar(stmt) is not None


def create_user(db: Session, actor: User | None, form: UserCreateForm) -> User:
    if active_count(db) >= MAX_ACTIVE_USERS:
        raise FormError(f"The maximum of {MAX_ACTIVE_USERS} active users has been reached.")
    if _email_taken(db, form.email):
        raise FormError({"email": "A user with this email already exists."})
    user = User(
        name=form.name, email=form.email, password_hash=hash_password(form.password), role="admin"
    )
    db.add(user)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise FormError({"email": "A user with this email already exists."}) from exc
    audit.log(
        db, actor, "User Created", "users", entity_type="user", entity_id=user.id, remarks=user.email
    )
    return user


def deactivate_user(db: Session, actor: User, user_id: int) -> User:
    user = get_user(db, user_id)
    if user.id == actor.id:
        raise FormError("You cannot deactivate your own account.")
    user.is_active = False
    audit.log(
        db, actor, "User Deactivated", "users", entity_type="user", entity_id=user.id,
        remarks=user.email,
    )  # fmt: skip
    return user


def activate_user(db: Session, actor: User, user_id: int) -> User:
    user = get_user(db, user_id)
    if not user.is_active and active_count(db) >= MAX_ACTIVE_USERS:
        raise FormError(f"The maximum of {MAX_ACTIVE_USERS} active users has been reached.")
    user.is_active = True
    audit.log(
        db, actor, "User Activated", "users", entity_type="user", entity_id=user.id,
        remarks=user.email,
    )  # fmt: skip
    return user


def reset_password(db: Session, actor: User, user_id: int, new_password: str) -> User:
    user = get_user(db, user_id)
    user.password_hash = hash_password(new_password)
    audit.log(
        db, actor, "Password Reset", "users", entity_type="user", entity_id=user.id,
        remarks=user.email,
    )  # fmt: skip
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(func.lower(User.email) == email.strip().lower()))
    if user is None or not user.is_active or not verify_password(user.password_hash, password):
        return None
    user.last_login_at = now_utc()
    return user


def update_profile(db: Session, user: User, form: ProfileForm) -> User:
    if _email_taken(db, form.email, exclude_id=user.id):
        raise FormError({"email": "A user with this email already exists."})
    changes = {}
    for name in ("name", "email"):
        new = getattr(form, name)
        if getattr(user, name) != new:
            changes[name] = {"from": getattr(user, name), "to": new}
            setattr(user, name, new)
    if changes:
        audit.log(
            db, user, "Profile Updated", "profile", entity_type="user", entity_id=user.id,
            details={"changes": changes},
        )  # fmt: skip
    return user


def change_password(db: Session, user: User, form: ChangePasswordForm) -> User:
    if not verify_password(user.password_hash, form.current_password):
        raise FormError({"current_password": "Current password is incorrect."})
    user.password_hash = hash_password(form.new_password)
    audit.log(db, user, "Password Changed", "profile", entity_type="user", entity_id=user.id)
    return user
