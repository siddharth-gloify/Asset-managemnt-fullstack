from __future__ import annotations

from fastapi import Request


def client_ip(request: Request) -> str | None:
    """Client IP for log lines only (Vercel's header when present, else the direct peer)."""
    value = request.headers.get("x-vercel-forwarded-for")
    if value:
        return value.split(",")[0].strip()
    return request.client.host if request.client else None
