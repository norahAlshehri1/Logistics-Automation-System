from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from pathlib import Path
from datetime import datetime, timezone
import shutil
import os

import models
import schemas
import auth
from database import engine, get_db, run_migrations
from extractor import extract_invoice_data

# ── Startup ───────────────────────────────────────────────────────────────────

models.Base.metadata.create_all(bind=engine)
run_migrations()

os.makedirs("uploaded_docs", exist_ok=True)

app = FastAPI(title="Logistics Paperwork Automation System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.post("/register/", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    hashed = auth.get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login/", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me/", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


# ── Cases ─────────────────────────────────────────────────────────────────────

@app.post("/cases/", response_model=schemas.CaseResponse)
def create_case(
    case: schemas.CaseCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_case = models.Case(
        customer=case.customer,
        service_type=case.service_type,
        created_by=current_user.id
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case


@app.get("/cases/", response_model=list[schemas.CaseResponse])
def read_cases(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Case).order_by(models.Case.created_at.desc()).all()


@app.get("/cases/{case_id}", response_model=schemas.CaseResponse)
def get_case(
    case_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_case = db.query(models.Case).filter(models.Case.case_id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")
    return db_case


@app.put("/cases/{case_id}", response_model=schemas.CaseResponse)
def update_case_status(
    case_id: int,
    new_status: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    allowed = {"Pending", "In Review", "Approved", "Closed"}
    if new_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Status must be one of: {', '.join(sorted(allowed))}"
        )
    db_case = db.query(models.Case).filter(models.Case.case_id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")
    db_case.status = new_status
    db.commit()
    db.refresh(db_case)
    return db_case


@app.delete("/cases/{case_id}")
def delete_case(
    case_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_case = db.query(models.Case).filter(models.Case.case_id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")
    db.delete(db_case)
    db.commit()
    return {"message": "Case deleted successfully"}


# ── Documents ─────────────────────────────────────────────────────────────────

@app.get("/cases/{case_id}/documents/", response_model=list[schemas.DocumentResponse])
def get_case_documents(
    case_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_case = db.query(models.Case).filter(models.Case.case_id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")
    return db.query(models.Document).filter(models.Document.case_id == case_id).all()


@app.post("/cases/{case_id}/documents/")
def upload_document(
    case_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_case = db.query(models.Case).filter(models.Case.case_id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Sanitize filename to prevent path traversal
    safe_name = Path(file.filename).name
    file_location = f"uploaded_docs/{safe_name}"

    with open(file_location, "wb+") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_doc = models.Document(
        case_id=case_id,
        doc_type="Invoice",
        file_path=file_location,
        uploaded_by=current_user.id
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    return {
        "message": "Document uploaded successfully",
        "filename": safe_name,
        "document_id": db_doc.doc_id
    }


# ── Extraction ────────────────────────────────────────────────────────────────

@app.post("/documents/{document_id}/extract")
def extract_data_from_document(
    document_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    document = db.query(models.Document).filter(models.Document.doc_id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Clear any previous extraction for this document
    db.query(models.ExtractedFields).filter(
        models.ExtractedFields.doc_id == document_id
    ).delete()

    try:
        result = extract_invoice_data(document.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")

    confidence = result.pop("confidence_score", "Low")
    language = result.pop("language", "unknown")

    for field_name, value in result.items():
        db_field = models.ExtractedFields(
            case_id=document.case_id,
            doc_id=document_id,
            field_name=field_name,
            extracted_value=str(value) if value is not None else None,
            confidence=confidence,
            source_doc=document.file_path
        )
        db.add(db_field)

    db.commit()

    return {
        "message": "Data extracted and saved successfully",
        "document_id": document_id,
        "extracted_data": result,
        "confidence_score": confidence,
        "language": language
    }


@app.get("/documents/{document_id}/fields", response_model=list[schemas.ExtractedFieldResponse])
def get_document_fields(
    document_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.ExtractedFields).filter(
        models.ExtractedFields.doc_id == document_id
    ).all()


# ── Approval ──────────────────────────────────────────────────────────────────

@app.put("/documents/{document_id}/approve")
def approve_extracted_data(
    document_id: int,
    data: schemas.ApprovedData,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    document = db.query(models.Document).filter(models.Document.doc_id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    fields = db.query(models.ExtractedFields).filter(
        models.ExtractedFields.doc_id == document_id
    ).all()

    data_dict = data.model_dump(by_alias=True)
    now = datetime.now(timezone.utc)

    for field in fields:
        if field.field_name in data_dict and data_dict[field.field_name] is not None:
            field.approved_value = data_dict[field.field_name]
            field.approved_by = current_user.id
            field.approved_at = now

    db.commit()
    return {"message": "Data approved and saved successfully"}


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.get("/dashboard/summary")
def get_dashboard_summary(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    total_cases = db.query(func.count(models.Case.case_id)).scalar() or 0
    total_docs = db.query(func.count(models.Document.doc_id)).scalar() or 0

    status_rows = (
        db.query(models.Case.status, func.count(models.Case.case_id))
        .group_by(models.Case.status)
        .all()
    )
    status_dist = {s: c for s, c in status_rows}

    pending = status_dist.get("Pending", 0)
    approved = status_dist.get("Approved", 0)

    recent = (
        db.query(models.Case)
        .order_by(models.Case.created_at.desc())
        .limit(5)
        .all()
    )
    recent_cases = [
        {
            "case_id": c.case_id,
            "customer": c.customer,
            "service_type": c.service_type,
            "status": c.status,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in recent
    ]

    return {
        "total_cases": total_cases,
        "total_documents": total_docs,
        "pending_review": pending,
        "approved": approved,
        "status_distribution": status_dist,
        "recent_cases": recent_cases,
    }
