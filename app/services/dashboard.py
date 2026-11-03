from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Asset, AssetAssignment, Employee, Location
from app.models.asset import ASSET_STATUSES, ASSET_TYPE_LABELS
from app.services import assets as asset_svc
from app.services import audit as audit_svc
from app.services import warranty as warranty_svc

TREND_DAYS = 14


def _daily_counts(db: Session, column, start: datetime, tz) -> dict:
    day = func.date(func.timezone(get_settings().app_timezone, column))
    rows = db.execute(select(day, func.count()).where(column >= start).group_by(day)).all()
    return {str(d): n for d, n in rows}


def build_dashboard(db: Session) -> dict:
    tz = get_settings().tz
    counts = asset_svc.status_counts(db)

    by_type = dict(
        db.execute(
            select(Asset.asset_type, func.count())
            .where(Asset.deleted_at.is_(None))
            .group_by(Asset.asset_type)
        ).all()
    )

    today = datetime.now(tz).date()
    days = [today - timedelta(days=i) for i in range(TREND_DAYS - 1, -1, -1)]
    start = datetime.combine(days[0], datetime.min.time(), tzinfo=tz)
    out = _daily_counts(db, AssetAssignment.checkout_at, start, tz)
    back = _daily_counts(db, AssetAssignment.checkin_at, start, tz)

    expiring = warranty_svc.nearby_expiry(db)

    return {
        "counts": counts,
        "people": db.scalar(select(func.count()).select_from(Employee)) or 0,
        "locations": db.scalar(select(func.count()).select_from(Location)) or 0,
        "expiring": expiring[:6],
        "expiring_count": len(expiring),
        "recent": audit_svc.latest_operations(db, 8),
        "chart": {
            "status": {
                "labels": [s.replace("_", " ").title() for s in ASSET_STATUSES],
                "slugs": ASSET_STATUSES,
                "series": [counts[s] for s in ASSET_STATUSES],
            },
            "types": {
                "labels": [ASSET_TYPE_LABELS.get(t, t) for t in by_type],
                "series": list(by_type.values()),
            },
            "trend": {
                "labels": [d.strftime("%d %b") for d in days],
                "checkouts": [out.get(d.isoformat(), 0) for d in days],
                "checkins": [back.get(d.isoformat(), 0) for d in days],
            },
        },
    }

