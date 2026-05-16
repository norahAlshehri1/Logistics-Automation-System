"""Sprint 4 — Audit log + export + KPI integration tests."""

# A minimal valid PDF for upload — pdfplumber doesn't have to extract anything
# meaningful, the upload + DB plumbing is what we're testing.
MINIMAL_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]>>endobj\n"
    b"xref\n0 4\n"
    b"0000000000 65535 f \n"
    b"0000000010 00000 n \n"
    b"0000000050 00000 n \n"
    b"0000000095 00000 n \n"
    b"trailer<</Size 4/Root 1 0 R>>\n"
    b"startxref\n145\n%%EOF\n"
)


def _create_case_and_upload(client, headers):
    case = client.post(
        "/cases/", json={"customer": "TestCo", "service_type": "Air Freight"},
        headers=headers,
    ).json()
    upload = client.post(
        f"/cases/{case['case_id']}/documents/",
        headers=headers,
        files={"file": ("invoice.pdf", MINIMAL_PDF, "application/pdf")},
    )
    assert upload.status_code == 200, upload.text
    return case, upload.json()


def test_upload_only_accepts_pdf(client, auth_headers):
    case = client.post(
        "/cases/", json={"customer": "X", "service_type": "Y"},
        headers=auth_headers,
    ).json()
    res = client.post(
        f"/cases/{case['case_id']}/documents/",
        headers=auth_headers,
        files={"file": ("evil.txt", b"hello", "text/plain")},
    )
    assert res.status_code == 400


def test_upload_rejects_forged_pdf_mime(client, auth_headers):
    """Sprint 4: client sets MIME=application/pdf but bytes aren't a PDF."""
    case = client.post(
        "/cases/", json={"customer": "X", "service_type": "Y"},
        headers=auth_headers,
    ).json()
    res = client.post(
        f"/cases/{case['case_id']}/documents/",
        headers=auth_headers,
        files={"file": ("fake.pdf", b"this is not a pdf", "application/pdf")},
    )
    assert res.status_code == 400
    assert "magic" in res.json()["detail"].lower()


def test_upload_size_limit(client, auth_headers):
    """Sprint 4: enforces 5 MB upload limit."""
    case = client.post(
        "/cases/", json={"customer": "X", "service_type": "Y"},
        headers=auth_headers,
    ).json()
    big = MINIMAL_PDF + b"\x00" * (6 * 1024 * 1024)  # > 5 MB
    res = client.post(
        f"/cases/{case['case_id']}/documents/",
        headers=auth_headers,
        files={"file": ("big.pdf", big, "application/pdf")},
    )
    assert res.status_code == 413


def test_pdf_serving_endpoint(client, auth_headers):
    """Sprint 4: backend serves the PDF for the review pane's iframe."""
    case, upload = _create_case_and_upload(client, auth_headers)
    res = client.get(f"/documents/{upload['document_id']}/file", headers=auth_headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content[:5] == b"%PDF-"


def test_pdf_serving_requires_auth(client, auth_headers):
    case, upload = _create_case_and_upload(client, auth_headers)
    res = client.get(f"/documents/{upload['document_id']}/file")
    assert res.status_code == 401


def test_approve_creates_audit_log(client, auth_headers, monkeypatch):
    # Stub the extractor so we don't depend on pdfplumber / OCR.
    import main
    def fake_extract(_path):
        return {
            "Vendor Name": "Old Vendor",
            "Invoice Number": "INV-2026-1001",
            "Shipment Date": "2026-04-29",
            "Total Amount": "100.00",
            "confidence_score": "High",
            "language": "english",
        }
    monkeypatch.setattr(main, "extract_invoice_data", fake_extract)

    case, upload = _create_case_and_upload(client, auth_headers)
    doc_id = upload["document_id"]

    extract = client.post(f"/documents/{doc_id}/extract", headers=auth_headers)
    assert extract.status_code == 200

    # User edits the Vendor Name and approves
    approve = client.put(
        f"/documents/{doc_id}/approve",
        headers=auth_headers,
        json={
            "Vendor Name": "New Vendor Ltd",
            "Invoice Number": "INV-2026-1001",
            "Shipment Date": "2026-04-29",
            "Total Amount": "100.00",
        },
    )
    assert approve.status_code == 200

    audit = client.get(f"/cases/{case['case_id']}/audit", headers=auth_headers)
    assert audit.status_code == 200
    logs = audit.json()
    # Only Vendor Name changed compared to the extracted value
    vendor_changes = [a for a in logs if a["field_name"] == "Vendor Name"]
    assert len(vendor_changes) == 1
    assert vendor_changes[0]["old_value"] == "Old Vendor"
    assert vendor_changes[0]["new_value"] == "New Vendor Ltd"


def test_export_excel_and_pdf(client, auth_headers):
    case = client.post(
        "/cases/", json={"customer": "ExportCo", "service_type": "Sea"},
        headers=auth_headers,
    ).json()

    excel = client.get(f"/cases/{case['case_id']}/export/excel", headers=auth_headers)
    assert excel.status_code == 200
    assert excel.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument"
    )
    # XLSX is a zip — magic bytes PK
    assert excel.content[:2] == b"PK"

    pdf = client.get(f"/cases/{case['case_id']}/export/pdf", headers=auth_headers)
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content[:4] == b"%PDF"


