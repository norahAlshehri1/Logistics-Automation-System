from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from database import Base

class Case(Base):
    __tablename__ = "cases"

    case_id = Column(Integer, primary_key=True, index=True)
    customer = Column(String, nullable=False)
    service_type = Column(String)
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column(Integer)

    documents = relationship("Document", back_populates="case")


class Document(Base):
    __tablename__ = "documents"

    doc_id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.case_id"))
    doc_type = Column(String)
    file_path = Column(String, nullable=False)
    upload_time = Column(DateTime, default=datetime.datetime.utcnow)
    uploaded_by = Column(Integer)

    case = relationship("Case", back_populates="documents")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)


class ExtractedFields(Base):
    __tablename__ = "extracted_fields"

    field_id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.case_id"))
    field_name = Column(String, nullable=False)
    extracted_value = Column(String)
    confidence = Column(String, default="High")
    source_doc = Column(String)
    approved_value = Column(String)
    approved_by = Column(Integer)
    approved_at = Column(DateTime)

    case = relationship("Case")