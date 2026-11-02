# Assetify by GLOIFY

Asset tracking and device management for a single office (max 6 users): assets, check-in/out,
people, locations, warranty alerts, notifications and an audit trail.

FastAPI + Jinja2 (server-rendered) · SQLAlchemy 2 + Postgres · Tailwind + Preline + HTMX.

## Local setup

```bash
uv sync
docker compose up -d                       # dev Postgres on localhost:5434
cp .env.example .env                       # then fill in the keys below
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"  # FIELD_ENCRYPTION_KEY
python -c "import secrets; print(secrets.token_urlsafe(48))"                               # SECRET_KEY
cd frontend && npm ci && npm run build && cd ..
uv run python -m app.cli init-db           # creates the tables (safe to re-run)
uv run python -m app.cli create-admin --name "Admin" --email you@company.com
uv run python -m app.cli seed-demo         # optional sample data
uv run uvicorn app.main:app --reload
```

Tests: `uv run pytest` (needs the dev Postgres; uses database `assetify_test`, override with `TEST_DATABASE_URL`).
Lint: `uv run ruff check .`

## Environment variables

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Postgres URL. On Vercel use the Neon **pooled** connection string. |
| `SECRET_KEY` | Signs the session cookie. |
| `FIELD_ENCRYPTION_KEY` | Fernet key for stored "last password" values. |
| `ENV` | `dev` or `prod`. `prod` refuses to start with an empty `ALLOWED_IPS`. |
| `ALLOWED_IPS` | Comma-separated CIDRs allowed to use the app (e.g. `203.0.113.10/32`). |
| `CLIENT_IP_HEADER` | Set to `x-vercel-forwarded-for` on Vercel so the allowlist sees the real client IP. |
| `TRUSTED_PROXIES` | Self-hosting only: CIDRs whose `X-Forwarded-For` is trusted. |
| `APP_TIMEZONE` | Display timezone, default `Asia/Kolkata`. |
| `SESSION_HTTPS_ONLY` | `true` in production (Vercel is HTTPS). |
| `CRON_SECRET` | Random string; Vercel Cron sends it as a bearer token to the warranty endpoint. |
| `LOG_LEVEL`, `LOG_DIR` | Logging. `LOG_DIR` is optional (stdout JSON is always on in prod). |

## Deploy on Vercel

1. Install the CLI: `npm i -g vercel`, then `vercel login`.
2. Use your Postgres database (Supabase transaction pooler string, port 6543) as `DATABASE_URL`.
3. Create the tables and the first admin from your machine (the `.env` file already points at the database):
   ```bash
   uv run python -m app.cli init-db
   uv run python -m app.cli create-admin --name "Admin" --email you@company.com
   ```
   Tables are created with `create_all`: it adds missing tables but never alters existing ones, so schema
   changes later mean editing the table by hand (or dropping and recreating while the data is disposable).
4. `vercel link`, then add the environment variables above (`vercel env add ...`) for Production:
   `DATABASE_URL, SECRET_KEY, FIELD_ENCRYPTION_KEY, ENV=prod, ALLOWED_IPS, CLIENT_IP_HEADER=x-vercel-forwarded-for, SESSION_HTTPS_ONLY=true, CRON_SECRET`.
5. `vercel deploy --prod`. The built CSS and vendored JS are committed under `app/static`, so no Node build runs on Vercel
   (re-run `cd frontend && npm run build` after changing templates' Tailwind classes).
6. Check `https://<your-domain>/healthz` from an allowed IP.

Back up `FIELD_ENCRYPTION_KEY` separately: without it stored device passwords are unrecoverable.

## Differences from the original spec (because of Vercel)

- **Scheduler:** Vercel Cron (`vercel.json`, 02:30 UTC = 08:00 IST) calls `/internal/cron/warranty` with `CRON_SECRET`, instead of in-process APScheduler. `python -m app.cli run-warranty-job` still works. Cron timing is UTC, so adjust the schedule if `APP_TIMEZONE` changes.
- **Photos:** stored (re-encoded, max 1600px) in Postgres and served via the authenticated `/media/{name}` route; max 4 MB because Vercel caps request bodies at 4.5 MB.
- **Logging:** JSON to stdout only (serverless has no persistent disk); read it with `vercel logs`.
- **No Docker/nginx/backup script:** Neon provides backups/point-in-time restore. `docker-compose.yml` is only the local dev database.
- **IP allowlist:** enforced in the app using Vercel's `x-vercel-forwarded-for`. For a stronger layer, add a Vercel Firewall rule too.
- Inline "add person / location" in the check-out popup opens an inline panel inside the popup rather than a second modal.

## Notes

- **Rotate `FIELD_ENCRYPTION_KEY`:** decrypt every `assets.last_password_enc` with the old key and re-encrypt with the new one in a one-off script, then swap the env var.
- **Add an asset type:** add it to `ASSET_TYPES` / `ASSET_TYPE_LABELS` in `app/models/asset.py` and the `Literal` in `AssetForm` (`app/schemas/forms.py`). No migration needed (plain string column).
- Max active users is the `MAX_ACTIVE_USERS` constant in `app/config.py`.
- Asset tag and serial uniqueness also applies to soft-deleted assets.
