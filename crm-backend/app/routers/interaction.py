from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone
from uuid import UUID

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
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

    if not interaction.follow_up_date:
        raise HTTPException(status_code=400, detail="follow_up_date is required")

    if not interaction.next_action:
        raise HTTPException(status_code=400, detail="next_action is required")

    new_interaction = Interaction(**interaction.dict())

    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)

    return new_interaction

@router.get("/", response_model=list[InteractionOut])
def list_interactions(db: Session = Depends(get_db)):
    results = (
        db.query(Interaction, Contact, User, Account)
        .outerjoin(Contact, Interaction.contact_id == Contact.id)
        .join(User, Interaction.user_id == User.id)
        .join(Account, Interaction.account_id == Account.id)
        .all()
    )

    output = []

    for interaction, contact, user, account in results:
        output.append({
            "id": interaction.id,
            "account_id": interaction.account_id,
            "account_name": account.company_name,
            "contact_id": interaction.contact_id,
            "contact_name": (
                f"{contact.first_name} {contact.last_name}")
                if contact else None,
            "user_id": interaction.user_id,
            "user_name": user.name,
            "type": interaction.type,
            "notes": interaction.notes,
            "next_action": interaction.next_action
            "follow_up_date": interaction.follow_up_date
            })

    return output


from datetime import datetime

@router.get("/follow-ups")
def get_follow_ups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):

    query = db.query(Interaction, Contact, Account, User)

    now = datetime.utcnow()

    if current_user.role == "rep":
        query = query.filter(Interaction.user_id == current_user.id)

    interactions = (
        db.query(Interaction, Contact, Account, User)
        .outerjoin(Contact, Interaction.contact_id == Contact.id)
        .join(Account, Interaction.account_id == Account.id)
        .join(User, Interaction.user_id == User.id)
        .filter(Interaction.follow_up_date != None)
        .filter(Interaction.status == "pending")
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

# @router.post("/{interaction_id}/complete")
# def complete_interaction(interaction_id: str, db: Session = Depends(get_db)):

#     # Validate UUID
#     try:
#         interaction_uuid = UUID(interaction_id)
#     except:
#         raise HTTPException(status_code=400, detail="Invalid UUID")
    
#     # Fetch interaction
#     interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()

#     if not interaction:
#         raise HTTPException(status_code=404, detail="Interaction not found")

#     # Debug
#     if interaction.status == "completed":
#         return {"message": "Already completed"}

#     # Update
#     interaction.status = "completed"
#     interaction.completed_at = datetime.utcnow()

#     print("After", interaction.status)

#     return {"message": "Follow-up marked as complete"}

@router.get("/my-follow-ups")
def my_follow_ups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    now = datetime.now(timezone.utc)

    interactions = (
        db.query(Interaction)
        .filter(Interaction.user_id == current_user.id)
        .filter(Interaction.follow_up_date != None)
        .filter(Interaction.follow_up_date <= now)
        .filter(Interaction.status.in_(["pending", "in_progress", "late"]))
        .all()
    )

    result = []

    for interaction in interactions:
        is_late = (
            interaction.follow_up_date is not None and
            interaction.follow_up_date <= now and
            interaction.status != "completed"
        )

        result.append({
            "id": interaction.id,
            "account_name": interaction.account.company_name,
            "contact_name": interaction.contact.first_name + " " + interaction.contact.last_name,
            "user_name": interaction.user.name,
            "user_email": interaction.user.email,
            "notes": interaction.notes,
            "next_action": interaction.next_action,
            "follow_up_date": interaction.follow_up_date,
            "status": interaction.status,
            "is_late": is_late
        })

    return result

@router.patch("/{interaction_id}/start")
def start_interaction(interaction_id: str, db: Session = Depends(get_db)):
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()

    if not interaction:
        raise HTTPException(status_code=404, detail="Not found")
    
    interaction.status = "in_progress"
    db.commit()

    return {"message": "Interaction started"}

@router.patch("/{interaction_id}/complete")
def complete_interaction(
    interaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    interaction = (
        db.query(Interaction)
        .filter(Interaction.id == interaction_id)
        .filter(Interaction.user_id == current_user.id)
        .first()
    )

    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    
    interaction.status = "completed"
    interaction.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(interaction)

    return {"message", "Interaction marked as completed"}

@router.get("/{interaction_id}")
def get_interaction(
    interaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    interaction = (
        db.query(Interaction)
        .options(
        joinedload(Interaction.account),
        joinedload(Interaction.contact)
    )
        .filter(Interaction.id == interaction_id)
        .filter(Interaction.user_id == current_user.id)
        .first()
    )

    if not interaction:
        raise HTTPException(status_code=404, detail="Not found")
    
    return {
        "id": interaction.id,
        "account_name": interaction.account.company_name,
        "contact_name": (
            f"{interaction.contact.first_name} {interaction.contact.last_name}"
            if interaction.contact else None
        ),
        "notes": interaction.notes,
        "status": interaction.status,
        "follow_up_date": interaction.follow_up_date,
        "next_action": interaction.next_action
    }