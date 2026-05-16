"""
Sprint 4 — Demo data seeder.

Wipes all existing users / cases / documents / extracted fields / audit logs
and re-populates the database with a realistic demo dataset:

  • 6 users covering all three roles (Admin / Staff / Viewer)
  • 10 shipment cases spanning every status (Pending / In Review / Approved / Closed)
  • 9 uploaded PDF documents (copied from test_invoices/ to uploaded_docs/)
  • Extracted fields with mixed per-field confidence levels (US2 demo)
  • Audit log entries covering field corrections (KPI 2 demo)
  • approved_at timestamps tuned so the KPI dashboard shows real numbers

Usage:
    python seed_data.py

Login credentials after seeding (all passwords are listed in DEMO_USERS below).
"""
import shutil
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

import auth
import models
from database import SessionLocal, engine, run_migrations


# ── Configuration ────────────────────────────────────────────────────────────

UPLOAD_DIR = Path("uploaded_docs")
TEST_DIR = Path("test_invoices")

NOW = datetime.now(timezone.utc)


def ago(**delta):
    return NOW - timedelta(**delta)


# ── Demo users ───────────────────────────────────────────────────────────────

DEMO_USERS = [
    # username, password, role
    ("linah",     "supervisor123", "admin"),   # Dr. Linah Saraireh (supervisor)
    ("norah",     "norah2026",     "staff"),
    ("bayader",   "bayader2026",   "staff"),
    ("shaykhah",  "shaykhah2026",  "staff"),
    ("maha",      "maha2026",      "staff"),
    ("viewer",    "viewer2026",    "viewer"),  # read-only stakeholder
]


# ── Demo cases ───────────────────────────────────────────────────────────────
# Each: customer, service_type, status, created_at, created_by_username, invoice_pdf

