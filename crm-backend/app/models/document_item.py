from sqlalchemy import Column, Integer, Float, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database import Base

class DocumentItem(Base):
    __tablename__ = "document_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))

    product_name = Column(Text)

    quantity = Column(Integer)

    price = Column(Float)