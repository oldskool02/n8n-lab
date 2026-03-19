from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)

    first_name = Column(String, nullable=False)

    last_name = Column(String, nullable=True)

    email = Column(String)

    phone = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
