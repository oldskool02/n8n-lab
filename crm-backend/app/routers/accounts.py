from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship
from uuid import UUID
from datetime import datetime, timedelta


from app.dependencies.database import get_db
from app.models import Account, Interaction, Contact, User
from app.schemas.account import AccountCreate, AccountFull
from app.schemas.interaction import InteractionOut
from typing import List


router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"]
)

# temporary in-memory list for testing
accounts = []

@router.get("/")
def list_accounts(db: Session = Depends(get_db)):
    return db.query(Account).all()


@router.post("/")
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    new_account = Account(**account.dict())
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


@router.get("/{account_id}/interactions", response_model=List[InteractionOut])
def get_account_interactions(account_id: UUID, db: Session = Depends(get_db)):
    return (
        db.query(Interaction)
        .filter(Interaction.account_id == account_id)
        .order_by(Interaction.interaction_date.desc())
        .all()
    )


@router.get("/{account_id}/full-view", response_model=AccountFull)
def get_account_full(account_id: UUID, db: Session = Depends(get_db)):

    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    contacts = (
        db.query(Contact)
        .filter(Contact.account_id == account_id)
        .all()
    )

    interactions_query  = (
        db.query(Interaction, Contact, User)
        .outerjoin(Contact, Interaction.contact_id == Contact.id)
        .outerjoin(User, Interaction.user_id == User.id)
        .filter(Interaction.account_id == account_id)
        .order_by(Interaction.interaction_date.desc())
        .all()
    )

    formatted_interactions = []

    for interaction, contact, user in interactions_query:
        formatted_interactions.append({
            "id": interaction.id,
            "account_id": interaction.account_id,
            "contact_id": interaction.contact_id,
            "user_id": interaction.user_id,
            "type": interaction.type,
            "notes": interaction.notes,
            "next_action": interaction.next_action,
            "contact_name": f"{contact.first_name} {contact.last_name}" if contact else None,
            "user_name": user.name if user else None
        })

    last_interaction = formatted_interactions[0] if formatted_interactions else None
    
    return {
        "id": account.id,
        "name": account.company_name,
        "contacts": contacts,
        "interactions": formatted_interactions,
        "last_interaction": last_interaction
    }


@router.get("/no-contact")
def get_accounts_no_contact(days: int = 30, db: Session = Depends(get_db)):

    accounts = db.query(Account).all()

    result = []

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    for account in accounts:

        last_interaction = (
            db.query(Interaction)
            .filter(Interaction.account_id == account.id)
            .order_by(Interaction.interaction_date.desc())
            .first()
        )

        # ❗ Case 1: No interactions at all
        if not last_interaction:
            result.append({
                "account_id": account.id,
                "name": account.company_name,
                "last_interaction": None,
                "days_since_last_contact": None
            })
            continue

        # ❗ Case 2: Interaction exists but is too old
        days_since = (datetime.utcnow() - last_interaction.interaction_date).days

        if days_since > days:
            result.append({
                "account_id": account.id,
                "name": account.company_name,
                "last_interaction": last_interaction.interaction_date,
                "days_since_last_contact": days_since
            })

    result = sorted(
        result, 
        key=lambda x: x["days_since_last_contact"] or 0, 
        reverse=True
    )

    return result


from datetime import datetime

@router.get("/priority")
def get_priority_accounts(limit: int = 10, db: Session = Depends(get_db)):

    accounts = db.query(Account).all()

    result = []

    for account in accounts:

        last_interaction = (
            db.query(Interaction)
            .filter(Interaction.account_id == account.id)
            .order_by(Interaction.interaction_date.desc())
            .first()
        )

        # Calculate days since contact
        if last_interaction:
            days_since = (datetime.utcnow() - last_interaction.interaction_date).days
        else:
            days_since = None

        result.append({
            "account_id": account.id,
            "name": account.company_name,
            "last_interaction": last_interaction.interaction_date if last_interaction else None,
            "days_since_last_contact": days_since
        })

        result = sorted(
            result,
            key=lambda x: x["days_since_last_contact"] if x["days_since_last_contact"] is not None else 9999,
            reverse=True
    )
    return result[:limit]
