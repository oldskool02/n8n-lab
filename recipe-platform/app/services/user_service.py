from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate
from app.security import hash_password


def create_user_service(
    db: Session,
    data: UserCreate,
):
    """
    Create a new user in the database.

    Args:
        db (Session): SQLAlchemy database session.
        data (UserCreate): Data for creating a new user.

    Returns:
        User: The created user object.
    """

    password_hash = hash_password(data.password)

    user = User(
        email=data.email,
        password_hash=password_hash,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

    except Exception:
        db.rollback()
        raise

    return user
