"""Vercel entrypoint: exposes the ASGI app."""

from app.main import app

__all__ = ["app"]
