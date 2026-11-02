from __future__ import annotations

import os
from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.config import get_settings


class Base(DeclarativeBase):
    pass


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    # prepare_threshold=None: transaction-mode poolers (Supabase/pgbouncer) don't support prepared statements.
    kwargs: dict = {"pool_pre_ping": True, "connect_args": {"prepare_threshold": None}}
    if os.environ.get("VERCEL"):
        # Serverless: no pooled connections held between invocations; use the provider's pooler URL.
        kwargs["poolclass"] = NullPool
    else:
        kwargs.update(pool_size=5, max_overflow=5, pool_recycle=1800)
    return create_engine(settings.sqlalchemy_url, **kwargs)


@lru_cache
def get_sessionmaker() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


def init_db() -> None:
    """Create any missing tables (safe to run repeatedly; never alters existing tables)."""
    import app.models  # noqa: F401  (register models on Base.metadata)

    Base.metadata.create_all(get_engine())


def SessionLocal() -> Session:
    return get_sessionmaker()()


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
