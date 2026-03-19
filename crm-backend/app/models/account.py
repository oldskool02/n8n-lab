from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

import uuid

from app.database import Base

class Account(Base):

    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    company_name = Column(Text, nullable=False)

    industry = Column(Text)

    website = Column(Text)
    
    address = Column(Text)
    
    assigned_rep = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    created_at = Column(DateTime, server_default=func.now())

    interactions = relationship("Interaction", back_populates="account")
