from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base
import uuid


class Firm(Base):
    __tablename__ = "firms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firm_name = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    drive_generated_folder_id = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class SystemTemplate(Base):
    __tablename__ = "system_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_name = Column(String, unique=True, nullable=False)
    document_type = Column(String, nullable=False)
    google_doc_template_id = Column(String, nullable=False)
    version = Column(Integer, default=1)
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firm_id = Column(UUID(as_uuid=True), ForeignKey("firms.id"))
    template_id = Column(UUID(as_uuid=True), ForeignKey("system_templates.id"))
    google_doc_id = Column(String)
    document_name = Column(String)
    status = Column(String)
    request_ip = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())