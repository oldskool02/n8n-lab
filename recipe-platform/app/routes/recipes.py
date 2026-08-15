from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import RecipeCreate, RecipeResponse
from app.services.recipe_service import (
    get_user_recipes,
    create_recipe_service,
)



router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
)


@router.get("/", response_model=list[RecipeResponse])
def get_recipes(
    user_id: int,
    db: Session = Depends(get_db),
):
    return get_user_recipes(db, user_id)


@router.post("/", response_model=RecipeResponse)
def create_recipe(
    data: RecipeCreate,
    user_id: int,
    db: Session = Depends(get_db),
):
    return create_recipe_service(db, user_id, data)
