from __future__ import annotations

import json

from fastapi import Request
from fastapi.responses import RedirectResponse, Response


def is_htmx(request: Request) -> bool:
    return request.headers.get("hx-request") == "true"


def flash(request: Request, message: str, kind: str = "success") -> None:
    flashes = request.session.get("flashes", [])
    flashes.append({"type": kind, "message": message})
    request.session["flashes"] = flashes


def pop_flashes(request: Request) -> list[dict]:
    return request.session.pop("flashes", [])


def hx_trigger(response: Response, **events) -> Response:
    """Merge events into the HX-Trigger header (toast, closeModal, ...)."""
    existing = response.headers.get("HX-Trigger")
    payload = json.loads(existing) if existing else {}
    payload.update(events)
    response.headers["HX-Trigger"] = json.dumps(payload)
    return response


def toast(response: Response, message: str, kind: str = "success") -> Response:
    return hx_trigger(response, toast={"type": kind, "message": message})


def redirect(request: Request, url: str, message: str | None = None, kind: str = "success"):
    """POST-redirect-GET. For HTMX requests the browser is told to navigate (HX-Redirect)."""
    if message:
        flash(request, message, kind)
    if is_htmx(request):
        response = Response(status_code=204)
        response.headers["HX-Redirect"] = url
        return response
    return RedirectResponse(url, status_code=303)
