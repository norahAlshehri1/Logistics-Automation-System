"""Sprint 5 -- Pagination tests for GET /cases/."""


def _seed_cases(client, headers, n):
    for i in range(n):
        res = client.post(
            "/cases/",
            json={"customer": f"Customer-{i:03d}", "service_type": "Sea Freight"},
            headers=headers,
        )
        assert res.status_code == 200, res.text


def test_pagination_returns_default_page_size(client, auth_headers):
    _seed_cases(client, auth_headers, 6)
    # Default page size is 50; with 6 rows we just get all of them.
    res = client.get("/cases/", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) == 6


def test_pagination_respects_limit_and_offset(client, auth_headers):
    _seed_cases(client, auth_headers, 7)

    # First page of 3
    page1 = client.get("/cases/?limit=3&offset=0", headers=auth_headers)
    assert page1.status_code == 200
    page1_body = page1.json()
    assert len(page1_body) == 3

    # Second page of 3 -- should be a disjoint set from page 1
    page2 = client.get("/cases/?limit=3&offset=3", headers=auth_headers)
    assert page2.status_code == 200
    page2_body = page2.json()
    assert len(page2_body) == 3

    page1_ids = {c["case_id"] for c in page1_body}
    page2_ids = {c["case_id"] for c in page2_body}
    assert page1_ids.isdisjoint(page2_ids)

    # Tail page (1 row remaining)
    tail = client.get("/cases/?limit=3&offset=6", headers=auth_headers)
    assert tail.status_code == 200
    assert len(tail.json()) == 1


def test_pagination_rejects_oversize_limit(client, auth_headers):
    # Max page size is 200; 999 must be rejected by FastAPI's Query(le=200).
    res = client.get("/cases/?limit=999&offset=0", headers=auth_headers)
    assert res.status_code == 422


def test_pagination_rejects_negative_offset(client, auth_headers):
    res = client.get("/cases/?limit=10&offset=-1", headers=auth_headers)
    assert res.status_code == 422
