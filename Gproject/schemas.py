from pydantic import BaseModel
from datetime import datetime

class CaseCreate(BaseModel):
    customer: str
    service_type: str
    created_by: int

class CaseResponse(BaseModel):
    case_id: int
    customer: str
    service_type: str
    status: str
    created_at: datetime
    created_by: int

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str