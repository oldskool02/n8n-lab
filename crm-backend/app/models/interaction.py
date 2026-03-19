from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)

    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    type = Column(Text)     # call, email, meeting, note, etc.

    notes = Column(Text)

    interaction_date = Column(DateTime, server_default=func.now())

    next_action = Column(Text)

    created_at = Column(DateTime, server_default=func.now())

    account = relationship("Account", back_populates="interactions")

    follow_up_date = Column(DateTime(timezone=True), nullable=True)
