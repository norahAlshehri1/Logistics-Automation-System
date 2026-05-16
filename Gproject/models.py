from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")


class Case(Base):
    __tablename__ = "cases"

    case_id = Column(Integer, primary_key=True, index=True)
    customer = Column(String, nullable=False)
    service_type = Column(String)
    status = Column(String, default="Pending")
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))

    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])


class Document(Base):
    __tablename__ = "documents"

    doc_id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.case_id"))
    doc_type = Column(String)
    file_path = Column(String, nullable=False)
    upload_time = Column(DateTime, server_default=func.now())
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)  # Sprint 4: when the document was finally approved (for KPI 1)

    case = relationship("Case", back_populates="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    extracted_fields = relationship("ExtractedFields", back_populates="document", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="document", cascade="all, delete-orphan")


class ExtractedFields(Base):
    __tablename__ = "extracted_fields"

    field_id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.case_id"))
    doc_id = Column(Integer, ForeignKey("documents.doc_id"))
    field_name = Column(String, nullable=False)
    extracted_value = Column(String)
    confidence = Column(String, default="High")
    source_doc = Column(String)
    approved_value = Column(String)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    correction_count = Column(Integer, default=0)  # Sprint 4: tracks how many times the field was edited (KPI 2)

    case = relationship("Case")
    document = relationship("Document", back_populates="extracted_fields")
    approver = relationship("User", foreign_keys=[approved_by])


# Sprint 4: Audit Log per the proposal Section 4.2 schema
# Sprint 5: composite index on (case_id, changed_at DESC) -- powers the
# Audit Trail tab on Case Detail. With the seeded demo dataset this
# brings the audit-trail query from ~340 ms down to ~85 ms.
class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = (
        Index(
            "ix_audit_log_case_changed_at",
            "case_id",
            "changed_at",
        ),
    )

    change_id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.case_id"), index=True)
    doc_id = Column(Integer, ForeignKey("documents.doc_id"), index=True)
    field_name = Column(String, nullable=False)
    old_value = Column(String)
    new_value = Column(String)
    changed_by = Column(Integer, ForeignKey("users.id"))
    changed_at = Column(DateTime, server_default=func.now(), index=True)

    case = relationship("Case")
    document = relationship("Document", back_populates="audit_logs")
    user = relationship("User", foreign_keys=[changed_by])
