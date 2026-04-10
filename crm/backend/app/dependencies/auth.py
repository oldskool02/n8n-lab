from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from uuid import UUID

from app.dependencies.database import get_db
from app.models.user import User

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        print("TOKEN RECEIVED:", token)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("PAYLOAD:", payload)

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # 👇 PUT IT RIGHT HERE
    print("USER ID FROM TOKEN:", user_id)

    users = db.query(User).all()
    print("DB USERS:", [str(u.id) for u in users])

    user = next((u for u in users if str(u.id) == str(user_id)), None)

    if not user:
        print("USER NOT FOUND IN DB")
        raise HTTPException(status_code=401, detail="User not found")

    return user