DEMO_CASES = [
    {
        "customer": "Aramex Saudi Arabia",
        "service_type": "Air Freight",
        "status": "Approved",
        "created_at": ago(days=21),
        "owner": "norah",
        "invoice": "INV-2026-1001.pdf",
        "approved_minutes_after_upload": 13,
        "extraction": {
            "Vendor Name":    ("Aramex Saudi Arabia",            "High"),
            "Invoice Number": ("INV-2026-1001",                  "High"),
            "Shipment Date":  ("2026-04-12",                     "High"),
            "Total Amount":   ("8450.00",                        "High"),
        },
        "approved_values": {
            "Vendor Name":    "Aramex Saudi Arabia",
            "Invoice Number": "INV-2026-1001",
            "Shipment Date":  "2026-04-12",
            "Total Amount":   "8450.00",
        },
        "audit_edits": [],
    },
    {
        "customer": "Arabian Freight Solutions Co.",
        "service_type": "Sea Freight",
        "status": "Approved",
        "created_at": ago(days=14),
        "owner": "bayader",
        "invoice": "INV-2026-9001.pdf",
        "approved_minutes_after_upload": 11,
        "extraction": {
            "Vendor Name":    ("Arabian Freight Solutions",      "Medium"),
            "Invoice Number": ("INV-2026-9001",                  "High"),
            "Shipment Date":  ("2026-04-29",                     "High"),
            "Total Amount":   ("12391.25",                       "High"),
        },
        "approved_values": {
            # Reviewer corrected the trailing "Co." that OCR missed
            "Vendor Name":    "Arabian Freight Solutions Co.",
            "Invoice Number": "INV-2026-9001",
            "Shipment Date":  "2026-04-29",
            "Total Amount":   "12391.25",
        },
        "audit_edits": [
            ("Vendor Name", "Arabian Freight Solutions", "Arabian Freight Solutions Co.", "bayader"),
        ],
    },
    {
        "customer": "Gulf Star Shipping Co.",
        "service_type": "Air Freight",
        "status": "Approved",
        "created_at": ago(days=12),
        "owner": "shaykhah",
        "invoice": "INV-2026-9002.pdf",
        "approved_minutes_after_upload": 14,
        "extraction": {
            "Vendor Name":    ("Gulf Star Shipping Co.",         "High"),
            "Invoice Number": ("INV-2026-9002",                  "High"),
            "Shipment Date":  ("22/04/2026",                     "Medium"),  # alt format
            "Total Amount":   ("7647.50",                        "High"),
        },
        "approved_values": {
            "Vendor Name":    "Gulf Star Shipping Co.",
            "Invoice Number": "INV-2026-9002",
            "Shipment Date":  "2026-04-22",   # reviewer normalized format
            "Total Amount":   "7647.50",
        },
        "audit_edits": [
            ("Shipment Date", "22/04/2026", "2026-04-22", "shaykhah"),
        ],
    },
    {
        "customer": "Saudi Express Cargo & Logistics",
        "service_type": "Heavy Cargo",
        "status": "Approved",
        "created_at": ago(days=10),
        "owner": "maha",
        "invoice": "INV-2026-9003.pdf",
        "approved_minutes_after_upload": 12,
        "extraction": {
            "Vendor Name":    ("Saudi Express Cargo",            "Medium"),
            "Invoice Number": ("INV-2026-9003",                  "High"),
            "Shipment Date":  ("2026-04-27",                     "High"),
            "Total Amount":   ("25530",                          "Low"),   # missing decimals
        },
        "approved_values": {
            "Vendor Name":    "Saudi Express Cargo & Logistics",
            "Invoice Number": "INV-2026-9003",
            "Shipment Date":  "2026-04-27",
            "Total Amount":   "25530.00",
        },
        "audit_edits": [
            ("Vendor Name",  "Saudi Express Cargo", "Saudi Express Cargo & Logistics", "maha"),
            ("Total Amount", "25530",               "25530.00",                        "maha"),
        ],
    },
    {
        "customer": "Riyadh Customs Clearance LLC",
        "service_type": "Customs Clearance",
        "status": "In Review",
        "created_at": ago(days=7),
        "owner": "norah",
        "invoice": "INV-2026-1002.pdf",
        "approved_minutes_after_upload": None,  # not approved yet
        "extraction": {
            "Vendor Name":    ("Riyadh Customs Clearance LLC",   "High"),
            "Invoice Number": ("INV-2026-1002",                  "High"),
            "Shipment Date":  ("2026-05-02",                     "High"),
            "Total Amount":   (None,                             "Missing"),  # not detected
        },
        "approved_values": None,
        "audit_edits": [],
    },
    {
        "customer": "Aramco Supply Chain Division",
        "service_type": "Heavy Cargo",
        "status": "In Review",
        "created_at": ago(days=5),
        "owner": "bayader",
        "invoice": "INV-2026-1003.pdf",
        "approved_minutes_after_upload": None,
        "extraction": {
            "Vendor Name":    ("Aramco Supply Chain",            "Medium"),
            "Invoice Number": ("INV-2026-1003",                  "High"),
            "Shipment Date":  ("2026-05-04",                     "High"),
            "Total Amount":   ("18250.00",                       "High"),
        },
        "approved_values": None,
        "audit_edits": [],
    },
    {
        "customer": "Jeddah Port Authority",
        "service_type": "Sea Freight",
        "status": "Pending",
        "created_at": ago(days=3),
        "owner": "shaykhah",
        "invoice": "INV-2026-1004.pdf",
        "approved_minutes_after_upload": None,
        "extraction": None,  # not yet extracted
        "approved_values": None,
        "audit_edits": [],
    },
    {
        "customer": "Bahri Logistics",
        "service_type": "Sea Freight",
        "status": "Pending",
        "created_at": ago(days=2),
        "owner": "maha",
        "invoice": "INV-2026-1005.pdf",
        "approved_minutes_after_upload": None,
        "extraction": None,
        "approved_values": None,
        "audit_edits": [],
    },
    {
        "customer": "Pioneer Manufacturing Ltd.",
        "service_type": "Air Freight",
        "status": "Pending",
        "created_at": ago(days=1),
        "owner": "norah",
        "invoice": None,  # case created but no doc uploaded yet
        "approved_minutes_after_upload": None,
        "extraction": None,
        "approved_values": None,
        "audit_edits": [],
    },
    {
        "customer": "King Khalid Express",
        "service_type": "Road",
        "status": "Closed",
        "created_at": ago(days=35),
        "owner": "bayader",
        "invoice": None,
        "approved_minutes_after_upload": None,
        "extraction": None,
        "approved_values": None,
        "audit_edits": [],
    },
]


# ── Seeding logic ────────────────────────────────────────────────────────────

def wipe(db: Session):
    """Clear demo-relevant tables."""
    db.query(models.AuditLog).delete()
    db.query(models.ExtractedFields).delete()
    db.query(models.Document).delete()
    db.query(models.Case).delete()
    db.query(models.User).delete()
    db.commit()

    # Wipe uploaded_docs/ but keep .gitkeep
    if UPLOAD_DIR.exists():
        for p in UPLOAD_DIR.iterdir():
            if p.is_file() and p.name != ".gitkeep":
                p.unlink()
            elif p.is_dir():
                shutil.rmtree(p)


