from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class ContactCreate(BaseModel):
    account_id: UUID
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class ContactOut(BaseModel):
    id: UUID
    account_id: UUID
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True
