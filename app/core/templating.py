from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.config import APP_NAME, get_settings
from app.core.htmx import pop_flashes
from app.models.asset import ASSET_STATUSES, ASSET_TYPE_LABELS, ASSET_TYPES, STATUS_LABELS

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

NAV = [
    ("assets", "Assets", "/assets"),
    ("checkin", "Check In", "/checkin"),
    ("checkout", "Check Out", "/checkout"),
    ("add_device", "Add Device", "/assets/new"),
    ("add_people", "Add People", "/people/new"),
    ("add_location", "Add Location", "/locations/new"),
    ("operations", "Latest Operations", "/operations"),
    ("warranty", "Warranty Nearby Expiry", "/warranty"),
]

STATUS_BADGE = {
    "available": "bg-emerald-100 text-emerald-800",
    "checked_out": "bg-amber-100 text-amber-800",
    "under_maintenance": "bg-sky-100 text-sky-800",
    "retired": "bg-gray-200 text-gray-700",
}


def fmt_dt(value: datetime | None) -> str:
    if not value:
        return "—"
    return value.astimezone(get_settings().tz).strftime("%d %b %Y, %I:%M %p")


def fmt_date(value: date | datetime | None) -> str:
    if not value:
        return "—"
    if isinstance(value, datetime):
        value = value.astimezone(get_settings().tz).date()
    return value.strftime("%d %b %Y")


def dash(value) -> str:
    return "—" if value in (None, "") else str(value)


templates.env.filters.update(dt=fmt_dt, d=fmt_date, dash=dash)
templates.env.globals.update(
    app_name=APP_NAME,
    nav_items=NAV,
    status_labels=STATUS_LABELS,
    status_badge=STATUS_BADGE,
    asset_statuses=ASSET_STATUSES,
    asset_types=ASSET_TYPES,
    asset_type_labels=ASSET_TYPE_LABELS,
    asset_type_options=list(ASSET_TYPE_LABELS.items()),
    get_flashes=pop_flashes,
)


def render(request: Request, name: str, context: dict | None = None, status: int = 200):
    return templates.TemplateResponse(request, name, context or {}, status_code=status)
