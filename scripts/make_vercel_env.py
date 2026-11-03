"""Create .env.vercel (git-ignored) with production values for Vercel.

Reads DATABASE_URL from .env, generates fresh SECRET_KEY / FIELD_ENCRYPTION_KEY / CRON_SECRET, and
takes the office IP allowlist as an argument. Existing .env.vercel keys are kept unless --force.

    python scripts/make_vercel_env.py --allowed-ips 203.0.113.10/32,10.0.0.0/8
"""

from __future__ import annotations

import argparse
import secrets
from pathlib import Path

from cryptography.fernet import Fernet

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / ".env.vercel"


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                values[key.strip()] = value.strip()
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allowed-ips", required=True, help="Comma-separated CIDRs")
    parser.add_argument("--timezone", default="Asia/Kolkata")
    parser.add_argument("--force", action="store_true", help="Regenerate secrets even if present")
    args = parser.parse_args()

    local = read_env(ROOT / ".env")
    existing = {} if args.force else read_env(TARGET)
    if "DATABASE_URL" not in local or "[YOUR-PASSWORD]" in local["DATABASE_URL"]:
        raise SystemExit("Set a real DATABASE_URL in .env first.")

    values = {
        "DATABASE_URL": local["DATABASE_URL"],
        "SECRET_KEY": existing.get("SECRET_KEY") or secrets.token_urlsafe(48),
        "FIELD_ENCRYPTION_KEY": existing.get("FIELD_ENCRYPTION_KEY") or Fernet.generate_key().decode(),
        "CRON_SECRET": existing.get("CRON_SECRET") or secrets.token_urlsafe(32),
        "ENV": "prod",
        "ALLOWED_IPS": args.allowed_ips,
        "CLIENT_IP_HEADER": "x-vercel-forwarded-for",
        "SESSION_HTTPS_ONLY": "true",
        "APP_TIMEZONE": args.timezone,
        "LOG_LEVEL": "INFO",
    }
    TARGET.write_text(
        "# Production values for Vercel. Git-ignored: never commit this file.\n"
        + "".join(f"{k}={v}\n" for k, v in values.items()),
        encoding="utf-8",
    )
    print(f"Wrote {TARGET.name} with {len(values)} variables (secrets not printed).")


if __name__ == "__main__":
    main()
