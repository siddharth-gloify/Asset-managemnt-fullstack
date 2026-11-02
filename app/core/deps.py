from __future__ import annotations

import time

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.models import User

_now = time.time  # patched in tests


class NotAuthenticated(Exception):
    def __init__(self, expired: bool = False):
        self.expired = expired


def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    session = request.session
    user_id = session.get("user_id")
    if not user_id:
        raise NotAuthenticated()
    now = _now()
    last_seen = session.get("last_seen") or 0
    if now - last_seen > get_settings().session_idle_minutes * 60:
        session.clear()
        raise NotAuthenticated(expired=True)
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        session.clear()
        raise NotAuthenticated()
    session["last_seen"] = now  # sliding timeout
    request.state.user = user
    request.state.user_id = user.id
    return user


def require_admin(user: User = Depends(current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required.")
    return user
