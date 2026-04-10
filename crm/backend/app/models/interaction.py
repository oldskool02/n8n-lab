from sqlalchemy import Column, Text, DateTime, ForeignKey, String, Enum, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base

class Interaction(Base):
    __tablename__ = "interactions"

    __table_args__ = (
        Index("idx_follow_up_status", 
              "follow_up_date", 
              postgresql_where=text("status = 'pending'")
              ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)

    account = relationship("Account", back_populates="interactions")

    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=True)

    contact = relationship("Contact", back_populates="interactions")

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="interactions")

    type = Column(String)     # call, email, meeting, note, etc.

    notes = Column(Text)

    interaction_date = Column(DateTime, server_default=func.now())

    next_action = Column(Text)

    created_at = Column(DateTime, server_default=func.now())

    follow_up_date = Column(DateTime(timezone=True), nullable=True)

    status = Column(
        Enum("pending", 
             "in_progress",
             "late",
             "completed", 
             name="interaction_status"
        ),
        default="pending"
    )  # pending, completed, etc.

    completed_at = Column(DateTime(timezone=True), nullable=True)
