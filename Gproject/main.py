from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware # تم إضافة هذا السطر الهام جداً
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import models, schemas, auth
from database import engine, SessionLocal
import shutil
import os
from extractor import extract_invoice_data

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Logistics Paperwork Automation System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

os.makedirs("uploaded_docs", exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register/")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pwd = auth.get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/login/", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/cases/", response_model=schemas.CaseResponse)
def create_case(case: schemas.CaseCreate, db: Session = Depends(get_db)):
    db_case = models.Case(
        customer=case.customer,
        service_type=case.service_type,
        created_by=case.created_by
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

@app.get("/cases/", response_model=list[schemas.CaseResponse])
def read_cases(db: Session = Depends(get_db)):
    return db.query(models.Case).all()

@app.put("/cases/{case_id}")
def update_case_status(case_id: int, new_status: str, db: Session = Depends(get_db)):
    db_case = db.query(models.Case).filter(models.Case.case_id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    db_case.status = new_status
    db.commit()
    db.refresh(db_case)
    return {"message": "Case updated successfully", "case": db_case}

@app.delete("/cases/{case_id}")
def delete_case(case_id: int, db: Session = Depends(get_db)):
    db_case = db.query(models.Case).filter(models.Case.case_id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    db.delete(db_case)
    db.commit()
    return {"message": "Case deleted successfully"}

@app.post("/cases/{case_id}/documents/")
def upload_document(case_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_case = db.query(models.Case).filter(models.Case.case_id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")

    file_location = f"uploaded_docs/{file.filename}"
    with open(file_location, "wb+") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    db_doc = models.Document(
        case_id=case_id,
        doc_type="Uploaded File",
        file_path=file_location,
        uploaded_by=1
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc) # تم إضافة هذا السطر لمعرفة رقم المستند الجديد
    
    # تم تعديل الإرجاع ليتضمن رقم المستند لكي تقرأه واجهة React
    return {
        "message": "Document uploaded successfully", 
        "filename": file.filename,
        "document_id": db_doc.doc_id 
    }

@app.post("/documents/{document_id}/extract")
def extract_data_from_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(models.Document).filter(models.Document.doc_id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        extraction_result = extract_invoice_data(document.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading document: {str(e)}")

    for field_name, value in extraction_result.items():
        db_field = models.ExtractedFields(
            case_id=document.case_id,
            field_name=field_name,
            extracted_value=value,
            source_doc=document.file_path
        )
        db.add(db_field)
    
    db.commit()

    return {
        "message": "Data extracted and saved successfully",
        "document_id": document.doc_id,
        "extracted_data": extraction_result
    }

# تعريف هيكل البيانات القادمة من الواجهة بشكل صحيح
class ApprovedData(BaseModel):
    Vendor_Name: str = Field(None, alias="Vendor Name")
    Invoice_Number: str = Field(None, alias="Invoice Number")
    Shipment_Date: str = Field(None, alias="Shipment Date")
    Total_Amount: str = Field(None, alias="Total Amount")

    class Config:
        populate_by_name = True

@app.put("/documents/{document_id}/approve")
def approve_extracted_data(document_id: int, data: ApprovedData, db: Session = Depends(get_db)):
    fields = db.query(models.ExtractedFields).filter(
        models.ExtractedFields.source_doc.contains(str(document_id))
    ).all()
    
    data_dict = data.dict(by_alias=True)
    for field in fields:
        if field.field_name in data_dict:
            field.approved_value = data_dict[field.field_name]
            field.approved_by = 1 
    
    db.commit()
    return {"message": "Data approved and saved successfully"}