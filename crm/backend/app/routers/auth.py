from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies.database import get_db
from app.models.user import User
from app.core.security import create_access_token


router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or user.password_hash != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({
        "sub": str(user.id),
        "role": user.role
    })

    return {
        "access_token": token, 
        "token_type": "bearer"}
