"""Sprint 4 — Case CRUD + search tests."""


def _create_case(client, headers, customer="Aramex", service_type="Air Freight"):
    res = client.post(
        "/cases/",
        json={"customer": customer, "service_type": service_type},
        headers=headers,
    )
    assert res.status_code == 200, res.text
    return res.json()


def test_case_crud_lifecycle(client, auth_headers):
    case = _create_case(client, auth_headers)
    case_id = case["case_id"]
    assert case["status"] == "Pending"

    list_res = client.get("/cases/", headers=auth_headers)
    assert list_res.status_code == 200
    assert any(c["case_id"] == case_id for c in list_res.json())

    upd = client.put(f"/cases/{case_id}?new_status=In Review", headers=auth_headers)
    assert upd.status_code == 200
    assert upd.json()["status"] == "In Review"

    bad = client.put(f"/cases/{case_id}?new_status=Bogus", headers=auth_headers)
    assert bad.status_code == 400

    delete = client.delete(f"/cases/{case_id}", headers=auth_headers)
    assert delete.status_code == 200

    missing = client.get(f"/cases/{case_id}", headers=auth_headers)
    assert missing.status_code == 404


def test_case_search_by_customer(client, auth_headers):
    _create_case(client, auth_headers, customer="Saudi Logistics Co.")
    _create_case(client, auth_headers, customer="Gulf Star Shipping")

    res = client.get("/cases/search?q=Gulf", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert len(body) == 1
    assert "Gulf" in body[0]["customer"]


def test_case_search_by_status(client, auth_headers):
    c1 = _create_case(client, auth_headers, customer="X")
    c2 = _create_case(client, auth_headers, customer="Y")
    client.put(f"/cases/{c1['case_id']}?new_status=Approved", headers=auth_headers)

    res = client.get("/cases/search?status=Approved", headers=auth_headers)
    assert res.status_code == 200
    ids = [c["case_id"] for c in res.json()]
    assert c1["case_id"] in ids
    assert c2["case_id"] not in ids
