from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
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

    case = relationship("Case", back_populates="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    extracted_fields = relationship("ExtractedFields", back_populates="document", cascade="all, delete-orphan")


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

    case = relationship("Case")
    document = relationship("Document", back_populates="extracted_fields")
    approver = relationship("User", foreign_keys=[approved_by])
