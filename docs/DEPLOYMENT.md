# Deployment Notes — LogiFlow

This document covers a minimal-but-defensible production deployment for the
Logistics Paperwork Automation System. The graduation-project version runs
against SQLite on a developer laptop; the notes below describe the
incremental steps needed to deploy the same codebase to a small VPS or
managed container host.

---

## 1. Environment variables

All production-sensitive configuration is driven by environment variables.
Set them either in the deployment platform's UI or in a `.env` file next to
`main.py` (the backend auto-loads it via `python-dotenv`).

| Variable | Required | Default (dev) | Production guidance |
|---|---|---|---|
| `SECRET_KEY` | **Yes** | `fallback-secret-key-set-env-var` | 256-bit random hex. Generate with `python -c "import secrets; print(secrets.token_hex(32))"`. Rotate at least quarterly; rotation invalidates all live JWTs. |
| `CORS_ORIGINS` | **Yes** | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated allow-list of the deployed frontend host(s). Example: `https://logiflow.example.com` |
| `DATABASE_URL` | No | `sqlite:///./logistics_automation.db` | When you outgrow SQLite, switch to `postgresql+psycopg://user:pwd@host/db`. Code change is one line in `database.py` (see §4). |
| `TESSDATA_PREFIX` | No (OS-dep) | system default | Path to the Tesseract language packs. Required if Tesseract is installed in a non-standard location. |
| `VITE_API_URL` *(frontend build)* | **Yes** | `http://127.0.0.1:8000` | Set at build time. Example: `VITE_API_URL=https://api.logiflow.example.com npm run build`. |

---

## 2. System prerequisites

The extraction pipeline needs Tesseract installed as a system binary
(`pytesseract` is just the Python wrapper).

```bash
# Ubuntu / Debian
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-ara poppler-utils

# macOS
brew install tesseract tesseract-lang poppler

# Windows (Chocolatey)
choco install tesseract -y
# Install Arabic language pack separately:
#   https://github.com/tesseract-ocr/tessdata/blob/main/ara.traineddata
```

`poppler-utils` ships the `pdftoppm` binary used by `pdf2image` to rasterize
scanned PDFs before OCR.

---

## 3. Backend (FastAPI + uvicorn)

### 3.1 Production process manager

Run uvicorn behind a process manager so the API restarts on crash and on
machine reboot.

**systemd unit (`/etc/systemd/system/logiflow.service`):**

```ini
[Unit]
Description=LogiFlow FastAPI backend
After=network.target

[Service]
User=logiflow
Group=logiflow
WorkingDirectory=/opt/logiflow/Gproject
EnvironmentFile=/opt/logiflow/Gproject/.env
ExecStart=/opt/logiflow/.venv/bin/uvicorn main:app \
    --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Then:

```bash
systemctl daemon-reload
systemctl enable --now logiflow
```

### 3.2 Reverse proxy (TLS + static files)

Front uvicorn with nginx so the public surface is HTTPS-only and the React
build is served directly.

```nginx
server {
    listen 443 ssl http2;
    server_name logiflow.example.com;
    ssl_certificate     /etc/letsencrypt/live/logiflow.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/logiflow.example.com/privkey.pem;

    # React build
    root /opt/logiflow/frontend/dist;
    index index.html;

    location / {
        try_files $uri /index.html;
    }

    location /api/ {
        rewrite ^/api/(.*)$ /$1 break;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 100 MB hard cap (we already enforce 5 MB per file in the app)
    client_max_body_size 100m;
}
```

Build the frontend pointing at the proxy:

```bash
cd frontend
VITE_API_URL=https://logiflow.example.com/api npm run build
```

---

## 4. Migrating from SQLite to PostgreSQL

SQLite is fine for a single-user demo. For multi-user production:

1. **Provision PostgreSQL 14+.** A 1-vCPU / 1 GB instance is enough for the
   expected load (50–100 cases per day).
2. **Install `psycopg`** in `Gproject/requirements.txt`:

   ```
   psycopg[binary]==3.2.3
   ```

3. **Edit `Gproject/database.py`** — replace the SQLite URL:

   ```python
   import os
   SQLALCHEMY_DATABASE_URL = os.getenv(
       "DATABASE_URL",
       "sqlite:///./logistics_automation.db",
   )
   engine = create_engine(SQLALCHEMY_DATABASE_URL)  # drop check_same_thread arg
   ```

4. **Migrate the schema.** The current `run_migrations()` function is SQLite-
   centric; for Postgres install Alembic and stamp the initial revision:

   ```bash
   pip install alembic
   alembic init alembic
   # Edit alembic/env.py to import models.Base.metadata
   alembic revision --autogenerate -m "initial schema"
   alembic upgrade head
   ```

5. **Move uploaded files off the local disk** — use S3 or an equivalent
   object store, and store the object key in `documents.file_path`. The
   `get_document_file` endpoint already validates the path; adapt it to
   stream from the object store.

---

## 5. Backups

| Data | Backup target | Frequency |
|---|---|---|
| `logistics_automation.db` (SQLite) | `s3://backups/logiflow/db/` | Hourly snapshot during business hours |
| `uploaded_docs/` | Same bucket, `uploaded_docs/` prefix | After every successful upload |
| `.env` | Out-of-band secrets manager (e.g. AWS SSM, 1Password) | On change |

If running against PostgreSQL, replace the SQLite snapshot with
`pg_dump --format=custom` cron.

---

## 6. Pre-flight checklist (per release)

- [ ] `python -m pytest -q` in `Gproject/` — **34/34 passing**.
- [ ] `npm run build` in `frontend/` — no warnings.
- [ ] `SECRET_KEY` is set and is **not** the development fallback.
- [ ] `CORS_ORIGINS` is set to the deployed origin only — no wildcards.
- [ ] Tesseract + `ara.traineddata` are installed and importable.
- [ ] `uploaded_docs/` directory exists and is writable by the service user.
- [ ] Reverse-proxy TLS certificate is valid (>= 30 days to expiry).
- [ ] First user has registered (becomes admin via `register_user`).
- [ ] `seed_data.py` is **not** run in production unless wiping the DB is intended.

---

## 7. Known limitations / out-of-scope items

These items are explicitly out of scope per the proposal (Section 2.2) and
the post-graduation roadmap (Sprint 5 doc Section 11). Not blockers for the
graduation demo, but worth noting:

- No external ERP / customs platform integration.
- No automatic HS-code classification.
- No multi-tenant isolation — every authenticated user sees every case.
- No structured logging or APM hookup (uvicorn defaults only).

For follow-up work see the post-graduation roadmap in Sprint 5.docx
(Figure 12).
