from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class InteractionCreate(BaseModel):
    account_id: UUID
    contact_id: Optional[UUID] = None
    user_id: UUID
    type: str
    notes: Optional[str] = None
    interaction_date: Optional[str] = None
    next_action: Optional[str] = None


class InteractionOut(BaseModel):
    id: UUID
    account_id: UUID
    contact_id: Optional[UUID] = None
    user_id: UUID
    type: str
    notes: Optional[str]
    next_action: Optional[str]

    # NEW (optional later)
    user_name: Optional[str]
    contact_name: Optional[str] = None

    class Config:
        from_attributes = True
