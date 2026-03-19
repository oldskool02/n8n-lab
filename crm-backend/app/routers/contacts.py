from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.dependencies.database import get_db
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactOut

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"]
)


@router.post("/", response_model=ContactOut)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    new_contact = Contact(**contact.dict())
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


@router.get("/", response_model=List[ContactOut])
def list_contacts(db: Session = Depends(get_db)):
    return db.query(Contact).all()


@router.get("/{account_id}/contacts", response_model=List[ContactOut])
def get_contacts(account_id: UUID, db: Session = Depends(get_db)):
    return (
        db.query(Contact)
        .filter(Contact.account_id == account_id)
        .all()
    )
