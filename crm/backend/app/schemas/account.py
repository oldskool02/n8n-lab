from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

from app.schemas.contact import ContactOut
from app.schemas.interaction import InteractionOut

class AccountCreate(BaseModel):
    company_name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    assigned_rep: Optional[UUID] = None


class AccountResponse(BaseModel):
    id: UUID
    company_name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    assigned_rep: Optional[UUID] = None

    class Config:
        from_attributes = True


class AccountFull(BaseModel):
    id: UUID
    name: str

    contacts: List[ContactOut]
    interactions: List[InteractionOut]
    last_interaction: Optional[InteractionOut] = None

    class Config:
        from_attributes = True
