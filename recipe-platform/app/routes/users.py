from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    RefreshTokenRequest,
)
from app.services.user_service import (
    authenticate_user_service,
    create_user_service,
)
from app.security import create_access_token
from app.services.auth_service import (
    create_refresh_session,
    get_session_for_refresh,
    update_refresh_session_activity,
    revoke_refresh_session,
    get_session_for_logout,
)


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", response_model=UserResponse)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    return create_user_service(db, data)


@router.post("/login")
def login(
    data: UserLogin,
    db: Session = Depends(get_db),
):
    user = authenticate_user_service(db, data)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_session(db, user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
def refresh_access_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    session = get_session_for_refresh(
        db,
        data.refresh_token,
    )

    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    update_refresh_session_activity(db, session)

    access_token = create_access_token(session.user_id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    session = get_session_for_logout(
        db,
        data.refresh_token,
    )

    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    revoke_refresh_session(db, session)

    return {
        "message": "Successfully logged out",
    }
