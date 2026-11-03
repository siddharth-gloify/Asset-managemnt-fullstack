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
uv run python -m app.cli seed-users        # logins come from SEED_USERS in .env (no sign-up in the app)
uv run python -m app.cli seed-demo         # optional sample data
uv run uvicorn app.main:app --reload
```

Tests: `uv run pytest` (needs the dev Postgres; uses database `assetify_test`, override with `TEST_DATABASE_URL`).
Lint: `uv run ruff check .`

## Environment variables

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Postgres URL. On Vercel use the Neon **pooled** connection string. |
| `SEED_USERS` | `Name\|email\|password,...` logins; `seed-users` creates/updates them (re-run after editing). |
| `SECRET_KEY` | Signs the session cookie. |
| `FIELD_ENCRYPTION_KEY` | Fernet key for stored "last password" values. |
| `ENV` | `dev` or `prod`. |
| `APP_TIMEZONE` | Display timezone, default `Asia/Kolkata`. |
| `SESSION_HTTPS_ONLY` | `true` in production (Vercel is HTTPS). |
| `CRON_SECRET` | Random string; Vercel Cron sends it as a bearer token to the warranty endpoint. |
| `LOG_LEVEL`, `LOG_DIR` | Logging. `LOG_DIR` is optional (stdout JSON is always on in prod). |

## Deploy on Vercel

1. Install the CLI (`npm i -g vercel`), then `vercel login`.
2. Database: the Supabase **transaction pooler** string (port 6543) goes in `.env` as `DATABASE_URL`. Create the tables
   and the first admin from your machine:
   ```bash
   uv run python -m app.cli init-db
   uv run python -m app.cli seed-users        # logins come from SEED_USERS in .env (no sign-up in the app)
   ```
   Tables are created with `create_all`: it adds missing tables but never alters existing ones, so schema
   changes later mean editing the table by hand (or dropping and recreating while the data is disposable).
3. Generate production settings (fresh secrets) into the git-ignored `.env.vercel`:
   ```bash
   uv run python scripts/make_vercel_env.py
   ```
4. Link the project and push those variables to Production:
   ```bash
   vercel link
   uv run python scripts/push_vercel_env.py
   ```
5. `vercel deploy --prod`. The built CSS and vendored JS are committed under `app/static`, so no Node build runs on Vercel
   (re-run `cd frontend && npm run build` after changing templates' Tailwind classes). `index.py` is the entrypoint.
6. Check `https://<your-domain>/healthz` then sign in.

Back up `FIELD_ENCRYPTION_KEY` separately: without it stored device passwords are unrecoverable.

## Differences from the original spec (because of Vercel)

- **Scheduler:** Vercel Cron (`vercel.json`, 02:30 UTC = 08:00 IST) calls `/internal/cron/warranty` with `CRON_SECRET`, instead of in-process APScheduler. `python -m app.cli run-warranty-job` still works. Cron timing is UTC, so adjust the schedule if `APP_TIMEZONE` changes.
- **Photos:** stored (re-encoded, max 1600px) in Postgres and served via the authenticated `/media/{name}` route; max 4 MB because Vercel caps request bodies at 4.5 MB.
- **Logging:** JSON to stdout only (serverless has no persistent disk); read it with `vercel logs`.
- **No Docker/nginx/backup script:** use Supabase's backups (daily on paid plans; export manually on the free plan). `docker-compose.yml` is only the local dev database.
- Inline "add person / location" in the check-out popup opens an inline panel inside the popup rather than a second modal.

## Notes

- **Rotate `FIELD_ENCRYPTION_KEY`:** decrypt every `assets.last_password_enc` with the old key and re-encrypt with the new one in a one-off script, then swap the env var.
- **Add an asset type:** add it to `ASSET_TYPES` / `ASSET_TYPE_LABELS` in `app/models/asset.py` and the `Literal` in `AssetForm` (`app/schemas/forms.py`). No migration needed (plain string column).
- Max active users is the `MAX_ACTIVE_USERS` constant in `app/config.py`.
- Asset tag and serial uniqueness also applies to soft-deleted assets.
