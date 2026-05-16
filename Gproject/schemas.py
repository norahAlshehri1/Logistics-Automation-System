from pydantic import AliasGenerator, BaseModel, ConfigDict
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


def _space_alias(field_name: str) -> str:
    """Convert ``Vendor_Name`` → ``Vendor Name`` for JSON wire compatibility."""
    return field_name.replace("_", " ")


class ApprovedData(BaseModel):
    # Sprint 5: use an AliasGenerator on the model config. Pydantic 2.13
    # raises UnsupportedFieldAttributeWarning when `alias=` is applied to
    # `Optional[str]` fields directly; the generator approach is the
    # supported idiom that produces the same wire format ("Vendor Name",
    # "Invoice Number", ...).
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=AliasGenerator(
            validation_alias=_space_alias,
            serialization_alias=_space_alias,
        ),
    )

    Vendor_Name:    Optional[str] = None
    Invoice_Number: Optional[str] = None
    Shipment_Date:  Optional[str] = None
    Total_Amount:   Optional[str] = None


# ── Sprint 4 — Audit Log ──────────────────────────────────────────────────────

class AuditLogResponse(BaseModel):
    change_id: int
    case_id: Optional[int]
    doc_id: Optional[int]
    field_name: str
    old_value: Optional[str]
    new_value: Optional[str]
    changed_by: Optional[int]
    changed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardSummary(BaseModel):
    total_cases: int
    total_documents: int
    pending_review: int
    approved: int
    status_distribution: dict
    recent_cases: list


# Sprint 4 — KPI tracking against proposal targets
class KPIReport(BaseModel):
    avg_processing_time_minutes: Optional[float]
    processing_time_target_pct: float
    processing_time_improvement_pct: Optional[float]

    correction_rate_per_case: Optional[float]
    correction_rate_target_pct: float
    correction_rate_improvement_pct: Optional[float]

    completeness_rate_pct: Optional[float]
    completeness_target_pct: float

    approved_documents: int
    sample_size: int
