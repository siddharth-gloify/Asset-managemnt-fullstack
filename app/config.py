from __future__ import annotations

import ipaddress
from functools import lru_cache
from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings, SettingsConfigDict

MAX_ACTIVE_USERS = 6
APP_NAME = "Assetify by GLOIFY"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    secret_key: str
    field_encryption_key: str
    allowed_ips: str = ""
    # Header carrying the real client IP when the platform sets it (Vercel: x-vercel-forwarded-for).
    client_ip_header: str = ""
    # Only used when client_ip_header is empty: X-Forwarded-For is honoured from these peers.
    trusted_proxies: str = ""
    app_timezone: str = "Asia/Kolkata"
    log_level: str = "INFO"
    log_dir: str = ""
    env: str = "dev"
    session_https_only: bool = False
    cron_secret: str = ""
    session_idle_minutes: int = 30

    @property
    def is_prod(self) -> bool:
        return self.env.lower() == "prod"

    @staticmethod
    def _normalize_url(url: str) -> str:
        # Drop Prisma-only query params (e.g. pgbouncer=true) that psycopg rejects.
        base, _, query = url.partition("?")
        kept = [p for p in query.split("&") if p and p.split("=")[0] not in ("pgbouncer", "connection_limit")]
        url = base + ("?" + "&".join(kept) if kept else "")
        for prefix in ("postgresql://", "postgres://"):
            if url.startswith(prefix):
                return "postgresql+psycopg://" + url[len(prefix):]
        return url

    @property
    def sqlalchemy_url(self) -> str:
        return self._normalize_url(self.database_url)

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.app_timezone)

    @staticmethod
    def _networks(raw: str) -> list[ipaddress._BaseNetwork]:
        nets = []
        for part in raw.split(","):
            part = part.strip()
            if part:
                nets.append(ipaddress.ip_network(part, strict=False))
        return nets

    @property
    def allowed_networks(self):
        return self._networks(self.allowed_ips)

    @property
    def trusted_proxy_networks(self):
        return self._networks(self.trusted_proxies)


@lru_cache
def get_settings() -> Settings:
    return Settings()