def seed_users(db: Session) -> dict[str, models.User]:
    users = {}
    for username, password, role in DEMO_USERS:
        u = models.User(
            username=username,
            hashed_password=auth.get_password_hash(password),
            role=role,
        )
        db.add(u)
        users[username] = u
    db.commit()
    for u in users.values():
        db.refresh(u)
    return users


def seed_cases(db: Session, users: dict[str, models.User]):
    for spec in DEMO_CASES:
        owner = users[spec["owner"]]
        case = models.Case(
            customer=spec["customer"],
            service_type=spec["service_type"],
            status=spec["status"],
            created_at=spec["created_at"],
            created_by=owner.id,
        )
        db.add(case)
        db.flush()  # populate case_id

        # Skip rest if no doc
        if not spec["invoice"]:
            continue

        # Document
        src = TEST_DIR / spec["invoice"]
        if not src.is_file():
            print(f"  ! missing test invoice {src}, skipping document for {spec['customer']}")
            continue

        upload_time = spec["created_at"] + timedelta(minutes=2)
        doc = models.Document(
            case_id=case.case_id,
            doc_type="Invoice",
            file_path="",  # filled after we have doc_id
            upload_time=upload_time,
            uploaded_by=owner.id,
        )
        db.add(doc)
        db.flush()

        # Copy PDF using the same {doc_id}_{name} convention as the live upload endpoint
        dest_name = f"{doc.doc_id}_{spec['invoice']}"
        dest = UPLOAD_DIR / dest_name
        UPLOAD_DIR.mkdir(exist_ok=True)
        shutil.copy(src, dest)
        doc.file_path = str(dest).replace("\\", "/")

        # ExtractedFields (if any)
        if spec["extraction"]:
            approved_at_field = None
            if spec["approved_minutes_after_upload"] is not None:
                approved_at_field = upload_time + timedelta(
                    minutes=spec["approved_minutes_after_upload"]
                )

            audit_field_set = {edit[0] for edit in spec["audit_edits"]}

            for field_name, (value, conf) in spec["extraction"].items():
                approved_value = None
                approved_by = None
                if spec["approved_values"]:
                    approved_value = spec["approved_values"].get(field_name)
                    approved_by = owner.id
                f = models.ExtractedFields(
                    case_id=case.case_id,
                    doc_id=doc.doc_id,
                    field_name=field_name,
                    extracted_value=value,
                    confidence=conf,
                    source_doc=doc.file_path,
                    approved_value=approved_value,
                    approved_by=approved_by,
                    approved_at=approved_at_field,
                    correction_count=1 if field_name in audit_field_set else 0,
                )
                db.add(f)

            # Set the document-level approved_at for KPI 1
            if approved_at_field:
                doc.approved_at = approved_at_field

        # AuditLog entries
        for field_name, old_val, new_val, by_username in spec["audit_edits"]:
            changed_at = upload_time + timedelta(
                minutes=spec["approved_minutes_after_upload"] or 5
            )
            db.add(models.AuditLog(
                case_id=case.case_id,
                doc_id=doc.doc_id,
                field_name=field_name,
                old_value=old_val,
                new_value=new_val,
                changed_by=users[by_username].id,
                changed_at=changed_at,
            ))

    db.commit()


def main():
    print("Initializing schema…")
    models.Base.metadata.create_all(bind=engine)
    run_migrations()

    db = SessionLocal()
    try:
        print("Wiping existing demo data…")
        wipe(db)

        print(f"Seeding {len(DEMO_USERS)} users…")
        users = seed_users(db)

        print(f"Seeding {len(DEMO_CASES)} cases (this may take a moment for bcrypt)…")
        seed_cases(db, users)

        # Counts
        case_count   = db.query(models.Case).count()
        doc_count    = db.query(models.Document).count()
        field_count  = db.query(models.ExtractedFields).count()
        audit_count  = db.query(models.AuditLog).count()
        user_count   = db.query(models.User).count()

        print()
        print("─" * 60)
        print("  Seed complete")
        print("─" * 60)
        print(f"  Users:          {user_count}")
        print(f"  Cases:          {case_count}")
        print(f"  Documents:      {doc_count}")
        print(f"  Extracted rows: {field_count}")
        print(f"  Audit entries:  {audit_count}")
        print("─" * 60)
        print()
        print("  Login credentials:")
        for username, password, role in DEMO_USERS:
            print(f"    {username:10s}  /  {password:18s}  ({role})")
        print()
        print("  Suggested demo flow:")
        print("    1. Log in as `linah` to see the admin dashboard with full KPIs.")
        print("    2. Log in as `bayader` (staff) to upload + extract + approve.")
        print("    3. Log in as `viewer` to see the read-only view (no delete).")
        print()
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
