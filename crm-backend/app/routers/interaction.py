from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.models.interaction import Interaction
from app.models.contact import Contact
from app.schemas.interaction import InteractionCreate, InteractionOut
from app.models.account import Account
from app.models.user import User

router = APIRouter(
    prefix="/interactions", 
    tags=["interactions"]
)


@router.post("/")
def create_interaction(interaction: InteractionCreate, db: Session = Depends(get_db)):
    new_interaction = Interaction(**interaction.dict())
    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)
    return new_interaction


@router.get("/", response_model=list[InteractionOut])
def list_interactions(db: Session = Depends(get_db)):
    results = (
        db.query(Interaction, Contact)
        .outerjoin(Contact, Interaction.contact_id == Contact.id)
        .all()
    )

    output = []

    for interaction, contact in results:
        output.append({
            "id": interaction.id,
            "account_id": interaction.account_id,
            "contact_id": interaction.contact_id,
            "user_id": interaction.user_id,
            "type": interaction.type,
            "notes": interaction.notes,
            "next_action": interaction.next_action,
            "contact_name": f"{contact.first_name} {contact.last_name}" if contact else None
        })

    return output


from datetime import datetime

@router.get("/follow-ups")
def get_follow_ups(db: Session = Depends(get_db)):

    now = datetime.utcnow()

    interactions = (
        db.query(Interaction, Contact, Account, User)
        .join(Contact, Interaction.contact_id == Contact.id)
        .join(Account, Interaction.account_id == Account.id)
        .join(User, Interaction.user_id == User.id)
        .filter(Interaction.follow_up_date != None)
        .filter(Interaction.follow_up_date <= now)
        .order_by(Interaction.follow_up_date.asc())
        .all()
    )

    result = []

    for interaction, contact, account, user in interactions:
        result.append({
            "account_name": account.company_name,
            "contact_name": f"{contact.first_name} {contact.last_name}",
            "user_name": user.name,
            "notes": interaction.notes,
            "next_action": interaction.next_action,
            "follow_up_date": interaction.follow_up_date
        })

    return result
