from sqlalchemy.orm import Session
from models import Firm
from fastapi import HTTPException


def validate_api_key(db: Session, api_key: str):
    firm = db.query(Firm).filter(Firm.api_key == api_key).first()

    if not firm or not firm.active:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return firm