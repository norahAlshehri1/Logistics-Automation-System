from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./logistics_automation.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _safe_exec(conn, sql: str) -> None:
    """
    Sprint 5: run a DDL statement and swallow "already exists" errors.

    SQLite doesn't support ``IF NOT EXISTS`` on every ALTER TABLE form, so
    instead of asking the schema we just attempt the change and tolerate
    ``OperationalError`` from a re-run. Anything else (syntax, constraint,
    permission) still raises.
    """
    try:
        conn.execute(text(sql))
    except OperationalError as exc:
        msg = str(exc).lower()
        if (
            "duplicate column name" in msg
            or "already exists" in msg
            or "duplicate" in msg
        ):
            return  # idempotent re-run
        raise


def run_migrations():
    """
    Add new columns and indexes to existing tables without dropping data.

    Idempotent: safe to call on every startup. Each ALTER/CREATE INDEX is
    wrapped so that re-running against an already-migrated DB is a no-op.
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    with engine.connect() as conn:
        # ── extracted_fields ──────────────────────────────────────────────
        if "extracted_fields" in tables:
            cols = [c["name"] for c in inspector.get_columns("extracted_fields")]
            if "doc_id" not in cols:
                _safe_exec(conn, (
                    "ALTER TABLE extracted_fields "
                    "ADD COLUMN doc_id INTEGER REFERENCES documents(doc_id)"
                ))
            if "approved_at" not in cols:
                _safe_exec(conn, (
                    "ALTER TABLE extracted_fields ADD COLUMN approved_at DATETIME"
                ))
            # Sprint 4: per-field correction counter for KPI 2 (data-entry error rate)
            if "correction_count" not in cols:
                _safe_exec(conn, (
                    "ALTER TABLE extracted_fields "
                    "ADD COLUMN correction_count INTEGER DEFAULT 0"
                ))
            conn.commit()

        # ── documents ────────────────────────────────────────────────────
        if "documents" in tables:
            cols = [c["name"] for c in inspector.get_columns("documents")]
            # Sprint 4: per-document approval timestamp for KPI 1 (processing time)
            if "approved_at" not in cols:
                _safe_exec(conn, (
                    "ALTER TABLE documents ADD COLUMN approved_at DATETIME"
                ))
            conn.commit()

        # ── users ────────────────────────────────────────────────────────
        if "users" in tables:
            cols = [c["name"] for c in inspector.get_columns("users")]
            if "role" not in cols:
                _safe_exec(conn, (
                    "ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user'"
                ))
            conn.commit()

        # ── audit_log indexes (Sprint 5) ─────────────────────────────────
        # Speeds up the Audit Trail tab on Case Detail. Composite index on
        # (case_id, changed_at) matches the WHERE + ORDER BY in
        # GET /cases/{case_id}/audit.
        if "audit_log" in tables:
            _safe_exec(conn, (
                "CREATE INDEX IF NOT EXISTS ix_audit_log_case_changed_at "
                "ON audit_log (case_id, changed_at)"
            ))
            _safe_exec(conn, (
                "CREATE INDEX IF NOT EXISTS ix_audit_log_changed_at "
                "ON audit_log (changed_at)"
            ))
            conn.commit()

        # ── cases / documents secondary indexes (Sprint 5) ───────────────
        # Pagination on the Cases page orders by created_at DESC.
        if "cases" in tables:
            _safe_exec(conn, (
                "CREATE INDEX IF NOT EXISTS ix_cases_created_at "
                "ON cases (created_at)"
            ))
            conn.commit()
        if "documents" in tables:
            _safe_exec(conn, (
                "CREATE INDEX IF NOT EXISTS ix_documents_case_id "
                "ON documents (case_id)"
            ))
            conn.commit()
