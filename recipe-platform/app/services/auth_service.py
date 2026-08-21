from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import REFRESH_TOKEN_EXPIRE_DAYS
from app.models import RefreshSession
from app.security import (
    create_refresh_token,
    hash_refresh_token,
)


def create_refresh_session(
    db: Session,
    user_id: int,
):
    """
    Create a new refresh session for the user.

    Returns:
        str: The refresh token to be given to the client.
    """
    refresh_token = create_refresh_token()
    token_hash = hash_refresh_token(refresh_token)

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    session = RefreshSession(
        user_id=user_id,
        token_hash=token_hash,
        created_at=now,
        last_activity_at=now,
        expires_at=expires_at,
    )

    try:
        db.add(session)
        db.commit()
        db.refresh(session)

    except Exception:
        db.rollback()
        raise

    return refresh_token


def get_session_for_logout(
    db: Session,
    token: str,
):
    """
    Get a refresh session by the token.

    Returns:
        RefreshSession | None: The refresh session if found, else None.
    """
    token_hash = hash_refresh_token(token)

    statement = select(RefreshSession).where(
        RefreshSession.token_hash == token_hash
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()


def validate_refresh_session(
    session: RefreshSession,
) -> bool:
    """
    Check whether the refresh session is still valid.

    Returns:
        bool: True if the session is active and not expired
    """
    now = datetime.now(timezone.utc)

    if session.revoked_at is not None:
        return False

    if session.expires_at <= now:
        return False

    return True


def revoke_refresh_session(
    db: Session,
    session: RefreshSession,
):
    """
    Revoke a refresh session.

    This will mark the session as revoked and prevent it from being used again.
    Sets the revoked_at timestamp to the current UTC time.
    """
    session.revoked_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(session)

    except Exception:
        db.rollback()
        raise


def get_session_for_refresh(
    db: Session,
    token: str,
):
    """
    Get a valid refresh session for the supplied token

    Returns:
        RefreshSession | None: The valid session if found, else None
    """

    session = get_session_for_logout(db, token)

    if session is None:
        return None

    if not validate_refresh_session(session):
        return None

    return session


def update_refresh_session_activity(
    db: Session,
    session: RefreshSession,
):
    """
    Update the last activity time for a refresh token
    """
    session.last_activity_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(session)

    except Exception:
        db.rollback()
        raise
