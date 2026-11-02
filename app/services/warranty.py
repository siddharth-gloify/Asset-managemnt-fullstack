from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Asset
from app.models.asset import STATUS_RETIRED
from app.services.notifications import notify

NEARBY_DAYS = 90
RECENTLY_EXPIRED_DAYS = 30


def today_local() -> date:
    return datetime.now(get_settings().tz).date()


def nearby_expiry(db: Session, today: date | None = None) -> list[tuple[Asset, int]]:
    """Assets whose warranty ends within 90 days (plus those that lapsed in the last 30 days)."""
    today = today or today_local()
    assets = db.scalars(
        select(Asset)
        .where(
            Asset.deleted_at.is_(None),
            Asset.status != STATUS_RETIRED,
            Asset.warranty_expiry <= today + timedelta(days=NEARBY_DAYS),
            Asset.warranty_expiry >= today - timedelta(days=RECENTLY_EXPIRED_DAYS),
        )
        .order_by(Asset.warranty_expiry.asc(), Asset.id.asc())
    ).all()
    return [(a, (a.warranty_expiry - today).days) for a in assets]


def run_warranty_job(db: Session, today: date | None = None) -> int:
    """Create warranty notifications; safe to run repeatedly (deduped per user, asset, bucket).

    Buckets: 11-30 days before expiry, 0-10 days before expiry, and 7-14 days after expiry. Using
    ranges rather than exact days means a missed run still catches up, and dedupe keys stop repeats.
    """
    today = today or today_local()
    created = 0
    assets = db.scalars(
        select(Asset).where(
            Asset.deleted_at.is_(None),
            Asset.status != STATUS_RETIRED,
            Asset.warranty_expiry <= today + timedelta(days=30),
            Asset.warranty_expiry >= today - timedelta(days=14),
        )
    ).all()
    for asset in assets:
        days = (asset.warranty_expiry - today).days
        if 10 < days <= 30:
            bucket, kind = "30", "warranty_expiring"
            msg = f"Warranty for {asset.asset_tag_id} expires in {days} days."
        elif 0 <= days <= 10:
            bucket, kind = "10", "warranty_expiring"
            msg = (
                f"Warranty for {asset.asset_tag_id} expires "
                + ("today." if days == 0 else f"in {days} days.")
            )
        elif -14 <= days <= -7:
            bucket, kind = "expired7", "warranty_expired"
            msg = f"Warranty for {asset.asset_tag_id} expired {-days} days ago."
        else:
            continue
        created += notify(
            db,
            kind,
            msg,
            f"/assets?q={asset.asset_tag_id}",
            dedupe_key=f"warranty:{asset.id}:{asset.warranty_expiry.isoformat()}:{bucket}",
        )
    return created
