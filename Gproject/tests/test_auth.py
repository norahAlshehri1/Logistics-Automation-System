"""Sprint 4 — Authentication tests."""


def test_register_then_login(client):
    res = client.post("/register/", json={"username": "alice", "password": "passw0rd"})
    assert res.status_code == 200
    assert res.json()["username"] == "alice"

    res = client.post("/login/", data={"username": "alice", "password": "passw0rd"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_register_short_password_rejected(client):
    res = client.post("/register/", json={"username": "bob", "password": "123"})
    assert res.status_code == 400


def test_register_duplicate_rejected(client):
    client.post("/register/", json={"username": "carol", "password": "secret1"})
    res = client.post("/register/", json={"username": "carol", "password": "secret2"})
    assert res.status_code == 400


def test_protected_route_rejects_anon(client):
    res = client.get("/cases/")
    assert res.status_code == 401


def test_login_wrong_password(client):
    client.post("/register/", json={"username": "dave", "password": "secret1"})
    res = client.post("/login/", data={"username": "dave", "password": "wrong"})
    assert res.status_code == 400
