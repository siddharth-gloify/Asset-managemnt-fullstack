from __future__ import annotations

import ipaddress

from fastapi import Request

from app.config import get_settings


def ip_in(value: str | None, networks) -> bool:
    if not value:
        return False
    try:
        addr = ipaddress.ip_address(value)
    except ValueError:
        return False
    return any(addr in net for net in networks)


def is_loopback(value: str | None) -> bool:
    try:
        return bool(value) and ipaddress.ip_address(value).is_loopback
    except ValueError:
        return False


def client_ip(request: Request) -> str | None:
    """Resolve the real client IP.

    Preference: the platform header (Vercel's x-vercel-forwarded-for) when configured; otherwise
    X-Forwarded-For, honoured only when the direct peer is a trusted proxy (walk from the right,
    skipping trusted hops); otherwise the direct peer.
    """
    settings = get_settings()
    peer = request.client.host if request.client else None
    if settings.client_ip_header:
        value = request.headers.get(settings.client_ip_header)
        if value:
            return value.split(",")[0].strip()
    trusted = settings.trusted_proxy_networks
    if peer and trusted and ip_in(peer, trusted):
        xff = request.headers.get("x-forwarded-for")
        if xff:
            hops = [h.strip() for h in xff.split(",") if h.strip()]
            for hop in reversed(hops):
                if not ip_in(hop, trusted):
                    return hop
            return hops[0] if hops else peer
    return peer
