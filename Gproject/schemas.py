from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# ── Auth ─────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True


# ── Cases ─────────────────────────────────────────────────────────────────────

class CaseCreate(BaseModel):
    customer: str
    service_type: str

class CaseResponse(BaseModel):
    case_id: int
    customer: str
    service_type: str
    status: str
    created_at: datetime
    created_by: Optional[int]

    class Config:
        from_attributes = True


# ── Documents ─────────────────────────────────────────────────────────────────

class DocumentResponse(BaseModel):
    doc_id: int
    case_id: int
    doc_type: Optional[str]
    file_path: str
    upload_time: Optional[datetime]

    class Config:
        from_attributes = True


# ── Extracted Fields ──────────────────────────────────────────────────────────

class ExtractedFieldResponse(BaseModel):
    field_id: int
    field_name: str
    extracted_value: Optional[str]
    approved_value: Optional[str]
    confidence: Optional[str]
    approved_at: Optional[datetime]

    class Config:
        from_attributes = True


class ApprovedData(BaseModel):
    Vendor_Name: Optional[str] = Field(None, alias="Vendor Name")
    Invoice_Number: Optional[str] = Field(None, alias="Invoice Number")
    Shipment_Date: Optional[str] = Field(None, alias="Shipment Date")
    Total_Amount: Optional[str] = Field(None, alias="Total Amount")

    class Config:
        populate_by_name = True


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardSummary(BaseModel):
    total_cases: int
    total_documents: int
    pending_review: int
    approved: int
    status_distribution: dict
    recent_cases: list
