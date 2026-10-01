from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.services.recipe_service import (
    delete_recipe_service,
    get_user_recipes,
)
from app.schemas import UserCreate, UserLogin
from app.security import hash_password, verify_password


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


def authenticate_user_service(
    db: Session,
    data: UserLogin,
):
    """
    Authenticate a user by verifying their email and password.

    Args:
        db (Session): SQLAlchemy database session.
        data (UserLogin): Data for user login.
    """

    statement = select(User).where(
        User.email == data.email
    )

    result = db.execute(statement)
    user = result.scalar_one_or_none()

    if user is None:
        return None

    if not verify_password(
        data.password,
        user.password_hash,
    ):
        return None

    return user


def delete_user_service(
    db: Session,
    user: User,
):
    recipes = get_user_recipes(
        db,
        user.id,
    )

    for recipe in recipes:
        delete_recipe_service(
            db,
            user.id,
            recipe.id,
        )

    try:
        db.delete(user)
        db.commit()

    except Exception:
        db.rollback()
        raise
