"""Sprint 4 — Role-based access control tests (proposal NFR §3.2)."""


def test_first_user_becomes_admin(client):
    res = client.post("/register/", json={"username": "first", "password": "secret1"})
    assert res.status_code == 200
    assert res.json()["role"] == "admin"


def test_second_user_is_staff(client):
    client.post("/register/", json={"username": "first", "password": "secret1"})
    res = client.post("/register/", json={"username": "second", "password": "secret1"})
    assert res.status_code == 200
    assert res.json()["role"] == "staff"


def _login(client, username):
    res = client.post("/login/", data={"username": username, "password": "secret1"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def test_staff_cannot_delete_case(client):
    # admin
    client.post("/register/", json={"username": "admin1", "password": "secret1"})
    admin_h = _login(client, "admin1")
    # staff
    client.post("/register/", json={"username": "staff1", "password": "secret1"})
    staff_h = _login(client, "staff1")

    case = client.post(
        "/cases/", json={"customer": "X", "service_type": "Y"}, headers=admin_h
    ).json()

    # Staff is blocked
    res = client.delete(f"/cases/{case['case_id']}", headers=staff_h)
    assert res.status_code == 403

    # Admin succeeds
    res = client.delete(f"/cases/{case['case_id']}", headers=admin_h)
    assert res.status_code == 200


# Sprint 5 — Viewer role tests. The seed data creates a "viewer" user with
# role='viewer'; the upload + delete endpoints must reject them.
def _make_viewer(client, db_promote_to_viewer=None):
    """
    Helper: register a user and demote their role to 'viewer'.

    Since /register/ promotes the first user to admin and subsequent users
    to staff, we mutate the role directly via the test database after
    creation.
    """
    import main
    import models
    from sqlalchemy.orm import Session

    client.post("/register/", json={"username": "admin0", "password": "secret1"})
    client.post("/register/", json={"username": "vieweruser", "password": "secret1"})

    # Promote the second user to viewer via the test-overridden DB session
    overrides = main.app.dependency_overrides
    get_db_override = list(overrides.values())[0]
    gen = get_db_override()
    db: Session = next(gen)
    try:
        u = db.query(models.User).filter(models.User.username == "vieweruser").first()
        u.role = "viewer"
        db.commit()
    finally:
        try:
            next(gen)
        except StopIteration:
            pass

    return _login(client, "vieweruser"), _login(client, "admin0")


def test_viewer_cannot_upload(client):
    viewer_h, _admin_h = _make_viewer(client)

    case = client.post(
        "/cases/", json={"customer": "ViewerCo", "service_type": "Air"},
        headers=viewer_h,
    ).json()
    upload = client.post(
        f"/cases/{case['case_id']}/documents/",
        headers=viewer_h,
        files={"file": ("x.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")},
    )
    assert upload.status_code == 403
    assert "staff" in upload.json()["detail"].lower()


def test_viewer_cannot_delete_case(client):
    viewer_h, admin_h = _make_viewer(client)

    case = client.post(
        "/cases/", json={"customer": "A", "service_type": "B"},
        headers=admin_h,
    ).json()
    res = client.delete(f"/cases/{case['case_id']}", headers=viewer_h)
    assert res.status_code == 403


# Sprint 5 — Path traversal hardening. GET /documents/{id}/file must
# refuse to serve a path that escapes uploaded_docs/.
def test_path_traversal_rejected(client, auth_headers, tmp_path):
    import main
    import models
    from sqlalchemy.orm import Session

    case = client.post(
        "/cases/", json={"customer": "X", "service_type": "Y"},
        headers=auth_headers,
    ).json()

    # Mutate the file_path to escape uploaded_docs/
    overrides = main.app.dependency_overrides
    get_db_override = list(overrides.values())[0]
    gen = get_db_override()
    db: Session = next(gen)
    try:
        # Insert a forged document row pointing outside uploaded_docs/
        doc = models.Document(
            case_id=case["case_id"],
            doc_type="Invoice",
            file_path="../../etc/passwd",
            uploaded_by=1,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        forged_id = doc.doc_id
    finally:
        try:
            next(gen)
        except StopIteration:
            pass

    res = client.get(f"/documents/{forged_id}/file", headers=auth_headers)
    assert res.status_code == 400
    assert "invalid" in res.json()["detail"].lower()
