# Threat Model — LogiFlow (Sprint 5)

This is a one-page STRIDE-style threat model for the Logistics Paperwork
Automation System. It documents the controls that are **already in place
across Sprints 1–5**; it is not a forward-looking compliance project.

| | |
|---|---|
| Scope | The deployed system as of Sprint 5: FastAPI backend, React SPA, SQLite (file-backed), local `uploaded_docs/`. |
| Trust boundaries | Browser ↔ React SPA, React SPA ↔ FastAPI (JWT-authenticated), FastAPI ↔ SQLite, FastAPI ↔ local file system. |
| Assets | (1) Uploaded invoice PDFs, (2) Extracted-field data (customer names, amounts), (3) User credentials (hashed), (4) JWT secret. |
| Adversary model | Unauthenticated external attacker on the public internet; authenticated low-privilege user (viewer) probing for escalation. |

---

## Per-endpoint STRIDE matrix

Legend: **S** = spoofing, **T** = tampering, **R** = repudiation, **I** =
information disclosure, **D** = denial of service, **E** = elevation of
privilege.

| Endpoint | Method | S | T | R | I | D | E | Notes |
|---|---|---|---|---|---|---|---|---|
| `/register/` | POST | ✓ unique username + Bcrypt hash | n/a | DB row records `id` | passwords never returned | password length ≥ 6; ratelimit recommended at proxy | first user → admin, others → staff |
| `/login/` | POST | ✓ Bcrypt verify | n/a | n/a | wrong-password returns generic 400 | ratelimit recommended at proxy | only successful credentials issue a JWT |
| `/me/` | GET | ✓ JWT required | read-only | n/a | returns own row only | n/a | reflects current role to the UI |
| `/cases/` (list) | GET | ✓ JWT | n/a | n/a | n/a | ✓ `limit ≤ 200` | n/a |
| `/cases/` (create) | POST | ✓ JWT | input validated by Pydantic | `created_by` recorded | n/a | n/a | n/a |
| `/cases/{id}` | GET/PUT | ✓ JWT | status whitelist | n/a | n/a | n/a | n/a |
| `/cases/{id}` (delete) | DELETE | ✓ JWT | n/a | n/a | n/a | n/a | ✓ `require_role("admin")` |
| `/cases/search` | GET | ✓ JWT | params validated | n/a | ILIKE bound parameters → no SQLi | n/a | n/a |
| `/cases/{id}/documents/` | POST | ✓ JWT | ✓ filename sanitized (Path.name); ✓ magic-byte check; ✓ MIME check | upload row records `uploaded_by` | path stored as `{doc_id}_{name}` — collision-safe | ✓ 5 MB cap, 1 MB chunk read | ✓ `require_role("staff")` blocks viewers |
| `/documents/{id}/file` | GET | ✓ JWT | ✓ `Path.relative_to(uploaded_docs)` blocks traversal | n/a | served only to authenticated users | n/a | n/a |
| `/documents/{id}/extract` | POST | ✓ JWT | extractor never executes uploaded content as code | n/a | n/a | OCR is CPU-bound — fronted by uvicorn worker count | n/a |
| `/documents/{id}/approve` | PUT | ✓ JWT | values validated by `ApprovedData` schema | ✓ AuditLog row written when value differs | n/a | n/a | n/a |
| `/cases/{id}/audit` | GET | ✓ JWT | read-only | n/a | only same-org audit (no multi-tenancy) | n/a | n/a |
| `/cases/{id}/export/{xlsx,pdf}` | GET | ✓ JWT | builders escape strings via openpyxl/reportlab APIs | n/a | streamed; no temp files on disk | n/a | n/a |
| `/dashboard/summary` | GET | ✓ JWT | read-only | n/a | aggregate-only — no PII leak | ✓ single grouped query (Sprint 5) | n/a |
| `/dashboard/kpi` | GET | ✓ JWT | read-only | n/a | aggregate-only | ✓ single grouped SUM query (Sprint 5) | n/a |

---

## Sprint-by-sprint control inventory

| Control | Sprint | Where in code |
|---|---|---|
| Bcrypt password hashing | 1 | `auth.get_password_hash` / `verify_password` |
| JWT stateless auth (60 min) | 1 | `auth.create_access_token` |
| `Depends(get_current_user)` on every protected route | 1, 4, 5 | `main.py` (every non-`/login/`, non-`/register/` route) |
| Filename sanitization (`Path(name).name`) | 1 | `main.upload_document` |
| MIME whitelist on upload | 1, 4 | `main.upload_document` |
| Magic-byte PDF check (`%PDF-`) | 4 | `main.upload_document` |
| 5 MB upload size cap | 4 | `main.MAX_UPLOAD_BYTES` + chunked read |
| RBAC roles (admin / staff / viewer) | 4, 5 | `auth.require_role` |
| AuditLog row on every value change | 4 | `main.approve_extracted_data` |
| Path-traversal guard on file serving | 4, 5 | `main.get_document_file` (`Path.relative_to`) |
| `CORS_ORIGINS` env override for prod | 5 | `main._cors_origins` |
| Idempotent migrations (no startup crash on re-run) | 5 | `database.run_migrations` + `_safe_exec` |
| Pagination with hard cap (200 rows) | 5 | `main.read_cases` |
| Composite index on AuditLog | 5 | `models.AuditLog.__table_args__` |

---

## Residual risks (acknowledged, out of scope for Sprint 5)

1. **No multi-tenancy.** Every authenticated user can list/view every case.
   In a multi-customer deployment, add a `tenant_id` column and a
   `case.tenant_id == current_user.tenant_id` filter on every query.
2. **JWT secret rotation.** Rotating `SECRET_KEY` invalidates all live
   sessions. A refresh-token + key-versioning scheme would smooth this.
3. **No rate limiting in the app.** `/login/` and `/register/` are
   open to brute force at the application layer. Mitigate at the reverse
   proxy (nginx `limit_req_zone` or Cloudflare).
4. **SQLite single-writer bottleneck.** Under concurrent writes the DB
   serializes them. Migrate to PostgreSQL (see `DEPLOYMENT.md` §4).
5. **Tesseract resource pinning.** OCR is CPU-bound. A flood of large PDF
   uploads could starve workers. Mitigate with a job queue (Celery/RQ) and
   per-user concurrency limits.

These items are out of scope per the proposal Section 2.2 and the Sprint 5
post-graduation roadmap.
