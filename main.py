from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import models, schemas, auth
from database import engine, SessionLocal
import shutil
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Logistics Paperwork Automation System")

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
    
    return {"message": "Document uploaded successfully", "filename": file.filename}