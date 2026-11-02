from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

PER_PAGE = 25


class FormError(Exception):
    """Validation/business-rule failure; `errors` maps field name (or "_" for form-level) to text."""

    def __init__(self, errors: dict[str, str] | str):
        self.errors = {"_": errors} if isinstance(errors, str) else errors
        super().__init__("; ".join(self.errors.values()))


class NotFound(Exception):
    pass


def now_utc() -> datetime:
    return datetime.now(UTC)


def escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


@dataclass
class Page:
    items: list[Any]
    total: int
    page: int
    per_page: int = PER_PAGE
    pages: int = field(init=False)

    def __post_init__(self):
        self.pages = max(1, math.ceil(self.total / self.per_page))

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def first(self) -> int:
        return 0 if self.total == 0 else (self.page - 1) * self.per_page + 1

    @property
    def last(self) -> int:
        return min(self.total, self.page * self.per_page)


def paginate(db: Session, stmt: Select, page: int, per_page: int = PER_PAGE, scalars: bool = True):
    page = max(1, page)
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    pages = max(1, math.ceil(total / per_page))
    page = min(page, pages)
    rows = db.execute(stmt.limit(per_page).offset((page - 1) * per_page))
    items = list(rows.scalars().all() if scalars else rows.all())
    return Page(items=items, total=total, page=page, per_page=per_page)
