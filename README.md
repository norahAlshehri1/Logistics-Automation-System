# Logistics Paperwork Automation System (LogiFlow)

End-to-end web app for ingesting commercial invoices (English & Arabic, digital
& scanned), extracting key fields automatically, allowing a human reviewer to
correct and approve them, and exporting the approved data as a branded Excel
or PDF deliverable. Built for BIS405 (Imam Abdulrahman Bin Faisal University).

> **Status:** Sprint 5 complete (freeze & rehearsal). All five proposal user
> stories delivered; all three primary KPIs exceed their proposal targets.

---

## What the system does

| Capability | Where | Notes |
|---|---|---|
| User auth (JWT + Bcrypt) | Backend | First user becomes admin; others = staff |
| RBAC (admin / staff / viewer) | Backend | Upload requires staff+, delete requires admin |
| Case + document lifecycle | Both | Create, list (paginated), filter, status update |
| OCR + bilingual extraction | Backend | pdfplumber → Tesseract fallback (EN/AR) |
| Side-by-side review UI | Frontend | Real embedded PDF + per-field confidence chips |
| Audit log of every edit | Both | `old_value / new_value / who / when` |
| Excel + PDF export | Backend | `openpyxl` + `reportlab`, streamed (no temp files) |
| KPI dashboard | Both | Processing time / corrections / completeness |
| Dark mode + toasts + skeletons | Frontend | Sprint 5 UX polish layer |

---

## Quickstart

### 1. Backend

```powershell
cd Gproject
pip install -r requirements.txt
python seed_data.py            # optional — wipes DB and seeds 6 users + 10 demo cases
uvicorn main:app --reload
```

API: <http://127.0.0.1:8000> · Swagger: <http://127.0.0.1:8000/docs>

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

UI: <http://localhost:5173>

### Demo credentials (after running `seed_data.py`)

| Username | Password | Role |
|---|---|---|
| `linah` | `supervisor123` | admin |
| `norah`, `bayader`, `shaykhah`, `maha` | `<name>2026` | staff |
| `viewer` | `viewer2026` | viewer (read-only) |

---

## Technology stack

**Backend** — Python 3.10+, FastAPI 0.115, SQLAlchemy 2.0, SQLite, pdfplumber,
pdf2image, pytesseract, Pillow, openpyxl, reportlab, JWT (`pyjwt`),
Bcrypt, pytest 9.

**Frontend** — React 19 + Vite, React Router v6, Axios, Chart.js (via
`react-chartjs-2`), CSS custom properties (dark-mode tokens).

---

## Project layout

```
.
├── Gproject/              FastAPI backend
│   ├── main.py            Route definitions
│   ├── auth.py            JWT + RBAC (require_role)
│   ├── models.py          SQLAlchemy ORM (incl. AuditLog index)
│   ├── database.py        Engine + idempotent migrations
│   ├── extractor.py       OCR + bilingual regex
│   ├── exporter.py        openpyxl + reportlab builders
│   ├── seed_data.py       Demo-data seeder (Sprint 5)
│   ├── pytest.ini         Pytest config (warnings filter)
│   └── tests/             34 tests, in-memory SQLite fixtures
├── frontend/              React SPA
│   └── src/
│       ├── App.jsx                Routes
│       ├── context/AuthContext.jsx
│       ├── context/ThemeContext.jsx   (Sprint 5: dark mode)
│       ├── context/ToastContext.jsx   (Sprint 5: toasts)
│       ├── components/Skeleton.jsx    (Sprint 5: loading)
│       ├── components/ProtectedRoute.jsx
│       └── pages/                 6 routed pages
├── docs/                  Sprint reports, charts, generators, handover docs
│   ├── DEPLOYMENT.md      (Sprint 5)
│   ├── THREAT_MODEL.md    (Sprint 5)
│   ├── VIDEO_SCRIPT.md
│   ├── generate_sprint{4,5}_assets.py
│   ├── generate_sprint{4,5}_doc.py
│   └── sprint{4,5}_assets/
├── Sprint 4.docx
└── Sprint 5.docx
```

---

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | `fallback-secret-key-set-env-var` | JWT signing key. **Set in production.** |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated allow-list |
| `VITE_API_URL` *(frontend)* | `http://127.0.0.1:8000` | Backend URL for Axios |

A `.env` file at the repo root or inside `Gproject/` is auto-loaded via
`python-dotenv`.

---

## Running the tests

```powershell
cd Gproject
python -m pytest -q
```

The suite uses an in-memory SQLite database and a FastAPI `TestClient` — it
never touches `logistics_automation.db`. Expect **34/34 passing** in ~13s on a
developer laptop.

---

## KPI achievement (vs. proposal Section 1.3 targets)

| KPI | Baseline | Sprint 5 | Target | Achieved |
|---|---|---|---|---|
| KPI 1 — Processing time | 22.0 min | 12.25 min | ≥ 35% drop | **44.3% drop** |
| KPI 2 — Correction rate | 3.0/case | 1.54/case | ≥ 40% drop | **48.5% drop** |
| KPI 3 — Completeness | 70.0% | 95.0% | ≥ 20% gain | **+25.0 pp** |

The numbers come from `GET /dashboard/kpi` after running `seed_data.py`.

---

## Handover documents

- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) — production deployment notes (env vars, CORS, JWT rotation, PostgreSQL migration path).
- [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md) — STRIDE-style threat model mapping endpoints to mitigations.
- [`docs/VIDEO_SCRIPT.md`](docs/VIDEO_SCRIPT.md) — narration for the fallback demo recording.
- `Sprint 1–5` reports — full sprint history under [`docs/`](docs/) and at the repo root.

---

## Team

| Member | ID | Sprint 5 focus |
|---|---|---|
| Norah Alshehri | 2230004682 | Backend: perf tuning, stability, RBAC |
| Bayader Alghamdi | 2230003715 | Backend: pagination, threat model, tests |
| Shaykhah Mohsen | 2230005764 | Frontend: theme, toasts, skeletons, animations |
| Maha Alnafea | 2230003005 | Frontend: demo script, fallback video, handover |

**Supervisor:** Dr. Linah Saraireh

---

## License

This project is a graduation deliverable for BIS405. Not licensed for
production reuse without permission of the authors.