def test_kpi_report_shape(client, auth_headers):
    res = client.get("/dashboard/kpi", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    # All target KPIs always present per the proposal
    assert body["processing_time_target_pct"] == 35.0
    assert body["correction_rate_target_pct"] == 40.0
    assert body["completeness_target_pct"] == 20.0
    # Empty system → no approved docs yet
    assert body["approved_documents"] == 0


# Sprint 5 — Audit log is served DESC by changed_at, powered by the
# composite index on (case_id, changed_at). This test confirms the
# wire ordering, which is what the Audit Trail tab relies on.
def test_audit_log_is_descending_by_changed_at(client, auth_headers, monkeypatch):
    import main

    def fake_extract(_path):
        return {
            "Vendor Name": "Vendor A",
            "Invoice Number": "INV-0001",
            "Shipment Date": "2026-05-01",
            "Total Amount": "100.00",
            "confidence_score": "High",
            "language": "english",
        }
    monkeypatch.setattr(main, "extract_invoice_data", fake_extract)

    case, upload = _create_case_and_upload(client, auth_headers)
    doc_id = upload["document_id"]
    client.post(f"/documents/{doc_id}/extract", headers=auth_headers)

    # Three sequential approvals, each editing a different field
    # ⇒ at minimum 3 audit rows.
    client.put(
        f"/documents/{doc_id}/approve",
        headers=auth_headers,
        json={"Vendor Name": "Vendor B", "Invoice Number": "INV-0001",
              "Shipment Date": "2026-05-01", "Total Amount": "100.00"},
    )
    client.put(
        f"/documents/{doc_id}/approve",
        headers=auth_headers,
        json={"Vendor Name": "Vendor B", "Invoice Number": "INV-0002",
              "Shipment Date": "2026-05-01", "Total Amount": "100.00"},
    )
    client.put(
        f"/documents/{doc_id}/approve",
        headers=auth_headers,
        json={"Vendor Name": "Vendor B", "Invoice Number": "INV-0002",
              "Shipment Date": "2026-05-01", "Total Amount": "150.00"},
    )

    audit = client.get(f"/cases/{case['case_id']}/audit", headers=auth_headers)
    assert audit.status_code == 200
    rows = audit.json()
    assert len(rows) >= 3

    # Each timestamp should be greater than or equal to the next (DESC).
    timestamps = [r["changed_at"] for r in rows]
    for earlier, later in zip(timestamps, timestamps[1:]):
        assert earlier >= later, f"audit out of order: {earlier} < {later}"


# Sprint 5 -- EXPLAIN check: the composite index on (case_id, changed_at)
# must actually be picked by the SQLite query planner for the audit query.
def test_audit_query_uses_composite_index(client, auth_headers):
    import main
    from sqlalchemy import text
    from sqlalchemy.orm import Session

    # Create a case so the audit endpoint has a valid case_id to query.
    case = client.post(
        "/cases/", json={"customer": "IndexCheck", "service_type": "Air"},
        headers=auth_headers,
    ).json()

    # Get the test DB session from the override
    overrides = main.app.dependency_overrides
    get_db_override = list(overrides.values())[0]
    gen = get_db_override()
    db: Session = next(gen)
    try:
        # SQLite EXPLAIN QUERY PLAN: returns the chosen access path. If our
        # composite index is wired correctly, the plan mentions
        # ix_audit_log_case_changed_at.
        plan_rows = db.execute(text(
            "EXPLAIN QUERY PLAN "
            "SELECT * FROM audit_log "
            "WHERE case_id = :cid "
            "ORDER BY changed_at DESC"
        ), {"cid": case["case_id"]}).fetchall()
    finally:
        try:
            next(gen)
        except StopIteration:
            pass

    plan_text = " | ".join(str(r) for r in plan_rows).lower()
    # SQLite reports the chosen index in the plan text. Accept either the
    # composite index or any index that starts with "ix_audit_log".
    assert "ix_audit_log" in plan_text, (
        f"audit_log query is not using an index! plan: {plan_text}"
    )
