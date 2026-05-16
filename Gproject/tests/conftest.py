"""
Sprint 4 — pytest fixtures.
Uses a per-test in-memory SQLite database so tests don't touch the
production logistics_automation.db file.
"""
import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Make the Gproject package importable when running `pytest` from any cwd.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import database  # noqa: E402
import models    # noqa: E402
import main      # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # Isolate uploads
    upload_dir = tmp_path / "uploaded_docs"
    upload_dir.mkdir()
    monkeypatch.chdir(tmp_path)

    # Build an in-memory engine shared across the test's threads
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    models.Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[database.get_db] = override_get_db

    with TestClient(main.app) as tc:
        yield tc

    main.app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    client.post("/register/", json={"username": "tester", "password": "secret1"})
    res = client.post("/login/", data={"username": "tester", "password": "secret1"})
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
