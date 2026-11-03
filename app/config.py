from __future__ import annotations

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
    app_timezone: str = "Asia/Kolkata"
    log_level: str = "INFO"
    log_dir: str = ""
    env: str = "dev"
    session_https_only: bool = False
    cron_secret: str = ""
    session_idle_minutes: int = 30
    # In-house logins, "Name|email|password" separated by commas; applied by `python -m app.cli seed-users`.
    seed_users: str = ""

    @property
    def seed_user_list(self) -> list[tuple[str, str, str]]:
        rows = []
        for part in self.seed_users.split(","):
            fields = [f.strip() for f in part.split("|")]
            if len(fields) == 3 and all(fields):
                rows.append((fields[0], fields[1], fields[2]))
        return rows

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



@lru_cache
def get_settings() -> Settings:
    return Settings()
