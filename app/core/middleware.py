from __future__ import annotations

import time
import uuid

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger
from app.core.netutil import client_ip

log = get_logger("http")

SLOW_REQUEST_MS = 1000


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Request id + client ip into log context, one access-log line per request."""

    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:16]
        ip = client_ip(request)
        request.state.request_id = rid
        request.state.client_ip = ip
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=rid, client_ip=ip)
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            log.exception("unhandled_exception", method=request.method, path=request.url.path)
            raise
        duration_ms = round((time.perf_counter() - start) * 1000, 1)
        response.headers["X-Request-ID"] = rid
        emit = log.warning if duration_ms > SLOW_REQUEST_MS else log.info
        emit(
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration_ms,
            user_id=getattr(request.state, "user_id", None),
            slow=duration_ms > SLOW_REQUEST_MS,
        )
        return response
