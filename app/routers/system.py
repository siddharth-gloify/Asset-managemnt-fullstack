"""Health check, authenticated media, and the Vercel Cron entrypoint."""

from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.deps import current_user
from app.core.logging import get_logger
from app.db import get_db
from app.models import Asset, User
from app.services.warranty import run_warranty_job

router = APIRouter()
log = get_logger("system")


@router.get("/healthz")
def healthz(db: Session = Depends(get_db)):
    try:
        db.execute(text("select 1"))
    except Exception:
        log.exception("healthcheck_failed")
        return JSONResponse({"status": "error", "db": "down"}, status_code=503)
    return {"status": "ok", "db": "up"}


@router.get("/media/{name}")
def media(name: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    asset = db.execute(
        select(Asset)
        .where(Asset.photo_name == name, Asset.deleted_at.is_(None))
        .execution_options(populate_existing=True)
    ).scalar_one_or_none()
    if asset is None or asset.photo_data is None:
        raise HTTPException(status_code=404, detail="Image not found.")
    return Response(
        asset.photo_data,
        media_type=asset.photo_mime or "application/octet-stream",
        headers={
            "Cache-Control": "private, max-age=86400, immutable",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.get("/internal/cron/warranty")
def cron_warranty(request: Request, db: Session = Depends(get_db)):
    """Called daily by Vercel Cron, which sends `Authorization: Bearer $CRON_SECRET`."""
    secret = get_settings().cron_secret
    supplied = request.headers.get("authorization", "")
    if not secret or not secrets.compare_digest(supplied, f"Bearer {secret}"):
        raise HTTPException(status_code=401, detail="Unauthorized.")
    created = run_warranty_job(db)
    db.commit()
    log.info("warranty_job", notifications_created=created)
    return {"created": created}
