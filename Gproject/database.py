from sqlalchemy import create_engine, text, inspect
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


def run_migrations():
    """Add new columns to existing tables without dropping data."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    with engine.connect() as conn:
        if "extracted_fields" in tables:
            cols = [c["name"] for c in inspector.get_columns("extracted_fields")]
            if "doc_id" not in cols:
                conn.execute(text(
                    "ALTER TABLE extracted_fields ADD COLUMN doc_id INTEGER REFERENCES documents(doc_id)"
                ))
            if "approved_at" not in cols:
                conn.execute(text(
                    "ALTER TABLE extracted_fields ADD COLUMN approved_at DATETIME"
                ))
            conn.commit()

        if "users" in tables:
            cols = [c["name"] for c in inspector.get_columns("users")]
            if "role" not in cols:
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user'"
                ))
            conn.commit()
